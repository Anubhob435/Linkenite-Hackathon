"""
Analytics endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return {"message": "Dashboard analytics - to be implemented"}


@router.get("/sentiment")
async def get_sentiment_analysis():
    """Get sentiment analysis data."""
    return {"message": "Sentiment analytics - to be implemented"}