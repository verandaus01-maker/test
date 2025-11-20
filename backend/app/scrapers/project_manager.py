"""
Scraping Project Management System
Advanced project and campaign management for lead scraping operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ProjectStatus(str, Enum):
    """Project status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectTemplate:
    """
    Reusable scraping project template

    Templates include pre-configured settings for common scraping scenarios
    """

    def __init__(
        self,
        name: str,
        description: str,
        business_type: str,
        sources: List[str],
        filters: Dict[str, Any],
        enrichment_config: Dict[str, Any],
        scoring_config: Dict[str, Any],
        estimated_leads: int,
        estimated_duration_hours: int,
    ):
        self.name = name
        self.description = description
        self.business_type = business_type
        self.sources = sources
        self.filters = filters
        self.enrichment_config = enrichment_config
        self.scoring_config = scoring_config
        self.estimated_leads = estimated_leads
        self.estimated_duration_hours = estimated_duration_hours

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'business_type': self.business_type,
            'sources': self.sources,
            'filters': self.filters,
            'enrichment_config': self.enrichment_config,
            'scoring_config': self.scoring_config,
            'estimated_leads': self.estimated_leads,
            'estimated_duration_hours': self.estimated_duration_hours,
        }


# Pre-built project templates
TEMPLATES = {
    'tech_startups_sf': ProjectTemplate(
        name="SF Bay Area Tech Startups",
        description="Scrape technology startups in San Francisco Bay Area",
        business_type="technology",
        sources=['linkedin', 'crunchbase', 'angellist'],
        filters={
            'industry': ['Technology', 'Software', 'SaaS'],
            'location': {
                'city': 'San Francisco',
                'state': 'California',
                'radius_miles': 50
            },
            'company_size': {'min': 10, 'max': 250},
            'funding': {'raised': True},
            'growth_signals': {
                'is_hiring': True,
                'min_job_openings': 3
            }
        },
        enrichment_config={
            'email_finding': True,
            'tech_detection': True,
            'funding_data': True,
            'contact_extraction': True
        },
        scoring_config={
            'enable_ai_scoring': True,
            'weights': {
                'funding': 25,
                'growth_signals': 20,
                'tech_stack': 20,
                'team_size': 15,
                'contact_quality': 20
            }
        },
        estimated_leads=1500,
        estimated_duration_hours=4,
    ),

    'healthcare_practices': ProjectTemplate(
        name="Healthcare Practices",
        description="Medical practices and clinics nationwide",
        business_type="healthcare",
        sources=['google_maps', 'healthgrades', 'zocdoc'],
        filters={
            'business_type': 'Healthcare',
            'specialties': ['Primary Care', 'Dentistry', 'Dermatology'],
            'has_website': True,
            'min_rating': 4.0
        },
        enrichment_config={
            'email_finding': True,
            'phone_validation': True,
            'address_verification': True
        },
        scoring_config={
            'enable_ai_scoring': True,
            'weights': {
                'contact_completeness': 30,
                'online_presence': 25,
                'ratings': 20,
                'location_quality': 25
            }
        },
        estimated_leads=5000,
        estimated_duration_hours=6,
    ),

    'ecommerce_stores': ProjectTemplate(
        name="E-commerce Stores",
        description="Online retail and e-commerce businesses",
        business_type="ecommerce",
        sources=['shopify_directory', 'google_maps', 'company_website'],
        filters={
            'has_ecommerce': True,
            'technologies': ['Shopify', 'WooCommerce', 'Magento'],
            'min_monthly_traffic': 10000
        },
        enrichment_config={
            'email_finding': True,
            'tech_detection': True,
            'social_media_extraction': True
        },
        scoring_config={
            'enable_ai_scoring': True,
            'weights': {
                'platform_type': 25,
                'traffic_volume': 25,
                'social_presence': 20,
                'contact_quality': 30
            }
        },
        estimated_leads=3000,
        estimated_duration_hours=5,
    ),

    'professional_services': ProjectTemplate(
        name="Professional Services",
        description="Consulting, marketing, and professional service firms",
        business_type="professional_services",
        sources=['linkedin', 'clutch', 'google_maps'],
        filters={
            'services': ['Consulting', 'Marketing', 'Design', 'Development'],
            'company_size': {'min': 5, 'max': 100},
            'has_portfolio': True
        },
        enrichment_config={
            'email_finding': True,
            'decision_maker_extraction': True,
            'client_extraction': True
        },
        scoring_config={
            'enable_ai_scoring': True,
            'weights': {
                'client_portfolio': 30,
                'team_expertise': 25,
                'online_presence': 20,
                'contact_quality': 25
            }
        },
        estimated_leads=2000,
        estimated_duration_hours=3,
    ),

    'real_estate_agencies': ProjectTemplate(
        name="Real Estate Agencies",
        description="Real estate brokerages and agencies",
        business_type="real_estate",
        sources=['zillow', 'realtor.com', 'google_maps'],
        filters={
            'business_type': 'Real Estate',
            'has_active_listings': True,
            'min_agents': 3
        },
        enrichment_config={
            'email_finding': True,
            'phone_validation': True,
            'agent_extraction': True
        },
        scoring_config={
            'enable_ai_scoring': True,
            'weights': {
                'active_listings': 30,
                'agent_count': 20,
                'service_areas': 20,
                'contact_quality': 30
            }
        },
        estimated_leads=4000,
        estimated_duration_hours=5,
    ),
}


