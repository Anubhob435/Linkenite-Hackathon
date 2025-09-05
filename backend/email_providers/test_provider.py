"""
Test script for email providers.
"""
import asyncio
import os
from datetime import datetime, timedelta

from backend.email_providers import create_email_provider


async def test_imap_provider():
    """Test the IMAP email provider."""
    # For testing purposes, we'll use a public IMAP server
    # Note: This is just for demonstration and won't work with real credentials
    config = {
        "host": "imap.example.com",
        "port": 993,
        "username": "test@example.com",
        "password": "password",
        "use_ssl": True
    }
    
    try:
        provider = create_email_provider("imap", config)
        print("Created IMAP provider successfully")
        
        # Try to connect (this will fail with the dummy config)
        connected = await provider.connect()
        print(f"Connection attempt result: {connected}")
        
        if connected:
            # Fetch some emails
            since = datetime.now() - timedelta(days=7)
            emails = await provider.fetch_emails(since=since, limit=10)
            print(f"Fetched {len(emails)} emails")
            
            # Disconnect
            await provider.disconnect()
            print("Disconnected successfully")
        
    except Exception as e:
        print(f"Error testing IMAP provider: {e}")


if __name__ == "__main__":
    asyncio.run(test_imap_provider())