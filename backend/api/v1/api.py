"""
API v1 router configuration.
"""
from fastapi import APIRouter

from backend.api.v1.endpoints import emails, responses, analytics, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(emails.router, prefix="/emails", tags=["emails"])
api_router.include_router(responses.router, prefix="/responses", tags=["responses"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])