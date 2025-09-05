"""
Email management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus

router = APIRouter()


@router.get("/")
async def list_emails(
    skip: int = 0,
    limit: int = 100,
    sentiment: Optional[SentimentType] = None,
    priority: Optional[PriorityLevel] = None,
    status: Optional[EmailStatus] = None,
    db: Session = Depends(get_db)
):
    """List all emails with optional filtering."""
    query = db.query(Email)
    
    if sentiment:
        query = query.filter(Email.sentiment == sentiment)
    
    if priority:
        query = query.filter(Email.priority == priority)
    
    if status:
        query = query.filter(Email.status == status)
    
    emails = query.offset(skip).limit(limit).all()
    return emails


@router.get("/{email_id}")
async def get_email(email_id: str, db: Session = Depends(get_db)):
    """Get specific email by ID."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.put("/{email_id}/status")
async def update_email_status(email_id: str, status: EmailStatus, db: Session = Depends(get_db)):
    """Update email status."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    email.status = status
    db.commit()
    db.refresh(email)
    return email