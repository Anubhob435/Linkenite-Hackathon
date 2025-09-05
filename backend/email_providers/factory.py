"""
Email provider factory for creating provider instances.
"""
from typing import Dict, Any
from backend.email_providers.base import EmailProvider
from backend.email_providers.imap import IMAPEmailProvider


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
        # For Gmail, we would use the Gmail API
        raise NotImplementedError("Gmail provider not yet implemented")
    elif provider_type.lower() == "outlook":
        # For Outlook, we would use the Outlook Graph API
        raise NotImplementedError("Outlook provider not yet implemented")
    else:
        raise ValueError(f"Unsupported email provider type: {provider_type}")