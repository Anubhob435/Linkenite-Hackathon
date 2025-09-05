"""
Response model definitions.
"""
from typing import Optional
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from backend.core.database import Base
from backend.models.email import Email


class ResponseStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    FAILED = "failed"


class Response(Base):
    """Response model representing an AI-generated response to an email."""
    
    __tablename__ = "responses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id = Column(String, ForeignKey("emails.id"), nullable=False)
    
    generated_content = Column(Text, nullable=False)
    edited_content = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    status = Column(SQLEnum(ResponseStatus), nullable=False, default=ResponseStatus.DRAFT)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to email
    email = relationship("Email", back_populates="response")