"""
Email retrieval and filtering service.
"""
import asyncio
import re
from typing import List, Dict, Any
from datetime import datetime
import logging

from backend.email_providers import create_email_provider, EmailMessage
from backend.models.email import Email, SentimentType, PriorityLevel, EmailStatus
from backend.core.database import get_db

logger = logging.getLogger(__name__)


class EmailRetrievalService:
    """Service for retrieving and filtering emails."""
    
    def __init__(self):
        self.support_keywords = ["support", "query", "request", "help"]
    
    async def retrieve_emails_from_provider(self, 
                                          provider_type: str,
                                          provider_config: Dict[str, Any],
                                          folder: str = "INBOX",
                                          since: datetime = None,
                                          limit: int = 100) -> List[EmailMessage]:
        """Retrieve emails from a specific provider.
        
        Args:
            provider_type: The type of email provider (imap, gmail, outlook)
            provider_config: Configuration for the provider
            folder: The folder to retrieve emails from
            since: Only retrieve emails received after this date
            limit: Maximum number of emails to retrieve
            
        Returns:
            List of EmailMessage objects
        """
        try:
            provider = create_email_provider(provider_type, provider_config)
            connected = await provider.connect()
            
            if not connected:
                logger.error(f"Failed to connect to {provider_type} provider")
                return []
            
            emails = await provider.fetch_emails(folder=folder, since=since, limit=limit)
            await provider.disconnect()
            
            logger.info(f"Retrieved {len(emails)} emails from {provider_type} provider")
            return emails
            
        except Exception as e:
            logger.error(f"Error retrieving emails from {provider_type} provider: {e}")
            return []
    
    def filter_support_emails(self, emails: List[EmailMessage]) -> List[EmailMessage]:
        """Filter emails to only include support-related emails.
        
        Args:
            emails: List of EmailMessage objects
            
        Returns:
            List of filtered EmailMessage objects
        """
        filtered_emails = []
        
        for email in emails:
            # Check if subject contains support keywords
            subject_lower = email.subject.lower()
            if any(keyword in subject_lower for keyword in self.support_keywords):
                filtered_emails.append(email)
        
        logger.info(f"Filtered {len(filtered_emails)} support emails from {len(emails)} total emails")
        return filtered_emails
    
    def extract_email_metadata(self, email_message: EmailMessage) -> Dict[str, Any]:
        """Extract metadata from an email message.
        
        Args:
            email_message: EmailMessage object
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {
            "sender_email": email_message.sender,
            "subject": email_message.subject,
            "body": email_message.body,
            "received_at": email_message.received_at,
            "recipients": email_message.recipients,
            "message_id": email_message.message_id
        }
        
        # Extract contact information
        contact_info = self._extract_contact_info(email_message.body)
        metadata["contact_info"] = contact_info
        
        # Extract requirements
        requirements = self._extract_requirements(email_message.body)
        metadata["requirements"] = requirements
        
        return metadata
    
    def _extract_contact_info(self, body: str) -> Dict[str, Any]:
        """Extract contact information from email body.
        
        Args:
            body: Email body text
            
        Returns:
            Dictionary containing extracted contact information
        """
        contact_info = {}
        
        # Extract phone numbers (simple pattern)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, body)
        contact_info["phones"] = phones
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, body)
        contact_info["emails"] = emails
        
        return contact_info
    
    def _extract_requirements(self, body: str) -> List[str]:
        """Extract requirements from email body.
        
        Args:
            body: Email body text
            
        Returns:
            List of extracted requirements
        """
        # Simple extraction - in a real implementation, this would be more sophisticated
        requirements = []
        
        # Look for common requirement patterns
        requirement_patterns = [
            r'(need|require|want|looking for)\s+(.+?)[.!?]',
            r'(help with|assistance with)\s+(.+?)[.!?]',
            r'(issue with|problem with)\s+(.+?)[.!?]'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    requirements.append(match[1].strip())
                else:
                    requirements.append(match.strip())
        
        return requirements
    
    def convert_to_db_model(self, email_message: EmailMessage) -> Email:
        """Convert an EmailMessage to a database Email model.
        
        Args:
            email_message: EmailMessage object
            
        Returns:
            Email database model
        """
        metadata = self.extract_email_metadata(email_message)
        
        email_model = Email(
            sender_email=metadata["sender_email"],
            subject=metadata["subject"],
            body=metadata["body"],
            received_at=metadata["received_at"],
            sentiment=SentimentType.NEUTRAL,  # Will be updated by AI processing
            priority=PriorityLevel.NOT_URGENT,  # Will be updated by AI processing
            status=EmailStatus.PENDING,
            extracted_info=metadata
        )
        
        return email_model
    
    def deduplicate_emails(self, emails: List[Email]) -> List[Email]:
        """Remove duplicate emails based on message ID.
        
        Args:
            emails: List of Email objects
            
        Returns:
            List of deduplicated Email objects
        """
        seen_message_ids = set()
        unique_emails = []
        
        for email in emails:
            # Use subject + sender + received_at as a proxy for message ID
            # since we don't have a real message ID in our sample data
            message_id = f"{email.subject}_{email.sender_email}_{email.received_at}"
            
            if message_id not in seen_message_ids:
                seen_message_ids.add(message_id)
                unique_emails.append(email)
        
        logger.info(f"Deduplicated emails: {len(emails)} -> {len(unique_emails)}")
        return unique_emails


# Example usage
async def example_usage():
    """Example usage of the EmailRetrievalService."""
    service = EmailRetrievalService()
    
    # Example configuration (won't work with dummy values)
    config = {
        "host": "imap.example.com",
        "port": 993,
        "username": "user@example.com",
        "password": "password",
        "use_ssl": True
    }
    
    # Retrieve emails (this will fail with dummy config)
    emails = await service.retrieve_emails_from_provider("imap", config)
    print(f"Retrieved {len(emails)} emails")
    
    # Filter support emails
    support_emails = service.filter_support_emails(emails)
    print(f"Filtered {len(support_emails)} support emails")
    
    # Convert to database models
    db_emails = [service.convert_to_db_model(email) for email in support_emails]
    print(f"Converted {len(db_emails)} emails to database models")


if __name__ == "__main__":
    asyncio.run(example_usage())