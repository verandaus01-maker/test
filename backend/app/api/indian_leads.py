"""
API Endpoints for Indian Lead Scraping System
Complete workflow: Scrape → Enrich → Audit → Generate Lead Magnet → Outreach
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.scrapers.india_scraper import IndianBusinessScraper, IndianCitiesDatabase
from app.enrichment.decision_maker_finder import DecisionMakerFinder, EmailVerifier
from app.enrichment.website_auditor import WebsiteAuditor, LeadMagnetGenerator

router = APIRouter(prefix="/api/v1/indian-leads", tags=["Indian Leads"])


# Request/Response Models
class ScrapingRequest(BaseModel):
    business_type: str = Field(..., example="dental clinics")
    city: str = Field(..., example="Mumbai")
    state: Optional[str] = Field(None, example="Maharashtra")
    radius_km: int = Field(default=5, example=5)
    max_results: int = Field(default=50, le=200, example=50)
    sources: List[str] = Field(default=["google_maps", "justdial"], example=["google_maps", "justdial"])


class RadiusSearchRequest(BaseModel):
    business_type: str = Field(..., example="dental clinics")
    center_address: str = Field(..., example="Bandra, Mumbai")
    radius_km: int = Field(default=5, example=5)
    max_results: int = Field(default=50, example=50)


class EnrichmentRequest(BaseModel):
    company_name: str
    website: Optional[str] = None
    find_decision_makers: bool = True
    audit_website: bool = True
    generate_lead_magnet: bool = True


class LeadEnrichmentResponse(BaseModel):
    company_name: str
    decision_makers: Dict[str, Any]
    website_audit: Optional[Dict[str, Any]] = None
    lead_magnet: Optional[Dict[str, Any]] = None
    opportunities: List[Dict[str, Any]] = []
    outreach_email_template: Optional[str] = None


# Endpoints

@router.post("/scrape", response_model=Dict[str, Any])
async def scrape_indian_businesses(
    request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scrape Indian businesses from multiple sources

    Example: Scrape dental clinics in Mumbai from Google Maps and JustDial
    """
    scraper = IndianBusinessScraper()
    results = {
        'total_found': 0,
        'sources': {},
        'leads': [],
    }

    # Get city coordinates
    city_info = IndianCitiesDatabase.get_city_info(request.city)
    if not city_info and not request.state:
        raise HTTPException(status_code=400, detail=f"City '{request.city}' not found. Please provide state as well.")

    state = request.state or city_info.get('state', 'India')

    # Scrape from each source
    if 'google_maps' in request.sources:
        google_results = await scraper.scrape_google_maps_india(
            query=request.business_type,
            city=request.city,
            state=state,
            radius_km=request.radius_km,
            max_results=request.max_results
        )
        results['sources']['google_maps'] = len(google_results)
        results['leads'].extend(google_results)

    if 'justdial' in request.sources:
        justdial_results = await scraper.scrape_justdial(
            category=request.business_type,
            city=request.city,
            max_pages=3
        )
        results['sources']['justdial'] = len(justdial_results)
        results['leads'].extend(justdial_results)

    if 'indiamart' in request.sources:
        indiamart_results = await scraper.scrape_indiamart(
            product_category=request.business_type,
            city=request.city,
            max_results=request.max_results
        )
        results['sources']['indiamart'] = len(indiamart_results)
        results['leads'].extend(indiamart_results)

    results['total_found'] = len(results['leads'])

    # TODO: Save to database
    # background_tasks.add_task(save_leads_to_db, results['leads'], current_user.id, db)

    return results


