"""
Email providers package for handling different email services.
"""
from .base import EmailProvider, EmailMessage
from .imap import IMAPEmailProvider
from .gmail import GmailEmailProvider
from .outlook import OutlookEmailProvider
from .factory import create_email_provider, get_supported_providers
from .config import EmailProviderConfigManager, get_email_provider_config, save_email_provider_config

__all__ = [
    "EmailProvider",
    "EmailMessage",
    "IMAPEmailProvider", 
    "GmailEmailProvider",
    "OutlookEmailProvider",
    "create_email_provider",
    "get_supported_providers",
    "EmailProviderConfigManager",
    "get_email_provider_config",
    "save_email_provider_config"
]