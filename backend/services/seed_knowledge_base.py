"""
Script to seed the knowledge base with common support issues.
"""
import sys
import os
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.knowledge_base import KnowledgeBase


def seed_knowledge_base():
    """Seed the knowledge base with common support issues."""
    kb = KnowledgeBase()
    
    # Read the CSV file to identify common issues
    csv_path = "68b1acd44f393_Sample_Support_Emails_Dataset.csv"
    if not os.path.exists(csv_path):
        print(f"CSV file {csv_path} not found")
        return
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} emails from CSV")
    
    # Identify common issues and create knowledge base entries
    common_issues = [
        {
            "title": "Account Login Issues",
            "content": "If you're unable to log into your account, try resetting your password. Click 'Forgot Password' on the login page and follow the instructions sent to your email. If you continue to experience issues, please contact our support team.",
            "category": "Account Management",
            "tags": ["login", "account", "password", "access"]
        },
        {
            "title": "Password Reset Process",
            "content": "To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your email address, 3) Check your email for a password reset link, 4) Click the link and enter a new password, 5) Confirm your new password. The link expires in 24 hours.",
            "category": "Account Management",
            "tags": ["password", "reset", "account", "security"]
        },
        {
            "title": "Account Verification",
            "content": "After creating an account, you'll receive a verification email. Click the verification link in the email to activate your account. If you don't see the email, check your spam folder. Verification links expire in 48 hours.",
            "category": "Account Management",
            "tags": ["verification", "account", "email", "activation"]
        },
        {
            "title": "Billing and Payment Issues",
            "content": "For billing questions or payment issues, contact our billing department at billing@company.com or call 1-800-123-4567. Include your account number and a description of the issue in your communication. Our billing team is available Monday-Friday, 9AM-5PM EST.",
            "category": "Billing",
            "tags": ["billing", "payment", "invoice", "charge"]
        },
        {
            "title": "System Downtime and Outages",
            "content": "We strive for 99.9% uptime. If you're experiencing system issues, check our status page at status.company.com for current outages. For urgent issues, contact support with details about the problem, including error messages and the time it occurred.",
            "category": "Technical Support",
            "tags": ["downtime", "outage", "system", "error"]
        },
        {
            "title": "API Integration Support",
            "content": "For API integration questions, refer to our developer documentation at docs.company.com. Common integration issues include authentication errors, rate limiting, and incorrect endpoint usage. Ensure you're using the latest API version and valid API keys.",
            "category": "Developer Support",
            "tags": ["api", "integration", "developer", "documentation"]
        },
        {
            "title": "Subscription and Pricing Questions",
            "content": "For questions about pricing, plans, or subscription changes, visit our pricing page or contact our sales team at sales@company.com. Current subscribers can upgrade, downgrade, or cancel their subscriptions through the account settings page.",
            "category": "Sales",
            "tags": ["subscription", "pricing", "plan", "upgrade"]
        },
        {
            "title": "Refund Policy",
            "content": "We offer a 30-day money-back guarantee for new subscriptions. To request a refund, contact billing@company.com with your account details and reason for the refund request. Refund requests are typically processed within 5-7 business days.",
            "category": "Billing",
            "tags": ["refund", "money-back", "guarantee", "policy"]
        }
    ]
    
    # Add common issues to knowledge base
    print(f"Adding {len(common_issues)} common issues to knowledge base...")
    for issue in common_issues:
        kb.add_item(
            title=issue["title"],
            content=issue["content"],
            category=issue["category"],
            tags=issue["tags"]
        )
    
    print(f"Knowledge base seeded with {len(kb.items)} items")
    
    # Save to database (in a real implementation, we would save to the database)
    print("In a real implementation, these items would be saved to the database")
    
    # Example search
    print("\nExample searches:")
    results = kb.search_items("password")
    print(f"Search for 'password': {len(results)} results")
    
    results = kb.search_items("billing")
    print(f"Search for 'billing': {len(results)} results")


if __name__ == "__main__":
    seed_knowledge_base()