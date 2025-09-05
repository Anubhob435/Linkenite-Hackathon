"""
Gmail API email provider implementation with OAuth2 authentication.
"""
import base64
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.email_providers.base import EmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class GmailEmailProvider(EmailProvider):
    """Gmail API email provider implementation with OAuth2."""
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 refresh_token: Optional[str] = None,
                 access_token: Optional[str] = None):
        if not client_id:
            raise ValueError("Gmail client_id is required")
        if not client_secret:
            raise ValueError("Gmail client_secret is required")
            
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.credentials = None
        self.service = None
    
    async def connect(self) -> bool:
        """Connect to Gmail API using OAuth2 credentials."""
        try:
            if self.refresh_token:
                # Use existing refresh token
                self.credentials = Credentials(
                    token=self.access_token,
                    refresh_token=self.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=self.SCOPES
                )
                
                # Refresh token if needed
                if not self.credentials.valid:
                    if self.credentials.expired and self.credentials.refresh_token:
                        self.credentials.refresh(Request())
                    else:
                        logger.error("Invalid credentials and no refresh token available")
                        return False
            else:
                logger.error("No refresh token provided for Gmail authentication")
                return False
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Connected to Gmail API successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Gmail API: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Gmail API."""
        try:
            self.service = None
            self.credentials = None
            logger.info("Disconnected from Gmail API")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Gmail API: {e}")
            return False
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """Get OAuth2 authorization URL for initial setup.
        
        Args:
            redirect_uri: The redirect URI for OAuth2 flow
            
        Returns:
            Authorization URL for user to visit
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from OAuth2 callback
            redirect_uri: The redirect URI used in the flow
            
        Returns:
            Dictionary containing access_token and refresh_token
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = redirect_uri
        
        flow.fetch_token(code=code)
        
        return {
            "access_token": flow.credentials.token,
            "refresh_token": flow.credentials.refresh_token
        }
    
    async def fetch_emails(self, 
                          folder: str = "INBOX",
                          since: datetime = None,
                          limit: int = 100) -> List[EmailMessage]:
        """Fetch emails from Gmail."""
        if not self.service:
            await self.connect()
        
        try:
            # Build query
            query = f"in:{folder.lower()}"
            if since:
                # Format date for Gmail search
                date_str = since.strftime("%Y/%m/%d")
                query += f" after:{date_str}"
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for message in messages:
                try:
                    # Get full message details
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Extract headers
                    headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
                    
                    # Extract body
                    body = self._extract_body(msg['payload'])
                    
                    # Parse received date
                    received_at = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
                    
                    # Create EmailMessage object
                    email_obj = EmailMessage(
                        message_id=headers.get('Message-ID', message['id']),
                        sender=headers.get('From', ''),
                        recipients=[headers.get('To', '')],
                        subject=headers.get('Subject', ''),
                        body=body,
                        received_at=received_at,
                        raw_data={
                            'gmail_id': message['id'],
                            'thread_id': msg.get('threadId'),
                            'labels': msg.get('labelIds', [])
                        }
                    )
                    
                    emails.append(email_obj)
                    
                except Exception as e:
                    logger.warning(f"Failed to process Gmail message {message['id']}: {e}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails from Gmail")
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching emails from Gmail: {e}")
            return []
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail message payload."""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    # Nested multipart
                    body = self._extract_body(part)
                    if body:
                        break
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a Gmail message as read."""
        if not self.service:
            await self.connect()
        
        try:
            # Find the Gmail message ID from our message ID
            gmail_id = None
            if hasattr(self, '_message_id_cache'):
                gmail_id = self._message_id_cache.get(message_id)
            
            if not gmail_id:
                # Search for the message by Message-ID header
                results = self.service.users().messages().list(
                    userId='me',
                    q=f'rfc822msgid:{message_id}'
                ).execute()
                
                messages = results.get('messages', [])
                if not messages:
                    logger.warning(f"Gmail message with ID {message_id} not found")
                    return False
                
                gmail_id = messages[0]['id']
            
            # Remove UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=gmail_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Marked Gmail message {message_id} as read")
            return True
            
        except HttpError as e:
            logger.error(f"Gmail API error marking message as read: {e}")
            return False
        except Exception as e:
            logger.error(f"Error marking Gmail message as read: {e}")
            return False
    
    async def send_email(self, 
                        to: List[str],
                        subject: str,
                        body: str,
                        cc: List[str] = None,
                        bcc: List[str] = None) -> str:
        """Send an email via Gmail API."""
        if not self.service:
            await self.connect()
        
        try:
            # Create message
            message = self._create_message(to, subject, body, cc, bcc)
            
            # Send message
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info(f"Sent email via Gmail API: {result['id']}")
            return result['id']
            
        except HttpError as e:
            logger.error(f"Gmail API error sending email: {e}")
            return ""
        except Exception as e:
            logger.error(f"Error sending email via Gmail: {e}")
            return ""
    
    def _create_message(self, 
                       to: List[str],
                       subject: str,
                       body: str,
                       cc: List[str] = None,
                       bcc: List[str] = None) -> Dict[str, str]:
        """Create a Gmail message object."""
        import email.mime.text
        import email.mime.multipart
        
        message = email.mime.multipart.MIMEMultipart()
        message['to'] = ', '.join(to)
        message['subject'] = subject
        
        if cc:
            message['cc'] = ', '.join(cc)
        if bcc:
            message['bcc'] = ', '.join(bcc)
        
        message.attach(email.mime.text.MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        return {'raw': raw_message}