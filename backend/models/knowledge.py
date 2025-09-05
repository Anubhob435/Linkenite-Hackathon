"""
Knowledge base model definitions.
"""
from typing import List
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
import uuid

from backend.core.database import Base


class KnowledgeItem(Base):
    """Knowledge base item for RAG pipeline."""
    
    __tablename__ = "knowledge_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)