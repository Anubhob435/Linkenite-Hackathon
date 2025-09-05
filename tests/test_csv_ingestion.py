"""
Unit tests for CSV data ingestion functionality.
"""
import pytest
import tempfile
import csv
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.scripts.seed_data import CSVDataIngester
from backend.models import Email, SentimentType, PriorityLevel


class TestCSVDataIngester:
    """Test cases for CSV data ingestion."""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return [
            {
                'sender': 'test@example.com',
                'subject': 'Urgent help needed',
                'body': 'I cannot access my account and need immediate help',
                'sent_date': '2025-01-01 10:00:00'
            },
            {
                'sender': 'user@company.com',
                'subject': 'Thank you for great service',
                'body': 'Your service is excellent and I appreciate the support',
                'sent_date': '2025-01-02 14:30:00'
            },
            {
                'sender': 'customer@domain.com',
                'subject': 'General inquiry',
                'body': 'I have a question about your pricing plans',
                'sent_date': '2025-01-03 09:15:00'
            }
        ]
    
    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create a temporary CSV file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['sender', 'subject', 'body', 'sent_date'])
            writer.writeheader()
            writer.writerows(sample_csv_data)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    def test_csv_ingester_initialization(self, temp_csv_file):
        """Test CSV ingester initialization."""
        ingester = CSVDataIngester(temp_csv_file)
        assert ingester.csv_file_path == Path(temp_csv_file)
    
    def test_csv_ingester_file_not_found(self):
        """Test CSV ingester with non-existent file."""
        with pytest.raises(FileNotFoundError):
            CSVDataIngester("non_existent_file.csv")
    
    def test_load_csv_data(self, temp_csv_file, sample_csv_data):
        """Test loading CSV data."""
        ingester = CSVDataIngester(temp_csv_file)
        data = ingester.load_csv_data()
        
        assert len(data) == 3
        assert data[0]['sender'] == 'test@example.com'
        assert data[1]['subject'] == 'Thank you for great service'
        assert data[2]['body'] == 'I have a question about your pricing plans'
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative content."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)  # Create without __init__
        
        negative_text = "I cannot access my account and have urgent issues"
        sentiment = ingester._analyze_sentiment(negative_text)
        assert sentiment == SentimentType.NEGATIVE
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive content."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)
        
        positive_text = "Thank you for the excellent service and great support"
        sentiment = ingester._analyze_sentiment(positive_text)
        assert sentiment == SentimentType.POSITIVE
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral content."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)
        
        neutral_text = "I have a question about your pricing plans"
        sentiment = ingester._analyze_sentiment(neutral_text)
        assert sentiment == SentimentType.NEUTRAL
    
    def test_determine_priority_urgent(self):
        """Test priority determination for urgent emails."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)
        
        subject = "Urgent help needed"
        body = "I cannot access my account immediately"
        priority = ingester._determine_priority(subject, body)
        assert priority == PriorityLevel.URGENT
    
    def test_determine_priority_not_urgent(self):
        """Test priority determination for non-urgent emails."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)
        
        subject = "General question"
        body = "I have a question about your services"
        priority = ingester._determine_priority(subject, body)
        assert priority == PriorityLevel.NOT_URGENT
    
    def test_extract_info(self):
        """Test information extraction from email content."""
        ingester = CSVDataIngester.__new__(CSVDataIngester)
        
        subject = "API integration help"
        body = "I need help with billing API integration for my account"
        sender = "user@example.com"
        
        info = ingester._extract_info(subject, body, sender)
        
        assert info['sender_domain'] == 'example.com'
        assert info['word_count'] == 10
        assert info['mentions_api'] is True
        assert info['mentions_billing'] is True
        assert info['mentions_login'] is True  # "account" keyword
    
    def test_process_and_insert_data(self, temp_csv_file):
        """Test processing and inserting CSV data into database."""
        ingester = CSVDataIngester(temp_csv_file)
        
        # Mock the database session and test the processing logic
        mock_session = MagicMock()
        
        with patch('backend.scripts.seed_data.get_db_session') as mock_get_db:
            # Create a mock context manager that returns our mock session
            mock_context = MagicMock()
            mock_context.__enter__.return_value = mock_session
            mock_context.__exit__.return_value = None
            mock_get_db.return_value = mock_context
            
            count = ingester.process_and_insert_data()
            
            assert count == 3
            
            # Verify that add was called 3 times (once for each email)
            assert mock_session.add.call_count == 3
            
            # Verify that the emails passed to add have the correct properties
            added_emails = [call.args[0] for call in mock_session.add.call_args_list]
            
            # Check that all added objects are Email instances
            for email in added_emails:
                assert hasattr(email, 'sender_email')
                assert hasattr(email, 'subject')
                assert hasattr(email, 'body')
                assert hasattr(email, 'sentiment')
                assert hasattr(email, 'priority')
    
    def test_process_invalid_date_format(self, db_session):
        """Test handling of invalid date format in CSV."""
        # Create CSV with invalid date
        invalid_data = [
            {
                'sender': 'test@example.com',
                'subject': 'Test',
                'body': 'Test body',
                'sent_date': 'invalid-date-format'
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['sender', 'subject', 'body', 'sent_date'])
            writer.writeheader()
            writer.writerows(invalid_data)
            temp_path = f.name
        
        try:
            ingester = CSVDataIngester(temp_path)
            
            with patch('backend.scripts.seed_data.get_db_session') as mock_get_db:
                mock_get_db.return_value.__enter__.return_value = db_session
                mock_get_db.return_value.__exit__.return_value = None
                
                # Should handle the error gracefully and return 0 inserted records
                count = ingester.process_and_insert_data()
                assert count == 0
        
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestSeedDatabaseFunction:
    """Test cases for the seed_database function."""
    
    def test_seed_database_success(self):
        """Test successful database seeding."""
        from backend.scripts.seed_data import seed_database
        
        with patch('backend.scripts.seed_data.CSVDataIngester') as mock_ingester_class:
            mock_ingester = MagicMock()
            mock_ingester.process_and_insert_data.return_value = 5
            mock_ingester_class.return_value = mock_ingester
            
            count = seed_database("test_file.csv")
            
            assert count == 5
            mock_ingester_class.assert_called_once_with("test_file.csv")
            mock_ingester.process_and_insert_data.assert_called_once()
    
    def test_seed_database_failure(self):
        """Test database seeding failure."""
        from backend.scripts.seed_data import seed_database
        
        with patch('backend.scripts.seed_data.CSVDataIngester') as mock_ingester_class:
            mock_ingester_class.side_effect = Exception("File processing error")
            
            with pytest.raises(Exception):
                seed_database("non_existent_file.csv")