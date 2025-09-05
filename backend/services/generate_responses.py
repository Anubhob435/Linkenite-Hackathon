"""
Script to generate responses for emails in the database.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.models.email import Email
from backend.models.response import Response
from backend.services.response_generation import ResponseGenerator
from backend.services.knowledge_base import KnowledgeBase


def generate_responses():
    """Generate responses for emails in the database."""
    # Create database session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get processed emails from database that don't have responses yet
        emails = db.query(Email).filter(Email.status == "processed").all()
        print(f"Found {len(emails)} processed emails in database")
        
        # Create knowledge base with sample items
        kb = KnowledgeBase()
        kb.add_item(
            title="Account Login Issues",
            content="If you're unable to log into your account, try resetting your password. Click 'Forgot Password' on the login page and follow the instructions sent to your email.",
            category="Account Management",
            tags=["login", "account", "password"]
        )
        
        kb.add_item(
            title="Password Reset Process",
            content="To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your email address, 3) Check your email for a password reset link, 4) Click the link and enter a new password.",
            category="Account Management",
            tags=["password", "reset", "account"]
        )
        
        kb.add_item(
            title="Billing Issues",
            content="For billing issues, please contact our billing department at billing@company.com or call 1-800-123-4567.",
            category="Billing",
            tags=["billing", "payment", "invoice"]
        )
        
        kb.add_item(
            title="System Downtime and Outages",
            content="We strive for 99.9% uptime. If you're experiencing system issues, check our status page at status.company.com for current outages. For urgent issues, contact support with details about the problem.",
            category="Technical Support",
            tags=["downtime", "outage", "system", "error"]
        )
        
        kb.add_item(
            title="API Integration Support",
            content="For API integration questions, refer to our developer documentation at docs.company.com. Common integration issues include authentication errors, rate limiting, and incorrect endpoint usage.",
            category="Developer Support",
            tags=["api", "integration", "developer", "documentation"]
        )
        
        # Create response generator
        generator = ResponseGenerator(kb)
        
        # Generate responses for each email
        for email in emails:
            print(f"Generating response for: {email.subject[:50]}...")
            
            # Generate appropriate response based on sentiment
            if email.sentiment == "negative":
                generated_content = generator.generate_empathetic_response(
                    email.subject, email.body, email.sentiment, email.extracted_info
                )
            else:
                generated_content = generator.generate_response(
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
        
        # Commit changes to database
        db.commit()
        print(f"Generated and saved responses for {len(emails)} emails")
        
    except Exception as e:
        print(f"Error generating responses: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    generate_responses()