import os
import requests
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_news(query="stock market"):
    """Fetch news articles from the News API"""
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 50,
    }
    response = requests.get(NEWS_API_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        clean_articles = []
        for article in articles:
            clean_articles.append({
                "title": article["title"],
                "description": article["description"],
                "content": article["content"],
                "source": article["source"]["name"],
                "published_at": article["publishedAt"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        return clean_articles
    else:
        print("Error:", response.status_code, response.text)
        return []

if __name__ == "__main__":
    while True:
        news = fetch_news()
        print(f"Fetched {len(news)} news articles.")
        for article in news:
            print(article["title"])
        time.sleep(60)