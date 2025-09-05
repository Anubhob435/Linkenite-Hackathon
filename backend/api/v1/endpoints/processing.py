"""
Email processing endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.email_workflow import EmailProcessingWorkflow
from backend.models.email import Email

router = APIRouter()


@router.post("/process")
async def process_pending_emails(batch_size: int = 10, db: Session = Depends(get_db)):
    """Process pending emails in batches."""
    workflow = EmailProcessingWorkflow()
    
    # Get pending emails from database
    emails = db.query(Email).filter(Email.status == "pending").all()
    
    # Add emails to workflow queue
    for email in emails:
        workflow.add_email_to_queue(email)
    
    # Process emails in batches
    processed_count = 0
    while workflow.get_queue_size() > 0 and processed_count < batch_size:
        if workflow.process_next_email(db):
            processed_count += 1
        else:
            break
    
    return {
        "message": f"Processed {processed_count} emails",
        "remaining_in_queue": workflow.get_queue_size()
    }


@router.post("/process/{email_id}")
async def process_single_email(email_id: str, db: Session = Depends(get_db)):
    """Process a single email by ID."""
    workflow = EmailProcessingWorkflow()
    
    # Get email from database
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    if email.status != "pending":
        raise HTTPException(status_code=400, detail="Email is not in pending status")
    
    # Add email to workflow queue and process it
    workflow.add_email_to_queue(email)
    
    success = workflow.process_next_email(db)
    if success:
        return {"message": "Email processed successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to process email")