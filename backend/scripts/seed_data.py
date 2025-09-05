"""
Database seeding script for CSV data ingestion.
"""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from backend.core.database import get_db_session
from backend.models import Email, SentimentType, PriorityLevel, EmailStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVDataIngester:
    """Utility class for ingesting CSV data into the database."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = Path(csv_file_path)
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
    
    def _analyze_sentiment(self, text: str) -> SentimentType:
        """Simple sentiment analysis based on keywords."""
        text_lower = text.lower()
        
        # Negative sentiment keywords
        negative_keywords = [
            'unable', 'cannot', 'error', 'issue', 'problem', 'failed', 'down',
            'critical', 'urgent', 'blocked', 'help', 'support', 'trouble'
        ]
        
        # Positive sentiment keywords
        positive_keywords = [
            'thank', 'great', 'excellent', 'good', 'appreciate', 'satisfied',
            'working', 'resolved', 'perfect'
        ]
        
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        
        if negative_count > positive_count:
            return SentimentType.NEGATIVE
        elif positive_count > negative_count:
            return SentimentType.POSITIVE
        else:
            return SentimentType.NEUTRAL
    
    def _determine_priority(self, subject: str, body: str) -> PriorityLevel:
        """Determine priority based on keywords in subject and body."""
        text = f"{subject} {body}".lower()
        
        urgent_keywords = [
            'urgent', 'critical', 'immediate', 'asap', 'emergency', 'down',
            'cannot access', 'blocked', 'billing error', 'charged twice',
            'servers are down', 'highly critical'
        ]
        
        for keyword in urgent_keywords:
            if keyword in text:
                return PriorityLevel.URGENT
        
        return PriorityLevel.NOT_URGENT
    
    def _extract_info(self, subject: str, body: str, sender: str) -> Dict[str, Any]:
        """Extract additional information from email content."""
        info = {
            'sender_domain': sender.split('@')[1] if '@' in sender else None,
            'word_count': len(body.split()),
            'has_question_mark': '?' in body,
            'mentions_api': 'api' in body.lower(),
            'mentions_billing': any(word in body.lower() for word in ['billing', 'charge', 'payment']),
            'mentions_login': any(word in body.lower() for word in ['login', 'log in', 'account']),
        }
        return info
    
    def load_csv_data(self) -> List[Dict[str, Any]]:
        """Load and parse CSV data."""
        data = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            
            logger.info(f"Loaded {len(data)} records from CSV file")
            return data
        
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def process_and_insert_data(self) -> int:
        """Process CSV data and insert into database."""
        csv_data = self.load_csv_data()
        inserted_count = 0
        
        with get_db_session() as db:
            for row in csv_data:
                try:
                    # Parse the sent_date
                    received_at = datetime.strptime(row['sent_date'], '%Y-%m-%d %H:%M:%S')
                    
                    # Analyze sentiment and priority
                    sentiment = self._analyze_sentiment(f"{row['subject']} {row['body']}")
                    priority = self._determine_priority(row['subject'], row['body'])
                    
                    # Extract additional information
                    extracted_info = self._extract_info(row['subject'], row['body'], row['sender'])
                    
                    # Create email record
                    email = Email(
                        sender_email=row['sender'],
                        subject=row['subject'],
                        body=row['body'],
                        received_at=received_at,
                        sentiment=sentiment,
                        priority=priority,
                        status=EmailStatus.PENDING,
                        extracted_info=extracted_info
                    )
                    
                    db.add(email)
                    inserted_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing row {row}: {e}")
                    continue
            
            logger.info(f"Successfully inserted {inserted_count} email records")
        
        return inserted_count


def seed_database(csv_file_path: str = "68b1acd44f393_Sample_Support_Emails_Dataset.csv"):
    """Seed the database with sample data from CSV file."""
    logger.info("Starting database seeding...")
    
    try:
        ingester = CSVDataIngester(csv_file_path)
        count = ingester.process_and_insert_data()
        logger.info(f"Database seeding completed. Inserted {count} records.")
        return count
    
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "68b1acd44f393_Sample_Support_Emails_Dataset.csv"
    
    try:
        seed_database(csv_file)
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        exit(1)