@router.post("/scrape/radius", response_model=Dict[str, Any])
async def scrape_by_radius(
    request: RadiusSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find businesses within specific radius of an address

    Example: Find all dental clinics within 5km of "Bandra, Mumbai"
    """
    scraper = IndianBusinessScraper()

    # Parse address to get coordinates (simplified - in production use geocoding API)
    # For now, extract city from address
    city_match = None
    for city in IndianCitiesDatabase.CITIES.keys():
        if city.lower() in request.center_address.lower():
            city_match = city
            break

    if not city_match:
        raise HTTPException(status_code=400, detail="Could not identify city from address")

    city_info = IndianCitiesDatabase.get_city_info(city_match)
    if not city_info:
        raise HTTPException(status_code=400, detail=f"City information not found")

    # Search in radius
    results = await scraper.find_business_in_radius(
        business_type=request.business_type,
        center_lat=city_info['lat'],
        center_lng=city_info['lng'],
        radius_km=request.radius_km,
        city=city_match,
        state=city_info['state'],
        max_results=request.max_results
    )

    return {
        'center': request.center_address,
        'radius_km': request.radius_km,
        'total_found': len(results),
        'leads': results,
    }


@router.post("/enrich", response_model=LeadEnrichmentResponse)
async def enrich_lead(
    request: EnrichmentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete lead enrichment:
    1. Find decision makers (CEO, Marketing Manager)
    2. Audit their website
    3. Generate lead magnet report
    4. Create personalized outreach email

    This gives you EVERYTHING needed to pitch!
    """
    result = {
        'company_name': request.company_name,
        'decision_makers': {},
        'website_audit': None,
        'lead_magnet': None,
        'opportunities': [],
        'outreach_email_template': None,
    }

    # Find decision makers
    if request.find_decision_makers:
        dm_finder = DecisionMakerFinder()
        decision_makers = await dm_finder.find_decision_makers(
            company_name=request.company_name,
            website=request.website
        )
        result['decision_makers'] = decision_makers

    # Audit website
    if request.audit_website and request.website:
        auditor = WebsiteAuditor()
        audit_result = await auditor.audit_website(request.website)
        result['website_audit'] = audit_result
        result['opportunities'] = audit_result.get('opportunities', [])

        # Generate lead magnet
        if request.generate_lead_magnet:
            lead_magnet_gen = LeadMagnetGenerator()
            lead_magnet = lead_magnet_gen.generate_pdf_report(audit_result)
            result['lead_magnet'] = lead_magnet

            # Generate outreach email
            decision_maker_name = None
            if result['decision_makers'].get('ceo'):
                decision_maker_name = result['decision_makers']['ceo'].get('name')
            elif result['decision_makers'].get('marketing_manager'):
                decision_maker_name = result['decision_makers']['marketing_manager'].get('name')

            outreach_email = lead_magnet_gen.generate_email_template(
                company_name=request.company_name,
                audit_data=audit_result,
                decision_maker=decision_maker_name
            )
            result['outreach_email_template'] = outreach_email

    return result


@router.post("/bulk-scrape-and-enrich")
async def bulk_scrape_and_enrich(
    scraping_request: ScrapingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete workflow:
    1. Scrape businesses from Indian sources
    2. Enrich each one (find decision makers, audit website)
    3. Generate lead magnets for all
    4. Return ready-to-use sales pipeline

    Example: "Find 10 dental clinics in Mumbai, audit their websites,
    find CEO contacts, and give me personalized pitch emails for each"
    """
    # Step 1: Scrape
    scraper = IndianBusinessScraper()
    city_info = IndianCitiesDatabase.get_city_info(scraping_request.city)
    state = scraping_request.state or city_info.get('state', 'India')

    all_leads = []

    if 'google_maps' in scraping_request.sources:
        google_results = await scraper.scrape_google_maps_india(
            query=scraping_request.business_type,
            city=scraping_request.city,
            state=state,
            radius_km=scraping_request.radius_km,
            max_results=scraping_request.max_results
        )
        all_leads.extend(google_results)

    if 'justdial' in scraping_request.sources:
        justdial_results = await scraper.scrape_justdial(
            category=scraping_request.business_type,
            city=scraping_request.city,
            max_pages=2
        )
        all_leads.extend(justdial_results)

    # Step 2: Enrich each lead
    enriched_leads = []
    dm_finder = DecisionMakerFinder()
    auditor = WebsiteAuditor()
    lead_magnet_gen = LeadMagnetGenerator()

    for lead in all_leads[:10]:  # Limit to first 10 for demo
        enriched = {
            **lead,
            'enrichment_status': 'processing',
        }

        # Find decision makers if website available
        if lead.get('website'):
            try:
                decision_makers = await dm_finder.find_decision_makers(
                    company_name=lead.get('company_name', ''),
                    website=lead.get('website')
                )
                enriched['decision_makers'] = decision_makers

                # Audit website
                audit_result = await auditor.audit_website(lead['website'])
                enriched['website_audit'] = {
                    'overall_score': audit_result.get('overall_score'),
                    'critical_issues_count': len(audit_result.get('issues', {}).get('critical', [])),
                    'opportunities': audit_result.get('opportunities', []),
                }

                # Generate outreach email
                outreach_email = lead_magnet_gen.generate_email_template(
                    company_name=lead.get('company_name', 'your business'),
                    audit_data=audit_result
                )
                enriched['outreach_email'] = outreach_email
                enriched['enrichment_status'] = 'complete'

            except Exception as e:
                enriched['enrichment_status'] = 'failed'
                enriched['enrichment_error'] = str(e)

        enriched_leads.append(enriched)

    return {
        'total_scraped': len(all_leads),
        'total_enriched': len(enriched_leads),
        'leads': enriched_leads,
        'summary': {
            'with_website': len([l for l in enriched_leads if l.get('website')]),
            'with_decision_makers': len([l for l in enriched_leads if l.get('decision_makers')]),
            'with_audit': len([l for l in enriched_leads if l.get('website_audit')]),
            'ready_for_outreach': len([l for l in enriched_leads if l.get('outreach_email')]),
        }
    }


@router.get("/cities/search")
async def search_cities(query: str):
    """Search Indian cities by name"""
    results = IndianCitiesDatabase.search_city(query)
    return {
        'query': query,
        'cities': results[:10],
    }


@router.get("/cities/{city_name}")
async def get_city_info(city_name: str):
    """Get information about a specific city"""
    info = IndianCitiesDatabase.get_city_info(city_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")

    return {
        'city': city_name,
        **info
    }


@router.get("/business-types")
async def get_supported_business_types():
    """Get list of supported business types for scraping"""
    return {
        'business_types': [
            {'value': 'dental clinics', 'label': 'Dental Clinics'},
            {'value': 'restaurants', 'label': 'Restaurants'},
            {'value': 'hotels', 'label': 'Hotels & Lodging'},
            {'value': 'gyms', 'label': 'Gyms & Fitness Centers'},
            {'value': 'salons', 'label': 'Beauty Salons & Spas'},
            {'value': 'doctors', 'label': 'Doctors & Clinics'},
            {'value': 'hospitals', 'label': 'Hospitals'},
            {'value': 'pharmacies', 'label': 'Pharmacies'},
            {'value': 'lawyers', 'label': 'Law Firms & Lawyers'},
            {'value': 'accountants', 'label': 'Accountants & Tax Consultants'},
            {'value': 'real estate', 'label': 'Real Estate Agencies'},
            {'value': 'schools', 'label': 'Schools & Coaching Centers'},
            {'value': 'colleges', 'label': 'Colleges & Universities'},
            {'value': 'car dealers', 'label': 'Car Dealerships'},
            {'value': 'electronics stores', 'label': 'Electronics & Mobile Stores'},
            {'value': 'clothing stores', 'label': 'Clothing & Fashion Stores'},
            {'value': 'jewellery stores', 'label': 'Jewellery Stores'},
            {'value': 'sweet shops', 'label': 'Sweet Shops & Bakeries'},
            {'value': 'pet shops', 'label': 'Pet Shops & Veterinary Clinics'},
            {'value': 'event planners', 'label': 'Event Management Companies'},
        ]
    }


@router.post("/verify-emails")
async def verify_email_addresses(
    emails: List[str],
    current_user: User = Depends(get_current_active_user)
):
    """Verify if email addresses are valid and deliverable"""
    verifier = EmailVerifier()
    results = await verifier.bulk_verify_emails(emails)

    return {
        'total_checked': len(emails),
        'results': results,
        'summary': {
            'valid': len([r for r in results if r['valid']]),
            'deliverable': len([r for r in results if r['deliverable']]),
            'role_based': len([r for r in results if r['role_based']]),
            'disposable': len([r for r in results if r['disposable']]),
        }
    }


# Background task helper functions
async def save_leads_to_db(leads: List[Dict], user_id: int, db: AsyncSession):
    """Save scraped leads to database"""
    # TODO: Implement database saving logic
    pass
