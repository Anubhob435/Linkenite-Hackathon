"""
Email provider factory for creating provider instances.
"""
from typing import Dict, Any
from backend.email_providers.base import EmailProvider
from backend.email_providers.imap import IMAPEmailProvider
from backend.email_providers.gmail import GmailEmailProvider
from backend.email_providers.outlook import OutlookEmailProvider


def create_email_provider(provider_type: str, config: Dict[str, Any]) -> EmailProvider:
    """Create an email provider instance based on the provider type.
    
    Args:
        provider_type: The type of provider to create (imap, gmail, outlook)
        config: Configuration dictionary for the provider
        
    Returns:
        EmailProvider instance
        
    Raises:
        ValueError: If the provider type is not supported
    """
    if provider_type.lower() == "imap":
        return IMAPEmailProvider(
            host=config.get("host"),
            port=config.get("port", 993),
            username=config.get("username"),
            password=config.get("password"),
            use_ssl=config.get("use_ssl", True)
        )
    elif provider_type.lower() == "gmail":
        return GmailEmailProvider(
            client_id=config.get("client_id"),
            client_secret=config.get("client_secret"),
            refresh_token=config.get("refresh_token"),
            access_token=config.get("access_token")
        )
    elif provider_type.lower() == "outlook":
        return OutlookEmailProvider(
            client_id=config.get("client_id"),
            client_secret=config.get("client_secret"),
            refresh_token=config.get("refresh_token"),
            access_token=config.get("access_token"),
            tenant_id=config.get("tenant_id", "common")
        )
    else:
        raise ValueError(f"Unsupported email provider type: {provider_type}")


def get_supported_providers() -> Dict[str, Dict[str, Any]]:
    """Get information about supported email providers.
    
    Returns:
        Dictionary with provider information
    """
    return {
        "imap": {
            "name": "IMAP",
            "description": "Generic IMAP email server",
            "auth_type": "basic",
            "required_fields": ["host", "port", "username", "password"],
            "optional_fields": ["use_ssl"]
        },
        "gmail": {
            "name": "Gmail",
            "description": "Google Gmail via API",
            "auth_type": "oauth2",
            "required_fields": ["client_id", "client_secret"],
            "optional_fields": ["refresh_token", "access_token"]
        },
        "outlook": {
            "name": "Outlook",
            "description": "Microsoft Outlook via Graph API",
            "auth_type": "oauth2",
            "required_fields": ["client_id", "client_secret"],
            "optional_fields": ["refresh_token", "access_token", "tenant_id"]
        }
    }