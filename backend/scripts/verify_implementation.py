"""
Verification script to demonstrate database models and CSV ingestion functionality.
"""
import logging
from sqlalchemy import func

from backend.core.database import get_db_session
from backend.models import Email, Response, KnowledgeItem, EmailProvider
from backend.models import SentimentType, PriorityLevel, EmailStatus, ResponseStatus, ProviderType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_database_models():
    """Verify that database models are working correctly."""
    logger.info("Verifying database models...")
    
    with get_db_session() as db:
        # Check email records
        total_emails = db.query(Email).count()
        logger.info(f"Total emails in database: {total_emails}")
        
        # Check sentiment distribution
        sentiment_counts = db.query(
            Email.sentiment, 
            func.count(Email.id)
        ).group_by(Email.sentiment).all()
        
        logger.info("Sentiment distribution:")
        for sentiment, count in sentiment_counts:
            logger.info(f"  {sentiment.value}: {count}")
        
        # Check priority distribution
        priority_counts = db.query(
            Email.priority, 
            func.count(Email.id)
        ).group_by(Email.priority).all()
        
        logger.info("Priority distribution:")
        for priority, count in priority_counts:
            logger.info(f"  {priority.value}: {count}")
        
        # Check status distribution
        status_counts = db.query(
            Email.status, 
            func.count(Email.id)
        ).group_by(Email.status).all()
        
        logger.info("Status distribution:")
        for status, count in status_counts:
            logger.info(f"  {status.value}: {count}")
        
        # Show sample emails
        sample_emails = db.query(Email).limit(3).all()
        logger.info(f"\nSample emails:")
        for email in sample_emails:
            logger.info(f"  From: {email.sender_email}")
            logger.info(f"  Subject: {email.subject}")
            logger.info(f"  Sentiment: {email.sentiment.value}, Priority: {email.priority.value}")
            logger.info(f"  Extracted info: {email.extracted_info}")
            logger.info("  ---")
        
        # Check other tables
        response_count = db.query(Response).count()
        knowledge_count = db.query(KnowledgeItem).count()
        provider_count = db.query(EmailProvider).count()
        
        logger.info(f"\nOther table counts:")
        logger.info(f"  Responses: {response_count}")
        logger.info(f"  Knowledge items: {knowledge_count}")
        logger.info(f"  Email providers: {provider_count}")


def create_sample_data():
    """Create some sample data to demonstrate relationships."""
    logger.info("Creating sample data...")
    
    with get_db_session() as db:
        # Create a sample knowledge item
        knowledge_item = KnowledgeItem(
            title="Password Reset Instructions",
            content="To reset your password, click on 'Forgot Password' and follow the instructions sent to your email.",
            category="authentication",
            tags=["password", "reset", "login", "help"]
        )
        db.add(knowledge_item)
        
        # Create a sample email provider
        provider = EmailProvider(
            provider_type=ProviderType.GMAIL,
            configuration={
                "client_id": "sample_client_id",
                "client_secret": "sample_client_secret",
                "redirect_uri": "http://localhost:8000/callback"
            },
            is_active=True
        )
        db.add(provider)
        
        # Get a sample email and create a response for it
        sample_email = db.query(Email).first()
        if sample_email:
            response = Response(
                email_id=sample_email.id,
                generated_content="Thank you for contacting us. We understand your concern and will help you resolve this issue promptly.",
                status=ResponseStatus.DRAFT
            )
            db.add(response)
        
        logger.info("Sample data created successfully")


def main():
    """Main verification function."""
    logger.info("Starting database implementation verification...")
    
    try:
        verify_database_models()
        create_sample_data()
        
        # Verify again after creating sample data
        logger.info("\nAfter creating sample data:")
        verify_database_models()
        
        logger.info("\n✅ Database implementation verification completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise


if __name__ == "__main__":
    main()