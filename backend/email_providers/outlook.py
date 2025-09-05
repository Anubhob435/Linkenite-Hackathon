"""
Outlook Graph API email provider implementation with OAuth2 authentication.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

import msal
import requests

from backend.email_providers.base import EmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class OutlookEmailProvider(EmailProvider):
    """Outlook Graph API email provider implementation with OAuth2."""
    
    # Microsoft Graph API scopes
    SCOPES = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Mail.ReadWrite'
    ]
    
    # Microsoft Graph API endpoints
    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    AUTHORITY = 'https://login.microsoftonline.com/common'
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 refresh_token: Optional[str] = None,
                 access_token: Optional[str] = None,
                 tenant_id: str = 'common'):
        if not client_id:
            raise ValueError("Outlook client_id is required")
        if not client_secret:
            raise ValueError("Outlook client_secret is required")
            
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.tenant_id = tenant_id
        self.app = None
        self.headers = None
    
    async def connect(self) -> bool:
        """Connect to Outlook Graph API using OAuth2 credentials."""
        try:
            # Create MSAL app
            self.app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"{self.AUTHORITY}/{self.tenant_id}"
            )
            
            if self.refresh_token:
                # Use refresh token to get new access token
                result = self.app.acquire_token_by_refresh_token(
                    refresh_token=self.refresh_token,
                    scopes=self.SCOPES
                )
                
                if 'access_token' in result:
                    self.access_token = result['access_token']
                    self.headers = {
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    }
                    logger.info("Connected to Outlook Graph API successfully")
                    return True
                else:
                    logger.error(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
                    return False
            elif self.access_token:
                # Use existing access token
                self.headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Test the token by making a simple API call
                response = requests.get(
                    f"{self.GRAPH_API_ENDPOINT}/me",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    logger.info("Connected to Outlook Graph API successfully")
                    return True
                else:
                    logger.error(f"Access token invalid: {response.status_code}")
                    return False
            else:
                logger.error("No access token or refresh token provided for Outlook authentication")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Outlook Graph API: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Outlook Graph API."""
        try:
            self.app = None
            self.headers = None
            self.access_token = None
            logger.info("Disconnected from Outlook Graph API")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Outlook Graph API: {e}")
            return False
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """Get OAuth2 authorization URL for initial setup.
        
        Args:
            redirect_uri: The redirect URI for OAuth2 flow
            
        Returns:
            Authorization URL for user to visit
        """
        if not self.app:
            self.app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"{self.AUTHORITY}/{self.tenant_id}"
            )
        
        auth_url = self.app.get_authorization_request_url(
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
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
        if not self.app:
            self.app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=f"{self.AUTHORITY}/{self.tenant_id}"
            )
        
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        if 'access_token' in result:
            return {
                "access_token": result['access_token'],
                "refresh_token": result.get('refresh_token', '')
            }
        else:
            raise Exception(f"Failed to exchange code for tokens: {result.get('error_description', 'Unknown error')}")
    
    async def fetch_emails(self, 
                          folder: str = "INBOX",
                          since: datetime = None,
                          limit: int = 100) -> List[EmailMessage]:
        """Fetch emails from Outlook."""
        if not self.headers:
            await self.connect()
        
        try:
            # Build API endpoint
            endpoint = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders/{folder}/messages"
            
            # Build query parameters
            params = {
                '$top': limit,
                '$orderby': 'receivedDateTime desc'
            }
            
            if since:
                # Format date for Graph API filter
                since_str = since.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                params['$filter'] = f"receivedDateTime ge {since_str}"
            
            # Make API request
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Outlook API error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            messages = data.get('value', [])
            
            emails = []
            for message in messages:
                try:
                    # Extract recipients
                    recipients = []
                    for recipient in message.get('toRecipients', []):
                        recipients.append(recipient['emailAddress']['address'])
                    
                    # Parse received date
                    received_at_str = message.get('receivedDateTime', '')
                    received_at = datetime.fromisoformat(received_at_str.replace('Z', '+00:00'))
                    
                    # Extract body
                    body_content = message.get('body', {})
                    body = body_content.get('content', '') if body_content else ''
                    
                    # Create EmailMessage object
                    email_obj = EmailMessage(
                        message_id=message.get('internetMessageId', message.get('id')),
                        sender=message.get('from', {}).get('emailAddress', {}).get('address', ''),
                        recipients=recipients,
                        subject=message.get('subject', ''),
                        body=body,
                        received_at=received_at,
                        raw_data={
                            'outlook_id': message.get('id'),
                            'conversation_id': message.get('conversationId'),
                            'is_read': message.get('isRead', False),
                            'importance': message.get('importance', 'normal')
                        }
                    )
                    
                    emails.append(email_obj)
                    
                except Exception as e:
                    logger.warning(f"Failed to process Outlook message {message.get('id')}: {e}")
                    continue
            
            logger.info(f"Fetched {len(emails)} emails from Outlook")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails from Outlook: {e}")
            return []
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark an Outlook message as read."""
        if not self.headers:
            await self.connect()
        
        try:
            # Find the Outlook message ID
            outlook_id = None
            
            # First try to find by internet message ID
            search_endpoint = f"{self.GRAPH_API_ENDPOINT}/me/messages"
            search_params = {
                '$filter': f"internetMessageId eq '{message_id}'"
            }
            
            response = requests.get(search_endpoint, headers=self.headers, params=search_params)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('value', [])
                if messages:
                    outlook_id = messages[0]['id']
            
            if not outlook_id:
                logger.warning(f"Outlook message with ID {message_id} not found")
                return False
            
            # Mark as read
            update_endpoint = f"{self.GRAPH_API_ENDPOINT}/me/messages/{outlook_id}"
            update_data = {'isRead': True}
            
            response = requests.patch(
                update_endpoint,
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Marked Outlook message {message_id} as read")
                return True
            else:
                logger.error(f"Failed to mark message as read: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking Outlook message as read: {e}")
            return False
    
    async def send_email(self, 
                        to: List[str],
                        subject: str,
                        body: str,
                        cc: List[str] = None,
                        bcc: List[str] = None) -> str:
        """Send an email via Outlook Graph API."""
        if not self.headers:
            await self.connect()
        
        try:
            # Build message object
            message = {
                'subject': subject,
                'body': {
                    'contentType': 'Text',
                    'content': body
                },
                'toRecipients': [
                    {'emailAddress': {'address': email}} for email in to
                ]
            }
            
            if cc:
                message['ccRecipients'] = [
                    {'emailAddress': {'address': email}} for email in cc
                ]
            
            if bcc:
                message['bccRecipients'] = [
                    {'emailAddress': {'address': email}} for email in bcc
                ]
            
            # Send message
            endpoint = f"{self.GRAPH_API_ENDPOINT}/me/sendMail"
            send_data = {'message': message}
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=send_data
            )
            
            if response.status_code == 202:  # Accepted
                logger.info("Sent email via Outlook Graph API")
                return "sent"  # Outlook doesn't return message ID for sent emails
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Error sending email via Outlook: {e}")
            return ""