"""
Base email provider abstract class and common interfaces.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class EmailMessage:
    """Represents an email message."""
    
    def __init__(self, 
                 message_id: str,
                 sender: str,
                 recipients: List[str],
                 subject: str,
                 body: str,
                 received_at: datetime,
                 raw_data: Dict[str, Any] = None):
        self.message_id = message_id
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.received_at = received_at
        self.raw_data = raw_data or {}


class EmailProvider(ABC):
    """Abstract base class for email providers."""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the email provider."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the email provider."""
        pass
    
    @abstractmethod
    async def fetch_emails(self, 
                          folder: str = "INBOX",
                          since: datetime = None,
                          limit: int = 100) -> List[EmailMessage]:
        """Fetch emails from the provider.
        
        Args:
            folder: The folder to fetch emails from (default: INBOX)
            since: Only fetch emails received after this date
            limit: Maximum number of emails to fetch
            
        Returns:
            List of EmailMessage objects
        """
        pass
    
    @abstractmethod
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read.
        
        Args:
            message_id: The ID of the message to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_email(self, 
                        to: List[str],
                        subject: str,
                        body: str,
                        cc: List[str] = None,
                        bcc: List[str] = None) -> str:
        """Send an email.
        
        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            
        Returns:
            Message ID of the sent email
        """
        pass