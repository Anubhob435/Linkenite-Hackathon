"""
Test script for knowledge base.
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.knowledge_base import KnowledgeBase


def test_knowledge_base():
    """Test the knowledge base system."""
    kb = KnowledgeBase()
    
    print("Testing Knowledge Base System")
    print("=" * 30)
    
    # Add some sample knowledge items
    print("\n1. Adding knowledge items...")
    item1_id = kb.add_item(
        title="Account Verification Process",
        content="To verify your account, please check your email for a verification link. Click the link to complete the verification process.",
        category="Account Management",
        tags=["verification", "account", "email"]
    )
    print(f"Added item 1 with ID: {item1_id}")
    
    item2_id = kb.add_item(
        title="Password Reset",
        content="If you've forgotten your password, click 'Forgot Password' on the login page and follow the instructions sent to your email.",
        category="Account Management",
        tags=["password", "reset", "account"]
    )
    print(f"Added item 2 with ID: {item2_id}")
    
    item3_id = kb.add_item(
        title="Billing Issues",
        content="For billing issues, please contact our billing department at billing@company.com or call 1-800-123-4567.",
        category="Billing",
        tags=["billing", "payment", "invoice"]
    )
    print(f"Added item 3 with ID: {item3_id}")
    
    # Search for items
    print("\n2. Searching for items...")
    results = kb.search_items("password")
    print(f"Found {len(results)} items for 'password' query")
    for item in results:
        print(f"  - {item.title}")
    
    results = kb.search_items("billing", category="Billing")
    print(f"Found {len(results)} billing items")
    for item in results:
        print(f"  - {item.title}")
    
    # Get item by ID
    print("\n3. Retrieving item by ID...")
    item = kb.get_item(item1_id)
    if item:
        print(f"Retrieved item: {item.title}")
        print(f"Content: {item.content[:50]}...")
    
    # Update item
    print("\n4. Updating item...")
    success = kb.update_item(item1_id, title="Updated Account Verification Process")
    print(f"Update successful: {success}")
    
    # Get categories and tags
    print("\n5. Getting categories and tags...")
    categories = kb.get_categories()
    tags = kb.get_tags()
    print(f"Categories: {categories}")
    print(f"Tags: {tags}")
    
    # Delete item
    print("\n6. Deleting item...")
    success = kb.delete_item(item2_id)
    print(f"Delete successful: {success}")
    
    # Check remaining items
    print(f"\n7. Remaining items: {len(kb.items)}")


if __name__ == "__main__":
    test_knowledge_base()