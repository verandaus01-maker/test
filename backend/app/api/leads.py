"""
Leads API Endpoints
Lead management, filtering, and operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.lead import Lead, LeadStatus, LeadSource
from app.models.lead_activity import LeadActivity, ActivityType
from app.filters.advanced_filters import AdvancedFilter
from app.scoring import LeadScorer
from app.enrichers.email_finder import EmailFinder
from app.webhooks import notify_lead_enriched

router = APIRouter()


# Pydantic models
class LeadCreate(BaseModel):
    company_name: str
    company_website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    source: LeadSource = LeadSource.MANUAL


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[LeadStatus] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LeadResponse(BaseModel):
    id: int
    company_name: str
    company_website: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    industry: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    lead_score: Optional[float]
    status: LeadStatus
    source: LeadSource
    created_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    total: int
    leads: List[LeadResponse]
    page: int
    per_page: int


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=1000),
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    min_score: Optional[float] = None,
    search: Optional[str] = None,
    industry: Optional[str] = None,
    country: Optional[str] = None,
    has_email: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List leads with filtering and pagination"""
    # Base query
    query = select(Lead).where(Lead.user_id == current_user.id)

    # Apply filters
    if status:
        query = query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
    if min_score:
        query = query.where(Lead.lead_score >= min_score)
    if industry:
        query = query.where(Lead.industry == industry)
    if country:
        query = query.where(Lead.country == country)
    if has_email is not None:
        if has_email:
            query = query.where(or_(Lead.email.isnot(None), Lead.contact_email.isnot(None)))
    if search:
        search_filter = or_(
            Lead.company_name.ilike(f"%{search}%"),
            Lead.company_domain.ilike(f"%{search}%"),
            Lead.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()

    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(Lead.created_at.desc())

    # Execute query
    result = await db.execute(query)
    leads = result.scalars().all()

    return {"total": total, "leads": leads, "page": page, "per_page": per_page}


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead manually"""
    new_lead = Lead(
        user_id=current_user.id,
        company_name=lead_data.company_name,
        company_website=lead_data.company_website,
        email=lead_data.email,
        phone=lead_data.phone,
        industry=lead_data.industry,
        city=lead_data.city,
        state=lead_data.state,
        country=lead_data.country,
        source=lead_data.source,
        status=LeadStatus.NEW
    )
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead


@router.get("/{lead_id}")
async def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed lead information"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == current_user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update lead information"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == current_user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    lead.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a lead"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == current_user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()


@router.post("/{lead_id}/enrich", response_model=LeadResponse)
async def enrich_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enrich lead data"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == current_user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.is_enriched = True
    lead.enriched_at = datetime.utcnow()
    await db.commit()
    await db.refresh(lead)
    return lead


@router.post("/{lead_id}/score")
async def score_lead(
    lead_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Calculate AI lead score"""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.user_id == current_user.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    scorer = LeadScorer()
    lead_data = {
        "id": lead.id,
        "company_name": lead.company_name,
        "employee_count": lead.employee_count,
        "annual_revenue": lead.annual_revenue,
        "email": lead.email,
        "email_verified": lead.email_verified,
        "phone": lead.phone,
        "is_hiring": lead.is_hiring,
        "job_openings_count": lead.job_openings_count,
        "recent_funding": lead.recent_funding,
        "technologies": lead.technologies,
        "is_enriched": lead.is_enriched,
    }
    score_result = scorer.calculate_lead_score(lead_data)
    lead.lead_score = score_result['lead_score']
    lead.fit_score = score_result['fit_score']
    lead.intent_score = score_result['intent_score']
    lead.scoring_factors = score_result['factors']
    await db.commit()
    return score_result


@router.post("/bulk-update")
async def bulk_update_leads(
    lead_ids: List[int],
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update multiple leads"""
    result = await db.execute(
        select(Lead).where(Lead.id.in_(lead_ids), Lead.user_id == current_user.id)
    )
    leads = result.scalars().all()
    for lead in leads:
        for field, value in updates.items():
            if hasattr(lead, field):
                setattr(lead, field, value)
    await db.commit()
    return {"success": True, "updated": len(leads)}
