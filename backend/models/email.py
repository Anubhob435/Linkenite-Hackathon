"""
Email model definitions.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from backend.core.database import Base


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class PriorityLevel(str, Enum):
    URGENT = "urgent"
    NOT_URGENT = "not_urgent"


class EmailStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    RESOLVED = "resolved"
    FAILED = "failed"


class Email(Base):
    """Email model representing a support email."""
    
    __tablename__ = "emails"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_email = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    received_at = Column(DateTime, nullable=False)
    
    sentiment = Column(SQLEnum(SentimentType), nullable=False)
    priority = Column(SQLEnum(PriorityLevel), nullable=False)
    status = Column(SQLEnum(EmailStatus), nullable=False, default=EmailStatus.PENDING)
    
    extracted_info = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to response
    response = relationship("Response", back_populates="email", uselist=False)