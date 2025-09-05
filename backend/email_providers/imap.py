"""
IMAP email provider implementation.
"""
import asyncio
import imaplib
import email
from typing import List, Dict, Any
from datetime import datetime
import logging

from backend.email_providers.base import EmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class IMAPEmailProvider(EmailProvider):
    """IMAP email provider implementation."""
    
    def __init__(self, 
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.connection = None
    
    async def connect(self) -> bool:
        """Connect to the IMAP server."""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self.connection = imaplib.IMAP4(self.host, self.port)
            
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to IMAP server {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the IMAP server."""
        try:
            if self.connection:
                self.connection.close()
                self.connection.logout()
                self.connection = None
                logger.info("Disconnected from IMAP server")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from IMAP server: {e}")
            return False
    
    async def fetch_emails(self, 
                          folder: str = "INBOX",
                          since: datetime = None,
                          limit: int = 100) -> List[EmailMessage]:
        """Fetch emails from the IMAP server."""
        if not self.connection:
            await self.connect()
        
        try:
            # Select the folder
            self.connection.select(folder)
            
            # Search for emails
            if since:
                # Format date for IMAP search
                date_str = since.strftime("%d-%b-%Y")
                search_criteria = f'(SINCE "{date_str}")'
            else:
                search_criteria = "ALL"
            
            # Search for emails
            status, messages = self.connection.search(None, search_criteria)
            
            if status != "OK":
                logger.error("Failed to search emails")
                return []
            
            # Get message IDs
            email_ids = messages[0].split()
            
            # Limit the number of emails
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in email_ids:
                # Fetch the email
                status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    logger.warning(f"Failed to fetch email {email_id}")
                    continue
                
                # Parse the email
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract email data
                message_id = email_message.get("Message-ID", str(email_id))
                sender = email_message.get("From", "")
                recipients = email_message.get("To", "").split(",")
                subject = email_message.get("Subject", "")
                received_at = email_message.get("Date", "")
                
                # Parse received_at
                try:
                    received_at = datetime.strptime(received_at, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    received_at = datetime.now()
                
                # Extract body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8")
                            break
                else:
                    body = email_message.get_payload(decode=True).decode("utf-8")
                
                # Create EmailMessage object
                email_obj = EmailMessage(
                    message_id=message_id,
                    sender=sender,
                    recipients=recipients,
                    subject=subject,
                    body=body,
                    received_at=received_at,
                    raw_data={"imap_id": email_id.decode("utf-8")}
                )
                
                emails.append(email_obj)
            
            logger.info(f"Fetched {len(emails)} emails from IMAP server")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails from IMAP server: {e}")
            return []
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an email as read."""
        if not self.connection:
            await self.connect()
        
        try:
            # Find the email by message ID
            status, messages = self.connection.search(None, f'HEADER Message-ID "{message_id}"')
            
            if status != "OK" or not messages[0]:
                logger.warning(f"Email with Message-ID {message_id} not found")
                return False
            
            email_id = messages[0].split()[0]
            
            # Mark as read
            self.connection.store(email_id, '+FLAGS', '\\Seen')
            logger.info(f"Marked email {message_id} as read")
            return True
            
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    async def send_email(self, 
                        to: List[str],
                        subject: str,
                        body: str,
                        cc: List[str] = None,
                        bcc: List[str] = None) -> str:
        """Send an email via SMTP (not implemented in this IMAP-only provider)."""
        logger.warning("Send email not implemented for IMAP provider")
        return ""