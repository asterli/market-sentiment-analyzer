# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints"""

    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_get_articles_default(self):
        """Test getting articles with default parameters"""
        response = client.get("/articles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_articles_with_limit(self):
        """Test getting articles with limit parameter"""
        response = client.get("/articles?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_get_articles_with_sentiment_filter(self):
        """Test filtering articles by sentiment"""
        for sentiment in ["positive", "negative", "neutral"]:
            response = client.get(f"/articles?sentiment={sentiment}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            # Verify all articles have the correct sentiment
            for article in data:
                assert article["sentiment"] == sentiment

    def test_get_articles_with_offset(self):
        """Test pagination with offset"""
        response = client.get("/articles?limit=5&offset=0")
        assert response.status_code == 200
        first_page = response.json()

        response = client.get("/articles?limit=5&offset=5")
        assert response.status_code == 200
        second_page = response.json()

        # Verify pages are different (if enough articles exist)
        if len(first_page) > 0 and len(second_page) > 0:
            assert first_page[0]["id"] != second_page[0]["id"]

    def test_get_articles_with_search(self):
        """Test searching articles"""
        response = client.get("/articles?search=market")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_article_by_id_not_found(self):
        """Test getting non-existent article"""
        response = client.get("/articles/999999999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_sentiment_stats(self):
        """Test sentiment statistics endpoint"""
        response = client.get("/sentiment/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Each stat should have required fields
        for stat in data:
            assert "sentiment" in stat
            assert "count" in stat
            assert "avg_confidence" in stat
            assert "percentage" in stat

    def test_sentiment_stats_with_time_period(self):
        """Test sentiment stats with different time periods"""
        for hours in [1, 6, 24, 48]:
            response = client.get(f"/sentiment/stats?hours={hours}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_market_sentiment(self):
        """Test overall market sentiment endpoint"""
        response = client.get("/sentiment/market")
        assert response.status_code in [200, 404]  # 404 if no articles
        if response.status_code == 200:
            data = response.json()
            assert "overall_score" in data
            assert "sentiment_label" in data
            assert "positive_count" in data
            assert "negative_count" in data
            assert "neutral_count" in data
            assert "total_articles" in data
            # Verify score is in valid range
            assert -1 <= data["overall_score"] <= 1
            # Verify label is valid
            assert data["sentiment_label"] in ["bullish", "bearish", "neutral"]

    def test_market_sentiment_time_period(self):
        """Test market sentiment with different time periods"""
        for hours in [6, 12, 24]:
            response = client.get(f"/sentiment/market?hours={hours}")
            assert response.status_code in [200, 404]

    def test_sentiment_trends(self):
        """Test sentiment trends endpoint"""
        response = client.get("/sentiment/trends")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Each trend should have required fields
        for trend in data:
            assert "timestamp" in trend
            assert "sentiment" in trend
            assert "count" in trend
            assert "avg_confidence" in trend

    def test_sentiment_trends_with_interval(self):
        """Test sentiment trends with custom interval"""
        response = client.get("/sentiment/trends?hours=48&interval=6")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_invalid_limit_too_large(self):
        """Test that limit validation works"""
        response = client.get("/articles?limit=1000")
        assert response.status_code == 422  # Validation error

    def test_invalid_limit_negative(self):
        """Test negative limit"""
        response = client.get("/articles?limit=-1")
        assert response.status_code == 422  # Validation error

    def test_invalid_sentiment_filter(self):
        """Test invalid sentiment filter doesn't break"""
        response = client.get("/articles?sentiment=invalid")
        assert response.status_code == 200
        # Should return empty list or handle gracefully

    def test_article_response_schema(self):
        """Test that article response has correct schema"""
        response = client.get("/articles?limit=1")
        if response.status_code == 200 and len(response.json()) > 0:
            article = response.json()[0]
            required_fields = [
                "id", "title", "source", "url",
                "published_at", "fetched_at", "sentiment", "sentiment_confidence"
            ]
            for field in required_fields:
                assert field in article
