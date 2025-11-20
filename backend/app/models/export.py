"""
Export Models
Manages data exports and export history
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ExportFormat(str, enum.Enum):
    """Export format enumeration"""
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"


class ExportStatus(str, enum.Enum):
    """Export status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Export(Base):
    """Export job tracking"""

    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Export Configuration
    name = Column(String, nullable=False)
    format = Column(SQLEnum(ExportFormat), nullable=False)
    filters = Column(JSON, nullable=True)  # Filters applied to export

    # File Information
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_url = Column(String, nullable=True)  # If using cloud storage

    # Export Options
    include_fields = Column(JSON, nullable=True)  # Specific fields to include
    exclude_fields = Column(JSON, nullable=True)  # Fields to exclude

    # Status
    status = Column(SQLEnum(ExportStatus), default=ExportStatus.PENDING, nullable=False)
    total_leads = Column(Integer, default=0)
    processed_leads = Column(Integer, default=0)
    error_message = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Auto-delete after expiry

    # Relationships
    user = relationship("User", back_populates="exports")
    export_leads = relationship("ExportLead", back_populates="export", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Export(id={self.id}, name={self.name}, format={self.format})>"


class ExportLead(Base):
    """Junction table linking exports to leads"""

    __tablename__ = "export_leads"

    id = Column(Integer, primary_key=True, index=True)
    export_id = Column(Integer, ForeignKey("exports.id"), nullable=False, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)

    # Relationships
    export = relationship("Export", back_populates="export_leads")
    lead = relationship("Lead", back_populates="exports")

    def __repr__(self):
        return f"<ExportLead(export_id={self.export_id}, lead_id={self.lead_id})>"
