"""
Analytics endpoints.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import get_db
from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    # Get total emails
    total_emails = db.query(func.count(Email.id)).scalar()
    
    # Get emails in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    recent_emails = db.query(func.count(Email.id)).filter(
        Email.received_at >= twenty_four_hours_ago
    ).scalar()
    
    # Get resolved emails
    resolved_emails = db.query(func.count(Email.id)).filter(
        Email.status == EmailStatus.RESOLVED
    ).scalar()
    
    # Get pending emails
    pending_emails = db.query(func.count(Email.id)).filter(
        Email.status == EmailStatus.PENDING
    ).scalar()
    
    # Get processed emails
    processed_emails = db.query(func.count(Email.id)).filter(
        Email.status == EmailStatus.PROCESSED
    ).scalar()
    
    stats = {
        "total_emails": total_emails,
        "recent_emails_24h": recent_emails,
        "resolved_emails": resolved_emails,
        "pending_emails": pending_emails,
        "processed_emails": processed_emails
    }
    
    return stats


@router.get("/sentiment")
async def get_sentiment_analysis(db: Session = Depends(get_db)):
    """Get sentiment analysis data."""
    # Count emails by sentiment
    sentiment_counts = db.query(
        Email.sentiment,
        func.count(Email.id)
    ).group_by(Email.sentiment).all()
    
    sentiment_data = {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    }
    
    for sentiment, count in sentiment_counts:
        sentiment_data[sentiment.value] = count
    
    return sentiment_data


@router.get("/priority")
async def get_priority_analysis(db: Session = Depends(get_db)):
    """Get priority analysis data."""
    # Count emails by priority
    priority_counts = db.query(
        Email.priority,
        func.count(Email.id)
    ).group_by(Email.priority).all()
    
    priority_data = {
        "urgent": 0,
        "not_urgent": 0
    }
    
    for priority, count in priority_counts:
        priority_data[priority.value] = count
    
    return priority_data


@router.get("/status")
async def get_status_analysis(db: Session = Depends(get_db)):
    """Get status analysis data."""
    # Count emails by status
    status_counts = db.query(
        Email.status,
        func.count(Email.id)
    ).group_by(Email.status).all()
    
    status_data = {}
    for status, count in status_counts:
        status_data[status.value] = count
    
    return status_data