"""
Response management endpoints.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.response import Response, ResponseStatus

router = APIRouter()


@router.post("/")
async def create_response(email_id: str, content: str, db: Session = Depends(get_db)):
    """Create a new response."""
    response = Response(
        email_id=email_id,
        generated_content=content,
        status=ResponseStatus.DRAFT
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


@router.get("/{response_id}")
async def get_response(response_id: str, db: Session = Depends(get_db)):
    """Get specific response by ID."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response


@router.put("/{response_id}")
async def update_response(response_id: str, content: Optional[str] = None, 
                         status: Optional[ResponseStatus] = None, 
                         db: Session = Depends(get_db)):
    """Update response content or status."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    if content is not None:
        response.edited_content = content
    
    if status is not None:
        response.status = status
    
    db.commit()
    db.refresh(response)
    return response


@router.post("/{response_id}/send")
async def send_response(response_id: str, db: Session = Depends(get_db)):
    """Send response to customer."""
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    # In a real implementation, this would actually send the email
    response.status = ResponseStatus.SENT
    response.sent_at = datetime.utcnow()
    
    db.commit()
    db.refresh(response)
    return response