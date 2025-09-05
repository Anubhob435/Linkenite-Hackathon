"""
Email processing workflow and priority queue system.
"""
import asyncio
import heapq
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from backend.models.email import Email, PriorityLevel, EmailStatus
from backend.models.response import Response
from backend.services.email_retrieval import EmailRetrievalService
from backend.services.ai_processing import AIProcessingEngine
from backend.services.response_generation import ResponseGenerator
from backend.services.knowledge_base import KnowledgeBase
from backend.core.database import get_db

logger = logging.getLogger(__name__)


class EmailProcessingWorkflow:
    """Email processing workflow manager."""
    
    def __init__(self):
        self.email_retrieval_service = EmailRetrievalService()
        self.ai_engine = AIProcessingEngine()
        
        # Create knowledge base
        self.knowledge_base = KnowledgeBase()
        self._seed_knowledge_base()
        
        self.response_generator = ResponseGenerator(self.knowledge_base)
        self.processing_queue = []  # Priority queue
        self._counter = 0  # To ensure unique timestamps for heapq comparison
    
    def _seed_knowledge_base(self):
        """Seed the knowledge base with common support issues."""
        common_issues = [
            {
                "title": "Account Login Issues",
                "content": "If you're unable to log into your account, try resetting your password. Click 'Forgot Password' on the login page and follow the instructions sent to your email.",
                "category": "Account Management",
                "tags": ["login", "account", "password"]
            },
            {
                "title": "Password Reset Process",
                "content": "To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your email address, 3) Check your email for a password reset link, 4) Click the link and enter a new password.",
                "category": "Account Management",
                "tags": ["password", "reset", "account"]
            },
            {
                "title": "Billing Issues",
                "content": "For billing issues, please contact our billing department at billing@company.com or call 1-800-123-4567.",
                "category": "Billing",
                "tags": ["billing", "payment", "invoice"]
            },
            {
                "title": "System Downtime and Outages",
                "content": "We strive for 99.9% uptime. If you're experiencing system issues, check our status page at status.company.com for current outages. For urgent issues, contact support with details about the problem.",
                "category": "Technical Support",
                "tags": ["downtime", "outage", "system", "error"]
            },
            {
                "title": "API Integration Support",
                "content": "For API integration questions, refer to our developer documentation at docs.company.com. Common integration issues include authentication errors, rate limiting, and incorrect endpoint usage.",
                "category": "Developer Support",
                "tags": ["api", "integration", "developer", "documentation"]
            }
        ]
        
        for issue in common_issues:
            self.knowledge_base.add_item(
                title=issue["title"],
                content=issue["content"],
                category=issue["category"],
                tags=issue["tags"]
            )
    
    def add_email_to_queue(self, email: Email):
        """Add an email to the processing queue.
        
        Args:
            email: Email object to add to queue
        """
        # Priority calculation: urgent emails get higher priority (lower number)
        priority = 0 if email.priority == PriorityLevel.URGENT else 1
        
        # Use heapq to maintain priority queue
        # Add a counter to ensure unique comparison values
        heapq.heappush(self.processing_queue, (priority, self._counter, datetime.now(), email))
        self._counter += 1
        logger.info(f"Added email to queue: {email.subject[:30]}... (Priority: {priority})")
    
    def process_next_email(self, db) -> bool:
        """Process the next email in the queue.
        
        Args:
            db: Database session
            
        Returns:
            True if an email was processed, False if queue is empty
        """
        if not self.processing_queue:
            return False
        
        # Get the highest priority email
        priority, counter, timestamp, email = heapq.heappop(self.processing_queue)
        
        try:
            logger.info(f"Processing email: {email.subject[:30]}...")
            
            # Process email through AI engine
            ai_results = self.ai_engine.process_email(email.subject, email.body)
            
            # Update email with AI results
            email.sentiment = ai_results["sentiment"]
            email.priority = ai_results["priority"]
            
            # Update extracted_info with AI results
            if email.extracted_info:
                email.extracted_info.update(ai_results["extracted_info"])
            else:
                email.extracted_info = ai_results["extracted_info"]
            
            # Update email status
            email.status = EmailStatus.PROCESSED
            
            # Generate response
            if email.sentiment == "negative":
                generated_content = self.response_generator.generate_empathetic_response(
                    email.subject, email.body, email.sentiment, email.extracted_info
                )
            else:
                generated_content = self.response_generator.generate_response(
                    email.subject, email.body, email.sentiment, email.extracted_info
                )
            
            # Create response object
            response = Response(
                email_id=email.id,
                generated_content=generated_content,
                status="draft"
            )
            
            # Add response to database
            db.add(response)
            
            # Commit changes
            db.commit()
            
            logger.info(f"Processed email: {email.subject[:30]}... (Priority: {priority})")
            return True
            
        except Exception as e:
            logger.error(f"Error processing email {email.id}: {e}")
            db.rollback()
            # Update email status to failed
            email.status = EmailStatus.FAILED
            db.commit()
            return True
    
    def process_batch(self, db, batch_size: int = 10) -> int:
        """Process a batch of emails from the queue.
        
        Args:
            db: Database session
            batch_size: Number of emails to process in batch
            
        Returns:
            Number of emails processed
        """
        processed_count = 0
        
        for _ in range(batch_size):
            if self.process_next_email(db):
                processed_count += 1
            else:
                break  # Queue is empty
        
        logger.info(f"Processed {processed_count} emails in batch")
        return processed_count
    
    def get_queue_size(self) -> int:
        """Get the current size of the processing queue.
        
        Returns:
            Number of emails in the queue
        """
        return len(self.processing_queue)
    
    def get_queue_summary(self) -> Dict[str, int]:
        """Get a summary of the processing queue.
        
        Returns:
            Dictionary with queue statistics
        """
        urgent_count = 0
        normal_count = 0
        
        for priority, counter, timestamp, email in self.processing_queue:
            if priority == 0:
                urgent_count += 1
            else:
                normal_count += 1
        
        return {
            "total": len(self.processing_queue),
            "urgent": urgent_count,
            "normal": normal_count
        }


# Example usage
async def example_usage():
    """Example usage of the EmailProcessingWorkflow."""
    workflow = EmailProcessingWorkflow()
    
    # Create some sample emails
    from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus
    import uuid
    
    email1 = Email(
        id=str(uuid.uuid4()),
        sender_email="user1@example.com",
        subject="Urgent: System access blocked",
        body="I cannot access the system. This is critical for my work.",
        received_at=datetime.now(),
        sentiment=SentimentType.NEGATIVE,
        priority=PriorityLevel.URGENT,
        status=EmailStatus.PENDING
    )
    
    email2 = Email(
        id=str(uuid.uuid4()),
        sender_email="user2@example.com",
        subject="General query about subscription",
        body="I would like to know more about your subscription options.",
        received_at=datetime.now(),
        sentiment=SentimentType.NEUTRAL,
        priority=PriorityLevel.NOT_URGENT,
        status=EmailStatus.PENDING
    )
    
    # Add emails to queue
    workflow.add_email_to_queue(email1)
    workflow.add_email_to_queue(email2)
    
    print(f"Queue size: {workflow.get_queue_size()}")
    print(f"Queue summary: {workflow.get_queue_summary()}")
    
    # Process emails (in a real implementation, we would have a database session)
    print("In a real implementation, emails would be processed with a database session")


if __name__ == "__main__":
    example_usage()