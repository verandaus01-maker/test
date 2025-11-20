"""
Scraping API Endpoints
Advanced scraping job management and execution with testing framework
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.scrapers.project_manager import project_manager, ProjectStatus
from app.scrapers.business_strategies import strategy_manager, BusinessType
from app.scrapers.testing_framework import quality_validator, scraper_benchmark

router = APIRouter()


# Pydantic models
class ProjectCreate(BaseModel):
    name: str
    description: str
    business_type: str
    template_name: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    description: str
    business_type: str
    status: str
    created_at: datetime
    leads_found: int
    progress: float


@router.get("/templates")
async def list_scraping_templates(current_user: User = Depends(get_current_user)):
    """
    List available scraping project templates

    Returns pre-configured templates for different business types
    """
    templates = project_manager.list_templates()
    return {
        "templates": templates,
        "total": len(templates)
    }


@router.get("/business-types")
async def list_business_types(current_user: User = Depends(get_current_user)):
    """List available business types with strategies"""
    strategies = strategy_manager.list_available_strategies()
    return {
        "business_types": strategies,
        "total": len(strategies)
    }


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_scraping_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new scraping project

    Can be created from template or custom configuration
    """
    try:
        if project_data.template_name:
            # Create from template
            project = project_manager.create_project_from_template(
                template_name=project_data.template_name,
                project_name=project_data.name,
                owner_id=current_user.id,
                custom_config=project_data.custom_config
            )
        else:
            # Create custom project
            if not project_data.custom_config:
                raise ValueError("custom_config required for non-template projects")

            project = project_manager.create_custom_project(
                name=project_data.name,
                description=project_data.description,
                business_type=project_data.business_type,
                config=project_data.custom_config,
                owner_id=current_user.id,
            )

        return project.to_dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects")
async def list_projects(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List all scraping projects for current user"""
    status_enum = None
    if status_filter:
        try:
            status_enum = ProjectStatus(status_filter)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    projects = project_manager.list_projects(
        owner_id=current_user.id,
        status=status_enum
    )

    return {
        "projects": [p.to_dict() for p in projects],
        "total": len(projects)
    }


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get detailed project information"""
    project = project_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return project.generate_report()


@router.post("/projects/{project_id}/start")
async def start_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    """Start a scraping project"""
    project = project_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        project.start()
        return {"message": "Project started", "project_id": project_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/pause")
async def pause_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    """Pause a running project"""
    project = project_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        project.pause()
        return {"message": "Project paused", "project_id": project_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/projects/{project_id}/resume")
async def resume_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
):
    """Resume a paused project"""
    project = project_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        project.resume()
        return {"message": "Project resumed", "project_id": project_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/portfolio/stats")
async def get_portfolio_stats(current_user: User = Depends(get_current_user)):
    """Get portfolio statistics for current user"""
    stats = project_manager.get_portfolio_stats(current_user.id)
    return stats


@router.post("/validate/leads")
async def validate_leads(
    leads: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
):
    """
    Validate lead data quality

    Performs comprehensive quality checks on lead data
    """
    validation_results = quality_validator.batch_validate(leads)
    return validation_results


@router.post("/detect/duplicates")
async def detect_duplicates(
    leads: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user),
):
    """Detect duplicate leads in a dataset"""
    duplicates = quality_validator.detect_duplicates(leads)
    return {
        "total_leads": len(leads),
        "duplicates_found": len(duplicates),
        "duplicate_rate": round((len(duplicates) / len(leads) * 100) if leads else 0, 2),
        "duplicates": duplicates[:20]  # Return first 20
    }


@router.get("/strategy/{business_type}")
async def get_business_strategy(
    business_type: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get scraping strategy for a business type

    Returns extraction schema, priority fields, and recommended sources
    """
    strategy = strategy_manager.get_strategy(business_type)

    return {
        "business_type": business_type,
        "extraction_schema": strategy.schema,
        "priority_fields": strategy.priority_fields,
        "quality_indicators": strategy.quality_indicators,
        "recommended_sources": strategy.recommended_sources,
    }


@router.post("/auto-detect/business-type")
async def auto_detect_business_type(
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
):
    """
    Automatically detect business type from data

    Uses AI to classify business based on available information
    """
    detected_type = strategy_manager.auto_detect_business_type(data)

    return {
        "detected_type": detected_type.value if detected_type else None,
        "confidence": "high" if detected_type else "low",
        "input_data": data
    }


@router.get("/benchmarks")
async def get_benchmarks(
    scraper_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Get scraper performance benchmarks"""
    if scraper_name:
        benchmarks = [b for b in scraper_benchmark.benchmarks if b['scraper_name'] == scraper_name]
    else:
        benchmarks = scraper_benchmark.benchmarks

    return {
        "benchmarks": benchmarks,
        "total": len(benchmarks)
    }


@router.post("/compare/scrapers")
async def compare_scrapers(
    scraper_names: List[str],
    current_user: User = Depends(get_current_user),
):
    """Compare performance of multiple scrapers"""
    comparison = scraper_benchmark.compare_scrapers(scraper_names)
    return comparison
