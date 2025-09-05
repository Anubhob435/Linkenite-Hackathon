"""
Demonstration script for email provider functionality.
"""
import asyncio
from typing import Dict, Any

from backend.email_providers import (
    create_email_provider,
    get_supported_providers,
    EmailProviderConfigManager
)


async def demo_email_providers():
    """Demonstrate email provider functionality."""
    print("=== Email Provider Integration Foundation Demo ===\n")
    
    # Show supported providers
    print("1. Supported Email Providers:")
    providers = get_supported_providers()
    for provider_type, info in providers.items():
        print(f"   - {info['name']}: {info['description']}")
        print(f"     Auth Type: {info['auth_type']}")
        print(f"     Required Fields: {', '.join(info['required_fields'])}")
        print(f"     Optional Fields: {', '.join(info['optional_fields'])}")
        print()
    
    # Demo provider creation
    print("2. Creating Email Provider Instances:")
    
    # IMAP Provider
    print("   Creating IMAP Provider...")
    try:
        imap_config = {
            "host": "imap.example.com",
            "port": 993,
            "username": "demo@example.com",
            "password": "demo_password",
            "use_ssl": True
        }
        imap_provider = create_email_provider("imap", imap_config)
        print(f"   ✓ IMAP Provider created: {type(imap_provider).__name__}")
        
        # Test connection (will fail without real server)
        print("   Testing IMAP connection...")
        result = await imap_provider.connect()
        print(f"   Connection result: {result} (expected to fail in demo)")
        
        # Test disconnection
        result = await imap_provider.disconnect()
        print(f"   Disconnection result: {result}")
        
    except Exception as e:
        print(f"   ✗ IMAP Provider error: {e}")
    
    print()
    
    # Gmail Provider
    print("   Creating Gmail Provider...")
    try:
        gmail_config = {
            "client_id": "demo_client_id",
            "client_secret": "demo_client_secret"
        }
        gmail_provider = create_email_provider("gmail", gmail_config)
        print(f"   ✓ Gmail Provider created: {type(gmail_provider).__name__}")
        
        # Show OAuth2 URL generation
        auth_url = gmail_provider.get_auth_url("http://localhost:8000/callback")
        print(f"   OAuth2 Auth URL: {auth_url[:50]}...")
        
        # Test connection (will fail without real credentials)
        print("   Testing Gmail connection...")
        result = await gmail_provider.connect()
        print(f"   Connection result: {result} (expected to fail in demo)")
        
        result = await gmail_provider.disconnect()
        print(f"   Disconnection result: {result}")
        
    except Exception as e:
        print(f"   ✗ Gmail Provider error: {e}")
    
    print()
    
    # Outlook Provider
    print("   Creating Outlook Provider...")
    try:
        outlook_config = {
            "client_id": "demo_client_id",
            "client_secret": "demo_client_secret",
            "tenant_id": "common"
        }
        outlook_provider = create_email_provider("outlook", outlook_config)
        print(f"   ✓ Outlook Provider created: {type(outlook_provider).__name__}")
        
        # Show OAuth2 URL generation
        auth_url = outlook_provider.get_auth_url("http://localhost:8000/callback")
        print(f"   OAuth2 Auth URL: {auth_url[:50]}...")
        
        # Test connection (will fail without real credentials)
        print("   Testing Outlook connection...")
        result = await outlook_provider.connect()
        print(f"   Connection result: {result} (expected to fail in demo)")
        
        result = await outlook_provider.disconnect()
        print(f"   Disconnection result: {result}")
        
    except Exception as e:
        print(f"   ✗ Outlook Provider error: {e}")
    
    print()
    
    # Demo configuration management
    print("3. Configuration Management:")
    config_manager = EmailProviderConfigManager()
    
    print("   Testing encryption/decryption...")
    sensitive_data = "super_secret_password_123"
    encrypted = config_manager.encrypt_sensitive_data(sensitive_data)
    decrypted = config_manager.decrypt_sensitive_data(encrypted)
    
    print(f"   Original: {sensitive_data}")
    print(f"   Encrypted: {encrypted[:20]}...")
    print(f"   Decrypted: {decrypted}")
    print(f"   Encryption working: {sensitive_data == decrypted}")
    
    print()
    
    # Demo error handling
    print("4. Error Handling:")
    
    # Test invalid provider type
    try:
        create_email_provider("invalid_provider", {})
    except ValueError as e:
        print(f"   ✓ Invalid provider type handled: {e}")
    
    # Test missing required fields
    try:
        create_email_provider("imap", {})
    except ValueError as e:
        print(f"   ✓ Missing required fields handled: {e}")
    
    print()
    print("=== Demo Complete ===")
    print("\nThe email provider integration foundation is ready!")
    print("Next steps:")
    print("- Configure real OAuth2 credentials for Gmail/Outlook")
    print("- Set up IMAP server details for IMAP provider")
    print("- Integrate with the email retrieval service")
    print("- Add provider configurations to the database")


if __name__ == "__main__":
    asyncio.run(demo_email_providers())