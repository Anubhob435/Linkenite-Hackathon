"""
Unit tests for email provider authentication and connection.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

from backend.email_providers.base import EmailProvider, EmailMessage
from backend.email_providers.imap import IMAPEmailProvider
from backend.email_providers.gmail import GmailEmailProvider
from backend.email_providers.outlook import OutlookEmailProvider
from backend.email_providers.factory import create_email_provider, get_supported_providers
from backend.email_providers.config import EmailProviderConfigManager


class TestEmailMessage:
    """Test cases for EmailMessage class."""
    
    def test_email_message_creation(self):
        """Test creating an EmailMessage instance."""
        received_at = datetime.now()
        
        email = EmailMessage(
            message_id="test-123",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            subject="Test Subject",
            body="Test body content",
            received_at=received_at,
            raw_data={"test": "data"}
        )
        
        assert email.message_id == "test-123"
        assert email.sender == "sender@example.com"
        assert email.recipients == ["recipient@example.com"]
        assert email.subject == "Test Subject"
        assert email.body == "Test body content"
        assert email.received_at == received_at
        assert email.raw_data == {"test": "data"}
    
    def test_email_message_default_raw_data(self):
        """Test EmailMessage with default raw_data."""
        email = EmailMessage(
            message_id="test-123",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            subject="Test Subject",
            body="Test body content",
            received_at=datetime.now()
        )
        
        assert email.raw_data == {}


class TestIMAPEmailProvider:
    """Test cases for IMAP email provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = IMAPEmailProvider(
            host="imap.example.com",
            port=993,
            username="test@example.com",
            password="password",
            use_ssl=True
        )
    
    @pytest.mark.asyncio
    @patch('imaplib.IMAP4_SSL')
    async def test_connect_success(self, mock_imap):
        """Test successful IMAP connection."""
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        mock_connection.login.return_value = None
        
        result = await self.provider.connect()
        
        assert result is True
        mock_imap.assert_called_once_with("imap.example.com", 993)
        mock_connection.login.assert_called_once_with("test@example.com", "password")
    
    @pytest.mark.asyncio
    @patch('imaplib.IMAP4_SSL')
    async def test_connect_failure(self, mock_imap):
        """Test IMAP connection failure."""
        mock_imap.side_effect = Exception("Connection failed")
        
        result = await self.provider.connect()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_disconnect_success(self):
        """Test successful IMAP disconnection."""
        mock_connection = Mock()
        self.provider.connection = mock_connection
        
        result = await self.provider.disconnect()
        
        assert result is True
        mock_connection.close.assert_called_once()
        mock_connection.logout.assert_called_once()
        assert self.provider.connection is None
    
    @pytest.mark.asyncio
    @patch('imaplib.IMAP4_SSL')
    async def test_fetch_emails(self, mock_imap):
        """Test fetching emails from IMAP."""
        # Mock IMAP connection and responses
        mock_connection = Mock()
        mock_imap.return_value = mock_connection
        mock_connection.login.return_value = None
        mock_connection.select.return_value = ("OK", None)
        mock_connection.search.return_value = ("OK", [b"1 2 3"])
        
        # Mock email fetch response
        mock_email_data = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Subject
Date: Mon, 01 Jan 2024 12:00:00 +0000

