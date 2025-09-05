"""
Response management endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_response():
    """Create a new response."""
    return {"message": "Create response - to be implemented"}


@router.get("/{response_id}")
async def get_response(response_id: str):
    """Get specific response by ID."""
    return {"message": f"Get response {response_id} - to be implemented"}