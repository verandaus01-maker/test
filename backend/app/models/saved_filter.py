"""
Saved Filter Model
Allows users to save and reuse filter configurations
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class SavedFilter(Base):
    """Saved filter configurations for quick access"""

    __tablename__ = "saved_filters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Filter Details
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    filter_config = Column(JSON, nullable=False)

    # Sharing
    is_public = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)

    # Usage Statistics
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_filters")

    def __repr__(self):
        return f"<SavedFilter(id={self.id}, name={self.name})>"
