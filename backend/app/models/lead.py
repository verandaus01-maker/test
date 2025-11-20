"""
Lead Model
Central model for storing scraped lead data
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    """Lead status enumeration"""
    NEW = "new"
    ENRICHED = "enriched"
    VERIFIED = "verified"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


class LeadSource(str, enum.Enum):
    """Lead source enumeration"""
    LINKEDIN = "linkedin"
    GOOGLE_MAPS = "google_maps"
    COMPANY_WEBSITE = "company_website"
    DIRECTORY = "directory"
    SOCIAL_MEDIA = "social_media"
    MANUAL = "manual"
    API = "api"


class Lead(Base):
    """Lead model storing comprehensive business information"""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scraping_job_id = Column(Integer, ForeignKey("scraping_jobs.id"), nullable=True, index=True)

    # Company Information
    company_name = Column(String, nullable=False, index=True)
    company_website = Column(String, nullable=True)
    company_domain = Column(String, nullable=True, index=True)
    company_description = Column(Text, nullable=True)
    company_tagline = Column(String, nullable=True)

    # Industry & Classification
    industry = Column(String, nullable=True, index=True)
    sub_industry = Column(String, nullable=True)
    business_type = Column(String, nullable=True)  # B2B, B2C, B2B2C
    keywords = Column(JSON, nullable=True)  # List of relevant keywords

    # Company Size & Demographics
    employee_count = Column(Integer, nullable=True, index=True)
    employee_range = Column(String, nullable=True)  # "1-10", "11-50", etc.
    annual_revenue = Column(Float, nullable=True)
    revenue_range = Column(String, nullable=True)
    founded_year = Column(Integer, nullable=True)

    # Location Information
    country = Column(String, nullable=True, index=True)
    state = Column(String, nullable=True, index=True)
    city = Column(String, nullable=True, index=True)
    address = Column(Text, nullable=True)
    postal_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Contact Information
    phone = Column(String, nullable=True)
    phone_verified = Column(Boolean, default=False)
    email = Column(String, nullable=True, index=True)
    email_verified = Column(Boolean, default=False)
    email_pattern = Column(String, nullable=True)  # e.g., {first}.{last}@company.com

    # Decision Makers
    contact_name = Column(String, nullable=True)
    contact_title = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_linkedin = Column(String, nullable=True)
    additional_contacts = Column(JSON, nullable=True)  # List of other decision makers

    # Social Media
    linkedin_url = Column(String, nullable=True)
    linkedin_followers = Column(Integer, nullable=True)
    facebook_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)

    # Technology Stack
    technologies = Column(JSON, nullable=True)  # List of technologies used
    tech_categories = Column(JSON, nullable=True)  # Analytics, CRM, etc.
    cms_platform = Column(String, nullable=True)
    ecommerce_platform = Column(String, nullable=True)

    # Growth Signals
    is_hiring = Column(Boolean, default=False)
    job_openings_count = Column(Integer, default=0)
    recent_funding = Column(Boolean, default=False)
    funding_amount = Column(Float, nullable=True)
    funding_round = Column(String, nullable=True)
    recent_news = Column(JSON, nullable=True)  # List of recent news articles

    # AI Lead Scoring
    lead_score = Column(Float, nullable=True, index=True)  # 0-100
    fit_score = Column(Float, nullable=True)  # How well they fit target criteria
    intent_score = Column(Float, nullable=True)  # Likelihood of interest
    scoring_factors = Column(JSON, nullable=True)  # Breakdown of scoring

    # Status & Metadata
    status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    source = Column(SQLEnum(LeadSource), nullable=False, index=True)
    source_url = Column(String, nullable=True)

    is_enriched = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, ForeignKey("leads.id"), nullable=True)

    # Tags and Notes
    tags = Column(JSON, nullable=True)  # Custom tags
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, nullable=True)  # User-defined fields

    # GDPR/Compliance
    consent_obtained = Column(Boolean, default=False)
    data_processing_consent = Column(Boolean, default=False)
    opt_out = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enriched_at = Column(DateTime, nullable=True)
    last_contacted = Column(DateTime, nullable=True)

    # Raw Data (for reference)
    raw_data = Column(JSON, nullable=True)  # Original scraped data

    # Relationships
    user = relationship("User", back_populates="leads")
    scraping_job = relationship("ScrapingJob", back_populates="leads")
    activities = relationship("LeadActivity", back_populates="lead", cascade="all, delete-orphan")
    exports = relationship("ExportLead", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead(id={self.id}, company={self.company_name}, score={self.lead_score})>"

    @property
    def full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.address, self.city, self.state, self.postal_code, self.country]
        return ", ".join([p for p in parts if p])

    @property
    def is_high_quality(self) -> bool:
        """Check if lead is high quality based on score"""
        return self.lead_score and self.lead_score >= 70

    @property
    def has_email(self) -> bool:
        """Check if lead has email"""
        return bool(self.email or self.contact_email)

    @property
    def has_phone(self) -> bool:
        """Check if lead has phone"""
        return bool(self.phone or self.contact_phone)
