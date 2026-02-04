# tests/test_fetch_news.py
import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fetch_news import fetch_news


class TestFetchNews:
    """Test suite for news fetching functionality"""

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_success(self, mock_get):
        """Test successful news fetching"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test description",
                    "content": "Test content",
                    "source": {"name": "Test Source"},
                    "url": "https://test.com",
                    "publishedAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call function
        articles = fetch_news(query="test")

        # Assertions
        assert len(articles) == 1
        assert articles[0]["title"] == "Test Article"
        assert articles[0]["source"] == "Test Source"
        assert "timestamp" in articles[0]
        mock_get.assert_called_once()

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_with_query(self, mock_get):
        """Test news fetching with custom query"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        fetch_news(query="bitcoin")

        # Verify query parameter was passed
        call_args = mock_get.call_args
        assert "q" in call_args[1]["params"]
        assert call_args[1]["params"]["q"] == "bitcoin"

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_with_from_date(self, mock_get):
        """Test news fetching with from_date parameter"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        from_date = datetime.now(timezone.utc)
        fetch_news(from_date=from_date)

        # Verify from parameter was passed
        call_args = mock_get.call_args
        assert "from" in call_args[1]["params"]

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_error_handling(self, mock_get):
        """Test error handling when API returns error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        articles = fetch_news()

        assert articles == []

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_empty_response(self, mock_get):
        """Test handling of empty article list"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        articles = fetch_news()

        assert articles == []

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_multiple_articles(self, mock_get):
        """Test fetching multiple articles"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": f"Article {i}",
                    "description": f"Description {i}",
                    "content": f"Content {i}",
                    "source": {"name": "Source"},
                    "url": f"https://test.com/{i}",
                    "publishedAt": "2024-01-01T00:00:00Z"
                }
                for i in range(5)
            ]
        }
        mock_get.return_value = mock_response

        articles = fetch_news()

        assert len(articles) == 5
        assert all("title" in a for a in articles)
        assert all("source" in a for a in articles)
        assert all("url" in a for a in articles)

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_article_structure(self, mock_get):
        """Test that returned articles have correct structure"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test",
                    "description": "Desc",
                    "content": "Content",
                    "source": {"name": "Source"},
                    "url": "https://test.com",
                    "publishedAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response

        articles = fetch_news()

        required_fields = ["title", "description", "content", "source", "url", "published_at", "timestamp"]
        for field in required_fields:
            assert field in articles[0]

    @patch('src.fetch_news.requests.get')
    def test_fetch_news_timestamp_added(self, mock_get):
        """Test that timestamp is added to articles"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "Test",
                    "description": "Desc",
                    "content": "Content",
                    "source": {"name": "Source"},
                    "url": "https://test.com",
                    "publishedAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response

        articles = fetch_news()

        assert "timestamp" in articles[0]
        # Verify timestamp is ISO format
        datetime.fromisoformat(articles[0]["timestamp"].replace('Z', '+00:00'))
