"""
Email management endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_emails():
    """List all emails."""
    return {"message": "Email endpoints - to be implemented"}


@router.get("/{email_id}")
async def get_email(email_id: str):
    """Get specific email by ID."""
    return {"message": f"Get email {email_id} - to be implemented"}