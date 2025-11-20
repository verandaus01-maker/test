"""
User Model
Handles user authentication and authorization
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)

    # Role-based access control
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # API Access
    api_key = Column(String, unique=True, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Usage tracking
    total_leads_scraped = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)

    # Relationships
    scraping_jobs = relationship("ScrapingJob", back_populates="user", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="user", cascade="all, delete-orphan")
    saved_filters = relationship("SavedFilter", back_populates="user", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        """Check if user is manager or admin"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