Test email body"""
        
        mock_connection.fetch.return_value = ("OK", [(None, mock_email_data)])
        
        self.provider.connection = mock_connection
        
        emails = await self.provider.fetch_emails()
        
        assert len(emails) == 3  # Should process 3 emails
        mock_connection.select.assert_called_once_with("INBOX")
        mock_connection.search.assert_called_once_with(None, "ALL")


class TestGmailEmailProvider:
    """Test cases for Gmail email provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = GmailEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token"
        )
    
    @pytest.mark.asyncio
    @patch('backend.email_providers.gmail.build')
    @patch('backend.email_providers.gmail.Credentials')
    @patch('backend.email_providers.gmail.Request')
    async def test_connect_success(self, mock_request, mock_credentials, mock_build):
        """Test successful Gmail API connection."""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_credentials.return_value = mock_creds
        
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        result = await self.provider.connect()
        
        assert result is True
        assert self.provider.service == mock_service
    
    @pytest.mark.asyncio
    @patch('backend.email_providers.gmail.Credentials')
    async def test_connect_invalid_credentials(self, mock_credentials):
        """Test Gmail connection with invalid credentials."""
        mock_creds = Mock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = None
        mock_credentials.return_value = mock_creds
        
        result = await self.provider.connect()
        
        assert result is False
    
    def test_get_auth_url(self):
        """Test getting Gmail OAuth2 authorization URL."""
        with patch('backend.email_providers.gmail.Flow') as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            mock_flow_instance.authorization_url.return_value = ("https://auth.url", "state")
            
            auth_url = self.provider.get_auth_url("http://localhost/callback")
            
            assert auth_url == "https://auth.url"
            mock_flow_instance.authorization_url.assert_called_once()
    
    def test_exchange_code_for_tokens(self):
        """Test exchanging authorization code for tokens."""
        with patch('backend.email_providers.gmail.Flow') as mock_flow:
            mock_flow_instance = Mock()
            mock_flow.from_client_config.return_value = mock_flow_instance
            
            mock_credentials = Mock()
            mock_credentials.token = "access_token"
            mock_credentials.refresh_token = "refresh_token"
            mock_flow_instance.credentials = mock_credentials
            
            tokens = self.provider.exchange_code_for_tokens("auth_code", "http://localhost/callback")
            
            assert tokens["access_token"] == "access_token"
            assert tokens["refresh_token"] == "refresh_token"
            mock_flow_instance.fetch_token.assert_called_once_with(code="auth_code")


