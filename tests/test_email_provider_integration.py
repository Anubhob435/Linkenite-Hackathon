"""
Integration tests for email provider functionality.
"""
import pytest
from backend.email_providers import (
    create_email_provider, 
    get_supported_providers,
    IMAPEmailProvider,
    GmailEmailProvider,
    OutlookEmailProvider
)


class TestEmailProviderIntegration:
    """Integration tests for email providers."""
    
    def test_supported_providers_info(self):
        """Test that all supported providers return proper information."""
        providers = get_supported_providers()
        
        # Check that all expected providers are present
        assert "imap" in providers
        assert "gmail" in providers
        assert "outlook" in providers
        
        # Check provider information structure
        for provider_type, info in providers.items():
            assert "name" in info
            assert "description" in info
            assert "auth_type" in info
            assert "required_fields" in info
            assert "optional_fields" in info
            
            # Verify auth types
            if provider_type == "imap":
                assert info["auth_type"] == "basic"
            else:
                assert info["auth_type"] == "oauth2"
    
    def test_create_all_provider_types(self):
        """Test creating instances of all provider types."""
        # Test IMAP provider
        imap_config = {
            "host": "imap.example.com",
            "port": 993,
            "username": "test@example.com",
            "password": "password",
            "use_ssl": True
        }
        imap_provider = create_email_provider("imap", imap_config)
        assert isinstance(imap_provider, IMAPEmailProvider)
        
        # Test Gmail provider
        gmail_config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token"
        }
        gmail_provider = create_email_provider("gmail", gmail_config)
        assert isinstance(gmail_provider, GmailEmailProvider)
        
        # Test Outlook provider
        outlook_config = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "tenant_id": "common"
        }
        outlook_provider = create_email_provider("outlook", outlook_config)
        assert isinstance(outlook_provider, OutlookEmailProvider)
    
    @pytest.mark.asyncio
    async def test_provider_lifecycle(self):
        """Test the basic lifecycle of email providers."""
        configs = {
            "imap": {
                "host": "imap.example.com",
                "port": 993,
                "username": "test@example.com",
                "password": "password",
                "use_ssl": True
            },
            "gmail": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            },
            "outlook": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            }
        }
        
        for provider_type, config in configs.items():
            provider = create_email_provider(provider_type, config)
            
            # Test connection (expected to fail without real credentials)
            connect_result = await provider.connect()
            # We expect these to fail in test environment
            assert connect_result is False
            
            # Test disconnection (should always succeed)
            disconnect_result = await provider.disconnect()
            assert disconnect_result is True
    
    def test_oauth2_provider_methods(self):
        """Test OAuth2-specific methods for Gmail and Outlook providers."""
        # Test Gmail OAuth2 methods
        gmail_provider = GmailEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Should have OAuth2 methods
        assert hasattr(gmail_provider, 'get_auth_url')
        assert hasattr(gmail_provider, 'exchange_code_for_tokens')
        
        # Test Outlook OAuth2 methods
        outlook_provider = OutlookEmailProvider(
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Should have OAuth2 methods
        assert hasattr(outlook_provider, 'get_auth_url')
        assert hasattr(outlook_provider, 'exchange_code_for_tokens')
    
    def test_provider_configuration_validation(self):
        """Test that providers validate their configuration properly."""
        # Test missing required fields
        with pytest.raises((ValueError, TypeError)):
            create_email_provider("imap", {})  # Missing required fields
        
        # Test invalid provider type
        with pytest.raises(ValueError):
            create_email_provider("invalid_provider", {})
    
    def test_provider_interface_compliance(self):
        """Test that all providers implement the required interface."""
        providers = [
            create_email_provider("imap", {
                "host": "imap.example.com",
                "port": 993,
                "username": "test@example.com",
                "password": "password"
            }),
            create_email_provider("gmail", {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            }),
            create_email_provider("outlook", {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            })
        ]
        
        # Check that all providers implement required methods
        required_methods = [
            'connect', 'disconnect', 'fetch_emails', 
            'mark_as_read', 'send_email'
        ]
        
        for provider in providers:
            for method_name in required_methods:
                assert hasattr(provider, method_name)
                assert callable(getattr(provider, method_name))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])