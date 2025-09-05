"""
Configuration management for email providers.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from datetime import datetime
import json
import logging

from backend.core.config import settings
from backend.core.database import get_db
from backend.models.provider import EmailProvider as EmailProviderConfig

logger = logging.getLogger(__name__)


class EmailProviderConfigManager:
    """Manages email provider configurations with encryption."""
    
    def __init__(self):
        # In production, this should be stored securely (e.g., environment variable)
        self.encryption_key = settings.SECRET_KEY.encode()[:32].ljust(32, b'0')
        self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive configuration data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive configuration data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def get_email_provider_config(self, provider_type: str, provider_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get configuration for an email provider.
        
        Args:
            provider_type: The type of provider (imap, gmail, outlook)
            provider_id: Optional specific provider ID
            
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            # Try to get from database first
            db = next(get_db())
            
            query = db.query(EmailProviderConfig).filter(
                EmailProviderConfig.provider_type == provider_type.lower()
            )
            
            if provider_id:
                query = query.filter(EmailProviderConfig.id == provider_id)
            
            provider_config = query.filter(EmailProviderConfig.is_active == True).first()
            
            if provider_config:
                config = json.loads(provider_config.configuration)
                
                # Decrypt sensitive fields
                sensitive_fields = ['password', 'refresh_token', 'access_token', 'client_secret']
                for field in sensitive_fields:
                    if field in config and config[field]:
                        try:
                            config[field] = self.decrypt_sensitive_data(config[field])
                        except Exception as e:
                            logger.warning(f"Failed to decrypt {field}: {e}")
                
                return config
            
            # Fallback to environment-based configuration
            return self._get_default_config(provider_type)
            
        except Exception as e:
            logger.error(f"Error getting email provider config: {e}")
            return self._get_default_config(provider_type)
    
    def _get_default_config(self, provider_type: str) -> Optional[Dict[str, Any]]:
        """Get default configuration from environment variables."""
        if provider_type.lower() == "imap":
            return {
                "host": "imap.example.com",
                "port": 993,
                "username": "user@example.com",
                "password": "password",
                "use_ssl": True
            }
        elif provider_type.lower() == "gmail":
            if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
                return None
            return {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "refresh_token": None,
                "access_token": None
            }
        elif provider_type.lower() == "outlook":
            if not settings.OUTLOOK_CLIENT_ID or not settings.OUTLOOK_CLIENT_SECRET:
                return None
            return {
                "client_id": settings.OUTLOOK_CLIENT_ID,
                "client_secret": settings.OUTLOOK_CLIENT_SECRET,
                "refresh_token": None,
                "access_token": None,
                "tenant_id": "common"
            }
        
        return None
    
    def save_email_provider_config(self, 
                                  provider_type: str, 
                                  config: Dict[str, Any],
                                  provider_id: Optional[str] = None) -> bool:
        """Save configuration for an email provider.
        
        Args:
            provider_type: The type of provider (imap, gmail, outlook)
            config: Configuration dictionary to save
            provider_id: Optional specific provider ID to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = next(get_db())
            
            # Encrypt sensitive fields
            config_copy = config.copy()
            sensitive_fields = ['password', 'refresh_token', 'access_token', 'client_secret']
            
            for field in sensitive_fields:
                if field in config_copy and config_copy[field]:
                    config_copy[field] = self.encrypt_sensitive_data(config_copy[field])
            
            if provider_id:
                # Update existing configuration
                provider_config = db.query(EmailProviderConfig).filter(
                    EmailProviderConfig.id == provider_id
                ).first()
                
                if provider_config:
                    provider_config.configuration = json.dumps(config_copy)
                    provider_config.updated_at = datetime.utcnow()
                else:
                    logger.error(f"Provider config with ID {provider_id} not found")
                    return False
            else:
                # Create new configuration
                provider_config = EmailProviderConfig(
                    provider_type=provider_type.lower(),
                    configuration=json.dumps(config_copy),
                    is_active=True
                )
                db.add(provider_config)
            
            db.commit()
            logger.info(f"Saved configuration for {provider_type} provider")
            return True
            
        except Exception as e:
            logger.error(f"Error saving email provider config: {e}")
            if 'db' in locals():
                db.rollback()
            return False
    
    def delete_email_provider_config(self, provider_id: str) -> bool:
        """Delete an email provider configuration.
        
        Args:
            provider_id: The provider ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db = next(get_db())
            
            provider_config = db.query(EmailProviderConfig).filter(
                EmailProviderConfig.id == provider_id
            ).first()
            
            if provider_config:
                provider_config.is_active = False
                db.commit()
                logger.info(f"Deleted provider config {provider_id}")
                return True
            else:
                logger.warning(f"Provider config {provider_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting email provider config: {e}")
            if 'db' in locals():
                db.rollback()
            return False
    
    def list_email_provider_configs(self, provider_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all email provider configurations.
        
        Args:
            provider_type: Optional filter by provider type
            
        Returns:
            List of provider configurations (without sensitive data)
        """
        try:
            db = next(get_db())
            
            query = db.query(EmailProviderConfig).filter(
                EmailProviderConfig.is_active == True
            )
            
            if provider_type:
                query = query.filter(EmailProviderConfig.provider_type == provider_type.lower())
            
            configs = query.all()
            
            result = []
            for config in configs:
                config_data = json.loads(config.configuration)
                
                # Remove sensitive fields from response
                sensitive_fields = ['password', 'refresh_token', 'access_token', 'client_secret']
                for field in sensitive_fields:
                    if field in config_data:
                        config_data[field] = "***" if config_data[field] else None
                
                result.append({
                    "id": str(config.id),
                    "provider_type": config.provider_type,
                    "configuration": config_data,
                    "is_active": config.is_active,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing email provider configs: {e}")
            return []


# Global instance
config_manager = EmailProviderConfigManager()

# Convenience functions for backward compatibility
def get_email_provider_config(provider_type: str) -> Optional[Dict[str, Any]]:
    """Get configuration for an email provider from settings."""
    return config_manager.get_email_provider_config(provider_type)


def save_email_provider_config(provider_type: str, config: Dict[str, Any]) -> bool:
    """Save configuration for an email provider."""
    return config_manager.save_email_provider_config(provider_type, config)