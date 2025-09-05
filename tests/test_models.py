"""
Unit tests for database models.
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from backend.models import (
    Email, Response, KnowledgeItem, EmailProvider,
    SentimentType, PriorityLevel, EmailStatus, ResponseStatus, ProviderType
)


class TestEmailModel:
    """Test cases for Email model."""
    
    def test_create_email(self, db_session):
        """Test creating a basic email record."""
        email = Email(
            sender_email="test@example.com",
            subject="Test Subject",
            body="Test email body content",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEUTRAL,
            priority=PriorityLevel.NOT_URGENT,
            status=EmailStatus.PENDING
        )
        
        db_session.add(email)
        db_session.commit()
        
        # Verify the email was created
        saved_email = db_session.query(Email).filter_by(sender_email="test@example.com").first()
        assert saved_email is not None
        assert saved_email.subject == "Test Subject"
        assert saved_email.sentiment == SentimentType.NEUTRAL
        assert saved_email.priority == PriorityLevel.NOT_URGENT
        assert saved_email.status == EmailStatus.PENDING
        assert saved_email.id is not None
        assert saved_email.created_at is not None
    
    def test_email_with_extracted_info(self, db_session):
        """Test creating email with extracted information."""
        extracted_info = {
            "sender_domain": "example.com",
            "word_count": 50,
            "mentions_api": True,
            "contact_phone": "+1234567890"
        }
        
        email = Email(
            sender_email="user@example.com",
            subject="API Integration Help",
            body="I need help with API integration",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEGATIVE,
            priority=PriorityLevel.URGENT,
            extracted_info=extracted_info
        )
        
        db_session.add(email)
        db_session.commit()
        
        saved_email = db_session.query(Email).first()
        assert saved_email.extracted_info == extracted_info
        assert saved_email.extracted_info["mentions_api"] is True
    
    def test_email_required_fields(self, db_session):
        """Test that required fields are enforced."""
        # Missing sender_email should raise an error
        with pytest.raises(IntegrityError):
            email = Email(
                subject="Test Subject",
                body="Test body",
                received_at=datetime.utcnow(),
                sentiment=SentimentType.NEUTRAL,
                priority=PriorityLevel.NOT_URGENT
            )
            db_session.add(email)
            db_session.commit()
    
    def test_email_enum_values(self, db_session):
        """Test that enum values are properly handled."""
        email = Email(
            sender_email="test@example.com",
            subject="Test Subject",
            body="Test body",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.POSITIVE,
            priority=PriorityLevel.URGENT,
            status=EmailStatus.RESOLVED
        )
        
        db_session.add(email)
        db_session.commit()
        
        saved_email = db_session.query(Email).first()
        assert saved_email.sentiment == SentimentType.POSITIVE
        assert saved_email.priority == PriorityLevel.URGENT
        assert saved_email.status == EmailStatus.RESOLVED


class TestResponseModel:
    """Test cases for Response model."""
    
    def test_create_response(self, db_session):
        """Test creating a response linked to an email."""
        # First create an email
        email = Email(
            sender_email="test@example.com",
            subject="Test Subject",
            body="Test body",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEUTRAL,
            priority=PriorityLevel.NOT_URGENT
        )
        db_session.add(email)
        db_session.commit()
        
        # Create response
        response = Response(
            email_id=email.id,
            generated_content="Thank you for your inquiry. We will help you with this issue.",
            status=ResponseStatus.DRAFT
        )
        
        db_session.add(response)
        db_session.commit()
        
        # Verify response was created
        saved_response = db_session.query(Response).first()
        assert saved_response is not None
        assert saved_response.email_id == email.id
        assert saved_response.status == ResponseStatus.DRAFT
        assert saved_response.sent_at is None
        assert saved_response.id is not None
    
    def test_response_email_relationship(self, db_session):
        """Test the relationship between Response and Email."""
        # Create email
        email = Email(
            sender_email="test@example.com",
            subject="Test Subject",
            body="Test body",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEUTRAL,
            priority=PriorityLevel.NOT_URGENT
        )
        db_session.add(email)
        db_session.commit()
        
        # Create response
        response = Response(
            email_id=email.id,
            generated_content="Generated response content",
            edited_content="Edited response content",
            status=ResponseStatus.SENT,
            sent_at=datetime.utcnow()
        )
        db_session.add(response)
        db_session.commit()
        
        # Test relationship access
        saved_email = db_session.query(Email).first()
        saved_response = db_session.query(Response).first()
        
        assert saved_response.email == saved_email
        assert saved_email.response == saved_response
    
    def test_response_status_enum(self, db_session):
        """Test response status enum values."""
        email = Email(
            sender_email="test@example.com",
            subject="Test",
            body="Test",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEUTRAL,
            priority=PriorityLevel.NOT_URGENT
        )
        db_session.add(email)
        db_session.commit()
        
        response = Response(
            email_id=email.id,
            generated_content="Test response",
            status=ResponseStatus.FAILED
        )
        db_session.add(response)
        db_session.commit()
        
        saved_response = db_session.query(Response).first()
        assert saved_response.status == ResponseStatus.FAILED


class TestKnowledgeItemModel:
    """Test cases for KnowledgeItem model."""
    
    def test_create_knowledge_item(self, db_session):
        """Test creating a knowledge base item."""
        knowledge_item = KnowledgeItem(
            title="How to reset password",
            content="To reset your password, click on the 'Forgot Password' link...",
            category="authentication",
            tags=["password", "reset", "login"]
        )
        
        db_session.add(knowledge_item)
        db_session.commit()
        
        saved_item = db_session.query(KnowledgeItem).first()
        assert saved_item is not None
        assert saved_item.title == "How to reset password"
        assert saved_item.category == "authentication"
        assert saved_item.tags == ["password", "reset", "login"]
        assert saved_item.id is not None
        assert saved_item.created_at is not None
    
    def test_knowledge_item_without_optional_fields(self, db_session):
        """Test creating knowledge item with only required fields."""
        knowledge_item = KnowledgeItem(
            title="Basic Help",
            content="Basic help content"
        )
        
        db_session.add(knowledge_item)
        db_session.commit()
        
        saved_item = db_session.query(KnowledgeItem).first()
        assert saved_item.title == "Basic Help"
        assert saved_item.category is None
        assert saved_item.tags is None


class TestEmailProviderModel:
    """Test cases for EmailProvider model."""
    
    def test_create_email_provider(self, db_session):
        """Test creating an email provider configuration."""
        config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "http://localhost:8000/callback"
        }
        
        provider = EmailProvider(
            provider_type=ProviderType.GMAIL,
            configuration=config,
            is_active=True
        )
        
        db_session.add(provider)
        db_session.commit()
        
        saved_provider = db_session.query(EmailProvider).first()
        assert saved_provider is not None
        assert saved_provider.provider_type == ProviderType.GMAIL
        assert saved_provider.configuration == config
        assert saved_provider.is_active is True
        assert saved_provider.id is not None
    
    def test_provider_type_enum(self, db_session):
        """Test provider type enum values."""
        providers = [
            EmailProvider(
                provider_type=ProviderType.GMAIL,
                configuration={"test": "gmail"}
            ),
            EmailProvider(
                provider_type=ProviderType.OUTLOOK,
                configuration={"test": "outlook"}
            ),
            EmailProvider(
                provider_type=ProviderType.IMAP,
                configuration={"test": "imap"}
            )
        ]
        
        for provider in providers:
            db_session.add(provider)
        db_session.commit()
        
        saved_providers = db_session.query(EmailProvider).all()
        assert len(saved_providers) == 3
        
        provider_types = [p.provider_type for p in saved_providers]
        assert ProviderType.GMAIL in provider_types
        assert ProviderType.OUTLOOK in provider_types
        assert ProviderType.IMAP in provider_types


class TestModelRelationships:
    """Test cases for model relationships and constraints."""
    
    def test_email_response_relationship_integrity(self, db_session):
        """Test the foreign key relationship between email and response."""
        # Create email and response
        email = Email(
            sender_email="test@example.com",
            subject="Test",
            body="Test body",
            received_at=datetime.utcnow(),
            sentiment=SentimentType.NEUTRAL,
            priority=PriorityLevel.NOT_URGENT
        )
        db_session.add(email)
        db_session.commit()
        
        response = Response(
            email_id=email.id,
            generated_content="Test response",
            status=ResponseStatus.DRAFT
        )
        db_session.add(response)
        db_session.commit()
        
        # Verify both exist
        assert db_session.query(Email).count() == 1
        assert db_session.query(Response).count() == 1
        
        # Test that we can access the relationship
        saved_response = db_session.query(Response).first()
        assert saved_response.email_id == email.id
        
        # Delete response first, then email (proper order)
        db_session.delete(response)
        db_session.delete(email)
        db_session.commit()
        
        # Both should be deleted
        assert db_session.query(Email).count() == 0
        assert db_session.query(Response).count() == 0
    
    def test_multiple_knowledge_items(self, db_session):
        """Test creating multiple knowledge items."""
        items = [
            KnowledgeItem(
                title="Password Reset",
                content="How to reset password",
                category="auth"
            ),
            KnowledgeItem(
                title="Account Verification",
                content="How to verify account",
                category="auth"
            ),
            KnowledgeItem(
                title="Billing Issues",
                content="How to handle billing",
                category="billing"
            )
        ]
        
        for item in items:
            db_session.add(item)
        db_session.commit()
        
        # Test querying by category
        auth_items = db_session.query(KnowledgeItem).filter_by(category="auth").all()
        assert len(auth_items) == 2
        
        billing_items = db_session.query(KnowledgeItem).filter_by(category="billing").all()
        assert len(billing_items) == 1