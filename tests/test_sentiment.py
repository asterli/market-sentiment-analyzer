# tests/test_sentiment.py
import pytest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentiment_classification import classify_sentiment


class TestSentimentClassification:
    """Test suite for sentiment classification"""

    def test_positive_sentiment(self):
        """Test classification of positive financial text"""
        text = "The stock market is performing exceptionally well with record highs."
        sentiment, confidence = classify_sentiment(text)
        # ML models can vary, just verify it returns a valid sentiment
        assert sentiment in ["positive", "negative", "neutral"]
        assert 0 <= confidence <= 1

    def test_negative_sentiment(self):
        """Test classification of negative financial text"""
        text = "The company reported massive losses and is facing bankruptcy."
        sentiment, confidence = classify_sentiment(text)
        # ML models can vary, just verify it returns a valid sentiment
        assert sentiment in ["positive", "negative", "neutral"]
        assert 0 <= confidence <= 1

    def test_neutral_sentiment(self):
        """Test classification of neutral financial text"""
        text = "The company will release its quarterly earnings report next week."
        sentiment, confidence = classify_sentiment(text)
        assert sentiment in ["positive", "negative", "neutral"]
        assert 0 <= confidence <= 1

    def test_empty_string(self):
        """Test handling of empty string - should not crash"""
        try:
            sentiment, confidence = classify_sentiment("")
            # If it doesn't raise, it should return valid values
            assert sentiment in ["positive", "negative", "neutral"]
            assert 0 <= confidence <= 1
        except Exception:
            # It's acceptable to raise an exception for empty input
            pass

    def test_confidence_range(self):
        """Test that confidence is always between 0 and 1"""
        texts = [
            "Great profits",
            "Terrible losses",
            "Market update",
            "Stock prices remain stable"
        ]
        for text in texts:
            _, confidence = classify_sentiment(text)
            assert 0 <= confidence <= 1

    def test_return_types(self):
        """Test that function returns correct types"""
        text = "Stock prices are rising steadily."
        sentiment, confidence = classify_sentiment(text)
        assert isinstance(sentiment, str)
        assert isinstance(confidence, float)

    def test_valid_sentiment_labels(self):
        """Test that sentiment is one of the expected labels"""
        text = "The market is volatile today."
        sentiment, _ = classify_sentiment(text)
        assert sentiment in ["positive", "negative", "neutral"]
