"""
AI processing engine for sentiment analysis and priority detection.
"""
import re
from typing import Dict, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class PriorityLevel(str, Enum):
    URGENT = "urgent"
    NOT_URGENT = "not_urgent"


class AIProcessingEngine:
    """AI processing engine for analyzing emails."""
    
    def __init__(self):
        # Define keywords for sentiment analysis
        self.positive_keywords = [
            "thank", "thanks", "appreciate", "great", "excellent", "good", 
            "wonderful", "fantastic", "amazing", "pleased", "satisfied",
            "happy", "delighted", "grateful", "awesome", "brilliant"
        ]
        
        self.negative_keywords = [
            "angry", "frustrated", "disappointed", "upset", "annoyed", 
            "disgusted", "hate", "terrible", "awful", "horrible",
            "bad", "worst", "unhappy", "dissatisfied", "furious",
            "problem", "issue", "error", "broken", "failed", "cannot",
            "can't", "won't", "don't", "doesn't", "didn't"
        ]
        
        # Define keywords for priority detection
        self.urgent_keywords = [
            "immediately", "urgent", "asap", "as soon as possible", 
            "critical", "emergency", "important", "hurry", "quick",
            "fast", "soon", "now", "instantly", "right away",
            "cannot access", "can't access", "blocked", "down",
            "crash", "crashed", "broken", "failure", "failed",
            "outage", "downtime", "offline", "unavailable"
        ]
    
    def analyze_sentiment(self, text: str) -> SentimentType:
        """Analyze the sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentType enum value
        """
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        # Determine sentiment based on keyword counts
        if positive_count > negative_count:
            return SentimentType.POSITIVE
        elif negative_count > positive_count:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL
    
    def determine_priority(self, subject: str, body: str) -> PriorityLevel:
        """Determine the priority level of an email.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            PriorityLevel enum value
        """
        text_lower = (subject + " " + body).lower()
        
        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in text_lower:
                return PriorityLevel.URGENT
        
        return PriorityLevel.NOT_URGENT
    
    def extract_information(self, body: str) -> Dict[str, Any]:
        """Extract key information from email body.
        
        Args:
            body: Email body text
            
        Returns:
            Dictionary containing extracted information
        """
        extracted_info = {}
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, body)
        extracted_info["phones"] = phones
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, body)
        extracted_info["emails"] = emails
        
        # Extract potential product names (words in capital letters)
        product_pattern = r'\b[A-Z][A-Z0-9]+\b'
        products = re.findall(product_pattern, body)
        extracted_info["products"] = products
        
        # Extract sentiment indicators
        sentiment_indicators = {
            "positive": [],
            "negative": []
        }
        
        for keyword in self.positive_keywords:
            if keyword in body.lower():
                sentiment_indicators["positive"].append(keyword)
        
        for keyword in self.negative_keywords:
            if keyword in body.lower():
                sentiment_indicators["negative"].append(keyword)
        
        extracted_info["sentiment_indicators"] = sentiment_indicators
        
        return extracted_info
    
    def process_email(self, subject: str, body: str) -> Dict[str, Any]:
        """Process an email through the AI engine.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Dictionary containing processed results
        """
        # Analyze sentiment
        sentiment = self.analyze_sentiment(body)
        
        # Determine priority
        priority = self.determine_priority(subject, body)
        
        # Extract information
        extracted_info = self.extract_information(body)
        
        # Combine results
        results = {
            "sentiment": sentiment,
            "priority": priority,
            "extracted_info": extracted_info
        }
        
        logger.info(f"Processed email - Sentiment: {sentiment}, Priority: {priority}")
        return results


# Example usage
def example_usage():
    """Example usage of the AIProcessingEngine."""
    engine = AIProcessingEngine()
    
    # Test with a sample email
    subject = "Urgent: Cannot access my account"
    body = "Hi support, I am unable to log into my account since yesterday. This is really frustrating and I need help immediately. Please assist as soon as possible."
    
    results = engine.process_email(subject, body)
    print(f"Subject: {subject}")
    print(f"Results: {results}")


if __name__ == "__main__":
    example_usage()