class ScrapingProject:
    """
    Advanced scraping project with complete lifecycle management

    Features:
    - Project planning and estimation
    - Progress tracking
    - Resource allocation
    - Quality metrics
    - Reporting
    """

    def __init__(
        self,
        project_id: str,
        name: str,
        description: str,
        business_type: str,
        config: Dict[str, Any],
        owner_id: int,
    ):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.business_type = business_type
        self.config = config
        self.owner_id = owner_id

        self.status = ProjectStatus.DRAFT
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        # Progress tracking
        self.total_targets = 0
        self.targets_processed = 0
        self.leads_found = 0
        self.leads_enriched = 0
        self.leads_verified = 0
        self.errors = 0

        # Quality metrics
        self.avg_lead_score = 0.0
        self.data_completeness = 0.0
        self.verification_rate = 0.0

        # Jobs/tasks
        self.jobs: List[Dict[str, Any]] = []

    def add_job(self, job_config: Dict[str, Any]) -> str:
        """
        Add a scraping job to the project

        Args:
            job_config: Job configuration

        Returns:
            Job ID
        """
        job_id = f"{self.project_id}_job_{len(self.jobs) + 1}"

        job = {
            'job_id': job_id,
            'config': job_config,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'results': None
        }

        self.jobs.append(job)
        logger.info(f"Added job {job_id} to project {self.project_id}")

        return job_id

    def start(self):
        """Start the project"""
        if self.status != ProjectStatus.DRAFT:
            raise ValueError(f"Cannot start project in {self.status} status")

        self.status = ProjectStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        logger.info(f"Project {self.project_id} started")

    def pause(self):
        """Pause the project"""
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError(f"Cannot pause project in {self.status} status")

        self.status = ProjectStatus.PAUSED
        self.updated_at = datetime.utcnow()

        logger.info(f"Project {self.project_id} paused")

    def resume(self):
        """Resume paused project"""
        if self.status != ProjectStatus.PAUSED:
            raise ValueError(f"Cannot resume project in {self.status} status")

        self.status = ProjectStatus.ACTIVE
        self.updated_at = datetime.utcnow()

        logger.info(f"Project {self.project_id} resumed")

    def complete(self):
        """Mark project as completed"""
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        logger.info(f"Project {self.project_id} completed")

    def update_progress(
        self,
        targets_processed: int = 0,
        leads_found: int = 0,
        leads_enriched: int = 0,
        leads_verified: int = 0,
        errors: int = 0
    ):
        """
        Update project progress

        Args:
            targets_processed: Number of targets processed
            leads_found: Number of leads found
            leads_enriched: Number of leads enriched
            leads_verified: Number of leads verified
            errors: Number of errors
        """
        self.targets_processed += targets_processed
        self.leads_found += leads_found
        self.leads_enriched += leads_enriched
        self.leads_verified += leads_verified
        self.errors += errors
        self.updated_at = datetime.utcnow()

    def calculate_metrics(self):
        """Calculate project metrics"""
        if self.leads_found > 0:
            self.data_completeness = (self.leads_enriched / self.leads_found) * 100
            self.verification_rate = (self.leads_verified / self.leads_found) * 100

    def get_progress_percentage(self) -> float:
        """Get project progress percentage"""
        if self.total_targets == 0:
            return 0.0

        return (self.targets_processed / self.total_targets) * 100

    def get_estimated_completion_time(self) -> Optional[datetime]:
        """Estimate project completion time"""
        if not self.started_at or self.total_targets == 0 or self.targets_processed == 0:
            return None

        elapsed = datetime.utcnow() - self.started_at
        rate = self.targets_processed / elapsed.total_seconds()  # targets per second

        remaining = self.total_targets - self.targets_processed
        estimated_seconds = remaining / rate if rate > 0 else 0

        return datetime.utcnow() + timedelta(seconds=estimated_seconds)

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive project report

        Returns:
            Project report dictionary
        """
        duration = None
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            duration = (end_time - self.started_at).total_seconds()

        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'business_type': self.business_type,
            'status': self.status.value,

            'timeline': {
                'created_at': self.created_at.isoformat(),
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'duration_seconds': duration,
                'estimated_completion': self.get_estimated_completion_time().isoformat() if self.get_estimated_completion_time() else None,
            },

            'progress': {
                'percentage': round(self.get_progress_percentage(), 2),
                'total_targets': self.total_targets,
                'targets_processed': self.targets_processed,
                'leads_found': self.leads_found,
                'leads_enriched': self.leads_enriched,
                'leads_verified': self.leads_verified,
                'errors': self.errors,
            },

            'quality_metrics': {
                'avg_lead_score': round(self.avg_lead_score, 2),
                'data_completeness': round(self.data_completeness, 2),
                'verification_rate': round(self.verification_rate, 2),
                'error_rate': round((self.errors / self.targets_processed * 100) if self.targets_processed > 0 else 0, 2),
            },

            'jobs': {
                'total': len(self.jobs),
                'pending': sum(1 for j in self.jobs if j['status'] == 'pending'),
                'running': sum(1 for j in self.jobs if j['status'] == 'running'),
                'completed': sum(1 for j in self.jobs if j['status'] == 'completed'),
                'failed': sum(1 for j in self.jobs if j['status'] == 'failed'),
            },

            'performance': {
                'leads_per_hour': round((self.leads_found / (duration / 3600)) if duration and duration > 0 else 0, 2),
                'avg_processing_time': round((duration / self.targets_processed) if self.targets_processed > 0 and duration else 0, 4),
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'business_type': self.business_type,
            'status': self.status.value,
            'config': self.config,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'jobs_count': len(self.jobs),
            'leads_found': self.leads_found,
            'progress': self.get_progress_percentage(),
        }


class ProjectManager:
    """
    Manages multiple scraping projects

    Features:
    - Project creation from templates
    - Project lifecycle management
    - Resource allocation
    - Portfolio analytics
    """

    def __init__(self):
        self.projects: Dict[str, ScrapingProject] = {}
        self.templates = TEMPLATES

    def create_project_from_template(
        self,
        template_name: str,
        project_name: str,
        owner_id: int,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> ScrapingProject:
        """
        Create project from template

        Args:
            template_name: Template name
            project_name: Project name
            owner_id: Project owner ID
            custom_config: Optional custom configuration overrides

        Returns:
            Created project
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]

        # Merge template config with custom config
        config = template.to_dict()
        if custom_config:
            config.update(custom_config)

        project_id = f"proj_{int(datetime.utcnow().timestamp())}_{owner_id}"

        project = ScrapingProject(
            project_id=project_id,
            name=project_name,
            description=template.description,
            business_type=template.business_type,
            config=config,
            owner_id=owner_id,
        )

        project.total_targets = template.estimated_leads

        self.projects[project_id] = project

        logger.info(f"Created project {project_id} from template {template_name}")

        return project

    def create_custom_project(
        self,
        name: str,
        description: str,
        business_type: str,
        config: Dict[str, Any],
        owner_id: int,
    ) -> ScrapingProject:
        """Create custom project"""
        project_id = f"proj_{int(datetime.utcnow().timestamp())}_{owner_id}"

        project = ScrapingProject(
            project_id=project_id,
            name=name,
            description=description,
            business_type=business_type,
            config=config,
            owner_id=owner_id,
        )

        self.projects[project_id] = project

        logger.info(f"Created custom project {project_id}")

        return project

    def get_project(self, project_id: str) -> Optional[ScrapingProject]:
        """Get project by ID"""
        return self.projects.get(project_id)

    def list_projects(self, owner_id: Optional[int] = None, status: Optional[ProjectStatus] = None) -> List[ScrapingProject]:
        """List projects with optional filters"""
        projects = list(self.projects.values())

        if owner_id:
            projects = [p for p in projects if p.owner_id == owner_id]

        if status:
            projects = [p for p in projects if p.status == status]

        return projects

    def get_portfolio_stats(self, owner_id: int) -> Dict[str, Any]:
        """
        Get portfolio statistics for an owner

        Args:
            owner_id: Owner ID

        Returns:
            Portfolio statistics
        """
        projects = self.list_projects(owner_id=owner_id)

        total_leads = sum(p.leads_found for p in projects)
        total_verified = sum(p.leads_verified for p in projects)

        return {
            'total_projects': len(projects),
            'active_projects': sum(1 for p in projects if p.status == ProjectStatus.ACTIVE),
            'completed_projects': sum(1 for p in projects if p.status == ProjectStatus.COMPLETED),
            'total_leads': total_leads,
            'total_verified_leads': total_verified,
            'avg_lead_score': round(sum(p.avg_lead_score for p in projects) / len(projects) if projects else 0, 2),
            'total_errors': sum(p.errors for p in projects),
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        return [
            {
                'name': name,
                **template.to_dict()
            }
            for name, template in self.templates.items()
        ]


# Global project manager instance
project_manager = ProjectManager()
