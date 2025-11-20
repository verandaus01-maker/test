"""
Scraping Job Model
Manages scraping campaigns and configurations
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(str, enum.Enum):
    """Job priority enumeration"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ScrapingJob(Base):
    """Scraping job model for managing lead generation campaigns"""

    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Job Configuration
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.NORMAL, nullable=False)

    # Data Sources
    sources = Column(JSON, nullable=False)  # ["linkedin", "google_maps", etc.]

    # Filter Configuration
    filters = Column(JSON, nullable=False)  # Complex filter criteria
    """
    Example filters structure:
    {
        "industry": ["Technology", "Software"],
        "location": {
            "country": "United States",
            "states": ["California", "New York"],
            "cities": ["San Francisco", "New York City"]
        },
        "company_size": {
            "min": 10,
            "max": 500
        },
        "technologies": ["React", "Python"],
        "growth_signals": {
            "is_hiring": true,
            "has_funding": true
        },
        "keywords": ["SaaS", "B2B"],
        "exclude_domains": ["competitor.com"]
    }
    """

    # Enrichment Settings
    enable_enrichment = Column(Boolean, default=True)
    enrichment_providers = Column(JSON, nullable=True)  # Which enrichment APIs to use
    verify_emails = Column(Boolean, default=True)
    verify_phones = Column(Boolean, default=True)
    find_decision_makers = Column(Boolean, default=True)
    detect_technologies = Column(Boolean, default=True)

    # Scoring Settings
    enable_ai_scoring = Column(Boolean, default=True)
    scoring_criteria = Column(JSON, nullable=True)  # Custom scoring weights

    # Limits & Constraints
    target_lead_count = Column(Integer, nullable=True)  # Max leads to scrape
    max_leads_per_source = Column(Integer, nullable=True)
    rate_limit_delay = Column(Integer, default=2)  # Seconds between requests

    # Schedule Configuration
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String, nullable=True)  # Cron expression
    schedule_timezone = Column(String, default="UTC")
    next_run_at = Column(DateTime, nullable=True)

    # Status & Progress
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    progress_percentage = Column(Integer, default=0)
    leads_found = Column(Integer, default=0)
    leads_enriched = Column(Integer, default=0)
    leads_verified = Column(Integer, default=0)
    leads_scored = Column(Integer, default=0)

    # Error Tracking
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    error_log = Column(JSON, nullable=True)  # List of errors

    # Celery Task Information
    celery_task_id = Column(String, nullable=True, unique=True)

    # Results & Statistics
    total_sources_scraped = Column(Integer, default=0)
    total_pages_scraped = Column(Integer, default=0)
    total_requests_made = Column(Integer, default=0)
    average_lead_score = Column(Integer, nullable=True)
    duplicates_found = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="scraping_jobs")
    leads = relationship("Lead", back_populates="scraping_job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ScrapingJob(id={self.id}, name={self.name}, status={self.status})>"

    @property
    def is_running(self) -> bool:
        """Check if job is currently running"""
        return self.status == JobStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """Check if job is completed"""
        return self.status == JobStatus.COMPLETED

    @property
    def duration_seconds(self) -> int:
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        elif self.started_at:
            return int((datetime.utcnow() - self.started_at).total_seconds())
        return 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate based on errors vs requests"""
        if self.total_requests_made == 0:
            return 0.0
        return ((self.total_requests_made - self.error_count) / self.total_requests_made) * 100