class TestOutlookEmailProvider:
    """Test cases for Outlook email provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = OutlookEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret",
            refresh_token="test_refresh_token"
        )
    
    @pytest.mark.asyncio
    @patch('backend.email_providers.outlook.msal.ConfidentialClientApplication')
    async def test_connect_success(self, mock_msal):
        """Test successful Outlook Graph API connection."""
        mock_app = Mock()
        mock_msal.return_value = mock_app
        mock_app.acquire_token_by_refresh_token.return_value = {
            "access_token": "test_access_token"
        }
        
        result = await self.provider.connect()
        
        assert result is True
        assert self.provider.access_token == "test_access_token"
        assert "Authorization" in self.provider.headers
    
    @pytest.mark.asyncio
    @patch('backend.email_providers.outlook.msal.ConfidentialClientApplication')
    async def test_connect_failure(self, mock_msal):
        """Test Outlook connection failure."""
        mock_app = Mock()
        mock_msal.return_value = mock_app
        mock_app.acquire_token_by_refresh_token.return_value = {
            "error": "invalid_grant",
            "error_description": "Token expired"
        }
        
        result = await self.provider.connect()
        
        assert result is False
    
    @pytest.mark.asyncio
    @patch('backend.email_providers.outlook.requests.get')
    async def test_fetch_emails(self, mock_get):
        """Test fetching emails from Outlook."""
        self.provider.headers = {"Authorization": "Bearer test_token"}
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "id": "message_1",
                    "internetMessageId": "msg_1@example.com",
                    "subject": "Test Subject",
                    "from": {"emailAddress": {"address": "sender@example.com"}},
                    "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
                    "receivedDateTime": "2024-01-01T12:00:00Z",
                    "body": {"content": "Test body"},
                    "isRead": False
                }
            ]
        }
        mock_get.return_value = mock_response
        
        emails = await self.provider.fetch_emails()
        
        assert len(emails) == 1
        assert emails[0].subject == "Test Subject"
        assert emails[0].sender == "sender@example.com"


class TestEmailProviderFactory:
    """Test cases for email provider factory."""
    
    def test_create_imap_provider(self):
        """Test creating IMAP provider."""
        config = {
            "host": "imap.example.com",
            "port": 993,
            "username": "test@example.com",
            "password": "password",
            "use_ssl": True
        }
        
        provider = create_email_provider("imap", config)
        
        assert isinstance(provider, IMAPEmailProvider)
        assert provider.host == "imap.example.com"
        assert provider.port == 993
    
    def test_create_gmail_provider(self):
        """Test creating Gmail provider."""
        config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token"
        }
        
        provider = create_email_provider("gmail", config)
        
        assert isinstance(provider, GmailEmailProvider)
        assert provider.client_id == "test_client_id"
        assert provider.client_secret == "test_client_secret"
    
    def test_create_outlook_provider(self):
        """Test creating Outlook provider."""
        config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "tenant_id": "common"
        }
        
        provider = create_email_provider("outlook", config)
        
        assert isinstance(provider, OutlookEmailProvider)
        assert provider.client_id == "test_client_id"
        assert provider.tenant_id == "common"
    
    def test_create_unsupported_provider(self):
        """Test creating unsupported provider type."""
        with pytest.raises(ValueError, match="Unsupported email provider type"):
            create_email_provider("unsupported", {})
    
    def test_get_supported_providers(self):
        """Test getting supported provider information."""
        providers = get_supported_providers()
        
        assert "imap" in providers
        assert "gmail" in providers
        assert "outlook" in providers
        
        assert providers["imap"]["auth_type"] == "basic"
        assert providers["gmail"]["auth_type"] == "oauth2"
        assert providers["outlook"]["auth_type"] == "oauth2"


class TestEmailProviderConfigManager:
    """Test cases for email provider configuration manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = EmailProviderConfigManager()
    
    def test_encrypt_decrypt_sensitive_data(self):
        """Test encryption and decryption of sensitive data."""
        original_data = "sensitive_password_123"
        
        encrypted = self.config_manager.encrypt_sensitive_data(original_data)
        decrypted = self.config_manager.decrypt_sensitive_data(encrypted)
        
        assert encrypted != original_data
        assert decrypted == original_data
    
    @patch('backend.email_providers.config.get_db')
    def test_get_email_provider_config_from_db(self, mock_get_db):
        """Test getting email provider config from database."""
        # Mock database session and query
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        mock_config = Mock()
        mock_config.configuration = '{"host": "imap.example.com", "port": 993}'
        mock_config.provider_type = "imap"
        mock_config.is_active = True
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_config
        mock_db.query.return_value = mock_query
        
        config = self.config_manager.get_email_provider_config("imap")
        
        assert config is not None
        assert config["host"] == "imap.example.com"
        assert config["port"] == 993
    
    @patch('backend.email_providers.config.get_db')
    def test_save_email_provider_config(self, mock_get_db):
        """Test saving email provider configuration."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        config = {
            "host": "imap.example.com",
            "port": 993,
            "username": "test@example.com",
            "password": "secret_password"
        }
        
        result = self.config_manager.save_email_provider_config("imap", config)
        
        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('backend.email_providers.config.get_db')
    def test_list_email_provider_configs(self, mock_get_db):
        """Test listing email provider configurations."""
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        mock_config = Mock()
        mock_config.id = "test-id"
        mock_config.provider_type = "imap"
        mock_config.configuration = '{"host": "imap.example.com", "password": "secret"}'
        mock_config.is_active = True
        mock_config.created_at = datetime.now()
        mock_config.updated_at = None
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_config]
        mock_db.query.return_value = mock_query
        
        configs = self.config_manager.list_email_provider_configs()
        
        assert len(configs) == 1
        assert configs[0]["id"] == "test-id"
        assert configs[0]["provider_type"] == "imap"
        # Sensitive fields should be masked
        assert configs[0]["configuration"]["password"] == "***"


@pytest.mark.asyncio
class TestEmailProviderIntegration:
    """Integration tests for email providers."""
    
    async def test_imap_provider_workflow(self):
        """Test complete IMAP provider workflow."""
        provider = IMAPEmailProvider(
            host="imap.example.com",
            port=993,
            username="test@example.com",
            password="password"
        )
        
        # Test connection (will fail in test environment, but should handle gracefully)
        result = await provider.connect()
        assert result is False  # Expected to fail without real server
        
        # Test disconnection
        result = await provider.disconnect()
        assert result is True
    
    async def test_gmail_provider_workflow(self):
        """Test Gmail provider workflow without real credentials."""
        provider = GmailEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Test connection without refresh token
        result = await provider.connect()
        assert result is False  # Expected to fail without refresh token
        
        # Test disconnection
        result = await provider.disconnect()
        assert result is True
    
    async def test_outlook_provider_workflow(self):
        """Test Outlook provider workflow without real credentials."""
        provider = OutlookEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Test connection without refresh token
        result = await provider.connect()
        assert result is False  # Expected to fail without refresh token
        
        # Test disconnection
        result = await provider.disconnect()
        assert result is True