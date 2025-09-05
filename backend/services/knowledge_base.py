"""
Knowledge base and vector storage system.
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from backend.models.knowledge import KnowledgeItem
from backend.core.database import get_db

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Knowledge base management system."""
    
    def __init__(self):
        self.items = []
    
    def add_item(self, title: str, content: str, category: str = None, tags: List[str] = None) -> str:
        """Add a new item to the knowledge base.
        
        Args:
            title: Title of the knowledge item
            content: Content of the knowledge item
            category: Category of the knowledge item
            tags: List of tags for the knowledge item
            
        Returns:
            ID of the created item
        """
        item_id = str(uuid.uuid4())
        
        item = KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )
        
        self.items.append(item)
        logger.info(f"Added knowledge item: {title}")
        return item_id
    
    def search_items(self, query: str, category: str = None, limit: int = 10) -> List[KnowledgeItem]:
        """Search for knowledge items.
        
        Args:
            query: Search query
            category: Category to filter by
            limit: Maximum number of items to return
            
        Returns:
            List of matching KnowledgeItem objects
        """
        results = []
        query_lower = query.lower()
        
        for item in self.items:
            # Check if item matches category filter
            if category and item.category != category:
                continue
            
            # Check if query matches title or content
            if (query_lower in item.title.lower() or 
                query_lower in item.content.lower() or
                any(query_lower in tag.lower() for tag in item.tags)):
                results.append(item)
        
        # Sort by relevance (simplified - in a real implementation, we would use embeddings)
        results.sort(key=lambda x: len(query_lower) / len(x.title + x.content), reverse=True)
        
        return results[:limit]
    
    def get_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Get a specific knowledge item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            KnowledgeItem object or None if not found
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def update_item(self, item_id: str, title: str = None, content: str = None, 
                   category: str = None, tags: List[str] = None) -> bool:
        """Update a knowledge item.
        
        Args:
            item_id: ID of the item to update
            title: New title (optional)
            content: New content (optional)
            category: New category (optional)
            tags: New tags (optional)
            
        Returns:
            True if successful, False if item not found
        """
        item = self.get_item(item_id)
        if not item:
            return False
        
        if title is not None:
            item.title = title
        if content is not None:
            item.content = content
        if category is not None:
            item.category = category
        if tags is not None:
            item.tags = tags
        
        logger.info(f"Updated knowledge item: {item_id}")
        return True
    
    def delete_item(self, item_id: str) -> bool:
        """Delete a knowledge item.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if successful, False if item not found
        """
        item = self.get_item(item_id)
        if not item:
            return False
        
        self.items.remove(item)
        logger.info(f"Deleted knowledge item: {item_id}")
        return True
    
    def get_categories(self) -> List[str]:
        """Get all unique categories in the knowledge base.
        
        Returns:
            List of unique categories
        """
        categories = set(item.category for item in self.items if item.category)
        return list(categories)
    
    def get_tags(self) -> List[str]:
        """Get all unique tags in the knowledge base.
        
        Returns:
            List of unique tags
        """
        tags = set()
        for item in self.items:
            tags.update(item.tags)
        return list(tags)


# Example usage
def example_usage():
    """Example usage of the KnowledgeBase."""
    kb = KnowledgeBase()
    
    # Add some sample knowledge items
    kb.add_item(
        title="Account Verification Process",
        content="To verify your account, please check your email for a verification link. Click the link to complete the verification process.",
        category="Account Management",
        tags=["verification", "account", "email"]
    )
    
    kb.add_item(
        title="Password Reset",
        content="If you've forgotten your password, click 'Forgot Password' on the login page and follow the instructions sent to your email.",
        category="Account Management",
        tags=["password", "reset", "account"]
    )
    
    kb.add_item(
        title="Billing Issues",
        content="For billing issues, please contact our billing department at billing@company.com or call 1-800-123-4567.",
        category="Billing",
        tags=["billing", "payment", "invoice"]
    )
    
    # Search for items
    results = kb.search_items("password")
    print(f"Found {len(results)} items for 'password' query")
    
    # Get categories and tags
    categories = kb.get_categories()
    tags = kb.get_tags()
    print(f"Categories: {categories}")
    print(f"Tags: {tags}")


if __name__ == "__main__":
    example_usage()