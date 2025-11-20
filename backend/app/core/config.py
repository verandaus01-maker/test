"""
Application Configuration
Centralized configuration management using Pydantic settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, AnyHttpUrl


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Lead Scraping System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # API Keys for Data Enrichment
    OPENAI_API_KEY: Optional[str] = None
    HUNTER_IO_API_KEY: Optional[str] = None
    CLEARBIT_API_KEY: Optional[str] = None
    FULLCONTACT_API_KEY: Optional[str] = None
    PEOPLEDATALABS_API_KEY: Optional[str] = None
    BUILT_WITH_API_KEY: Optional[str] = None
    PIPL_API_KEY: Optional[str] = None

    # Scraping Configuration
    MAX_CONCURRENT_SCRAPERS: int = 5
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Proxy Configuration
    PROXY_ENABLED: bool = False
    PROXY_ROTATION_URL: Optional[str] = None
    PROXY_USERNAME: Optional[str] = None
    PROXY_PASSWORD: Optional[str] = None

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 5000

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@yourcompany.com"
    SMTP_FROM_NAME: str = "Lead Scraper System"

    # LinkedIn
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None

    # Google Maps
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # CRM Integration
    HUBSPOT_API_KEY: Optional[str] = None
    SALESFORCE_CLIENT_ID: Optional[str] = None
    SALESFORCE_CLIENT_SECRET: Optional[str] = None
    SALESFORCE_USERNAME: Optional[str] = None
    SALESFORCE_PASSWORD: Optional[str] = None
    SALESFORCE_SECURITY_TOKEN: Optional[str] = None
    PIPEDRIVE_API_KEY: Optional[str] = None

    # Webhooks
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 10

    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 3600  # 1 hour

    # Data Retention
    DATA_RETENTION_DAYS: int = 90
    LOG_RETENTION_DAYS: int = 30

    # Feature Flags
    FEATURE_AI_SCORING: bool = True
    FEATURE_AUTO_ENRICHMENT: bool = True
    FEATURE_TECH_DETECTION: bool = True
    FEATURE_SOCIAL_SCRAPING: bool = True
    FEATURE_EMAIL_VERIFICATION: bool = True
    FEATURE_PHONE_VALIDATION: bool = True

    # Compliance
    GDPR_ENABLED: bool = True
    CCPA_ENABLED: bool = True
    DATA_PROCESSING_CONSENT_REQUIRED: bool = True

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    MIXPANEL_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
