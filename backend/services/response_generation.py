"""
Response generation with RAG pipeline.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from backend.services.knowledge_base import KnowledgeBase
from backend.services.ai_processing import SentimentType

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """Response generation system using RAG pipeline."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def generate_response(self, 
                         subject: str, 
                         body: str, 
                         sentiment: SentimentType,
                         extracted_info: Dict[str, Any] = None) -> str:
        """Generate a response for an email using RAG pipeline.
        
        Args:
            subject: Email subject
            body: Email body
            sentiment: Sentiment of the email
            extracted_info: Extracted information from the email
            
        Returns:
            Generated response content
        """
        # 1. Extract key topics from the email
        topics = self._extract_topics(subject, body)
        
        # 2. Retrieve relevant knowledge base items
        relevant_knowledge = self._retrieve_knowledge(topics)
        
        # 3. Generate response using prompt engineering
        response = self._generate_response_with_context(
            subject, body, sentiment, topics, relevant_knowledge, extracted_info
        )
        
        return response
    
    def _extract_topics(self, subject: str, body: str) -> List[str]:
        """Extract key topics from email subject and body.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            List of extracted topics
        """
        # Combine subject and body for topic extraction
        text = (subject + " " + body).lower()
        
        # Simple keyword-based topic extraction
        # In a real implementation, this would use NLP techniques
        common_topics = [
            "account", "login", "password", "verification", "billing",
            "payment", "subscription", "api", "integration", "refund",
            "access", "error", "issue", "problem", "help", "support"
        ]
        
        topics = []
        for topic in common_topics:
            if topic in text:
                topics.append(topic)
        
        # Extract product names (capitalized words)
        product_pattern = r'\b[A-Z][A-Z0-9]+\b'
        products = re.findall(product_pattern, subject + " " + body)
        topics.extend(products)
        
        return list(set(topics))  # Remove duplicates
    
    def _retrieve_knowledge(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge base items for topics.
        
        Args:
            topics: List of topics to search for
            
        Returns:
            List of relevant knowledge items
        """
        relevant_items = []
        
        for topic in topics:
            # Search knowledge base for items related to this topic
            items = self.knowledge_base.search_items(topic, limit=3)
            for item in items:
                # Convert KnowledgeItem to dictionary for easier handling
                item_dict = {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "tags": item.tags
                }
                relevant_items.append(item_dict)
        
        # Remove duplicates
        seen_ids = set()
        unique_items = []
        for item in relevant_items:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                unique_items.append(item)
        
        return unique_items[:5]  # Limit to 5 items
    
    def _generate_response_with_context(self,
                                      subject: str,
                                      body: str,
                                      sentiment: SentimentType,
                                      topics: List[str],
                                      knowledge_items: List[Dict[str, Any]],
                                      extracted_info: Dict[str, Any] = None) -> str:
        """Generate response using context and knowledge items.
        
        Args:
            subject: Email subject
            body: Email body
            sentiment: Sentiment of the email
            topics: Extracted topics
            knowledge_items: Relevant knowledge items
            extracted_info: Extracted information from the email
            
        Returns:
            Generated response content
        """
        # Start with a professional greeting
        response = "Hello,\n\n"
        
        # Acknowledge the customer's sentiment if negative
        if sentiment == SentimentType.NEGATIVE:
            response += "I understand you're experiencing some frustration, and I sincerely apologize for any inconvenience this has caused.\n\n"
        elif sentiment == SentimentType.POSITIVE:
            response += "Thank you for reaching out to us.\n\n"
        
        # Address the main topic of the email
        if knowledge_items:
            # Use the most relevant knowledge item
            primary_item = knowledge_items[0]
            response += f"Regarding your inquiry about {primary_item['title'].lower()}:\n\n"
            response += primary_item['content'] + "\n\n"
            
            # Mention additional relevant information
            if len(knowledge_items) > 1:
                response += "Additionally, you might find the following information helpful:\n"
                for item in knowledge_items[1:3]:  # Limit to 2 additional items
                    response += f"- {item['title']}: {item['content'][:100]}...\n"
                response += "\n"
        else:
            # Generic response when no specific knowledge is found
            response += "Thank you for your inquiry. We're currently looking into this matter and will get back to you with more detailed information shortly.\n\n"
        
        # Include contact information for further assistance
        response += "If you need further assistance, please don't hesitate to reach out to our support team at support@company.com or call us at 1-800-123-4567.\n\n"
        
        # Professional closing
        response += "Best regards,\n"
        response += "Customer Support Team"
        
        return response
    
    def generate_empathetic_response(self, 
                                   subject: str, 
                                   body: str, 
                                   sentiment: SentimentType,
                                   extracted_info: Dict[str, Any] = None) -> str:
        """Generate an empathetic response for negative sentiment emails.
        
        Args:
            subject: Email subject
            body: Email body
            sentiment: Sentiment of the email
            extracted_info: Extracted information from the email
            
        Returns:
            Generated empathetic response content
        """
        if sentiment != SentimentType.NEGATIVE:
            return self.generate_response(subject, body, sentiment, extracted_info)
        
        # Extract specific issues from the email
        issues = self._extract_issues(body)
        
        # Start with an empathetic greeting
        response = "Hello,\n\n"
        
        # Acknowledge the frustration and show empathy
        response += "I'm truly sorry to hear about the difficulties you're experiencing. I completely understand how frustrating this situation must be for you, and I want to assure you that we're taking your concerns seriously.\n\n"
        
        # Address specific issues mentioned
        if issues:
            response += "I can see that you're dealing with the following issues:\n"
            for issue in issues[:3]:  # Limit to 3 issues
                response += f"- {issue}\n"
            response += "\n"
        
        # Provide immediate assistance
        response += "To help resolve this as quickly as possible, I'm escalating your case to our senior support team. They will personally follow up with you within the next 24 hours.\n\n"
        
        # Offer additional support
        response += "In the meantime, if you have any additional questions or concerns, please feel free to reply to this email or contact our priority support line at 1-800-123-4567, extension 9.\n\n"
        
        # Professional closing
        response += "Thank you for your patience and understanding.\n\n"
        response += "Best regards,\n"
        response += "Customer Support Team"
        
        return response
    
    def _extract_issues(self, body: str) -> List[str]:
        """Extract specific issues from email body.
        
        Args:
            body: Email body
            
        Returns:
            List of extracted issues
        """
        # Simple pattern-based issue extraction
        # In a real implementation, this would be more sophisticated
        issue_patterns = [
            r'(cannot|can\'t|couldn\'t)\s+(.+?)[.!?]',
            r'(having trouble|struggling with)\s+(.+?)[.!?]',
            r'(issue with|problem with|error with)\s+(.+?)[.!?]',
            r'(not working|broken|failed)\s+(.+?)[.!?]'
        ]
        
        issues = []
        for pattern in issue_patterns:
            matches = re.findall(pattern, body, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    issues.append(match[1].strip())
                else:
                    issues.append(match.strip())
        
        return issues


# Example usage
def example_usage():
    """Example usage of the ResponseGenerator."""
    # Create a knowledge base with sample items
    from backend.services.knowledge_base import KnowledgeBase
    
    kb = KnowledgeBase()
    kb.add_item(
        title="Account Login Issues",
        content="If you're unable to log into your account, try resetting your password. Click 'Forgot Password' on the login page and follow the instructions sent to your email.",
        category="Account Management",
        tags=["login", "account", "password"]
    )
    
    kb.add_item(
        title="Password Reset Process",
        content="To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your email address, 3) Check your email for a password reset link, 4) Click the link and enter a new password.",
        category="Account Management",
        tags=["password", "reset", "account"]
    )
    
    # Create response generator
    generator = ResponseGenerator(kb)
    
    # Test with a sample email
    subject = "Help with login issue"
    body = "I can't access my account. This is really frustrating. Please help!"
    sentiment = SentimentType.NEGATIVE
    
    response = generator.generate_response(subject, body, sentiment)
    print("Generated Response:")
    print("=" * 20)
    print(response)
    
    # Test with empathetic response
    empathetic_response = generator.generate_empathetic_response(subject, body, sentiment)
    print("\n\nEmpathetic Response:")
    print("=" * 20)
    print(empathetic_response)


if __name__ == "__main__":
    example_usage()