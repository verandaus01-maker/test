"""
Lead Activity Model
Tracks all activities and interactions with leads
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ActivityType(str, enum.Enum):
    """Activity type enumeration"""
    CREATED = "created"
    ENRICHED = "enriched"
    VERIFIED = "verified"
    SCORED = "scored"
    CONTACTED = "contacted"
    EMAIL_SENT = "email_sent"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    CALLED = "called"
    MEETING_SCHEDULED = "meeting_scheduled"
    NOTE_ADDED = "note_added"
    STATUS_CHANGED = "status_changed"
    EXPORTED = "exported"
    CRM_SYNCED = "crm_synced"


class LeadActivity(Base):
    """Lead activity tracking for audit and analytics"""

    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Activity Details
    activity_type = Column(SQLEnum(ActivityType), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Metadata
    metadata = Column(Text, nullable=True)  # JSON string with additional data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    lead = relationship("Lead", back_populates="activities")

    def __repr__(self):
        return f"<LeadActivity(id={self.id}, type={self.activity_type}, lead_id={self.lead_id})>"
