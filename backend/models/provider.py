"""
Email provider configuration model.
"""
from typing import Dict, Any
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, Enum as SQLEnum
import uuid

from backend.core.database import Base


class ProviderType(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    IMAP = "imap"


class EmailProvider(Base):
    """Email provider configuration."""
    
    __tablename__ = "email_providers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_type = Column(SQLEnum(ProviderType), nullable=False)
    configuration = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)