# src/fetch_news.py
import os
import requests
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from dateutil import parser
from kafka import KafkaProducer
import json as json_module

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/everything"

def fetch_news(query="stock market", from_date=None):
    """Fetch news articles from the News API"""
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 50,
    }
    if from_date:
        params["from"] = from_date.isoformat()
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
                "url": article["url"],
                "published_at": article["publishedAt"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        return clean_articles
    else:
        print("Error:", response.status_code, response.text)
        return []

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json_module.dumps(v).encode("utf-8")
)

KAFKA_TOPIC = "news_articles"

if __name__ == "__main__":
    last_published_at = None
    while True:
        news = fetch_news(from_date=last_published_at)
        if news:
            print(f"Fetched {len(news)} new articles.")
            for article in news:
                producer.send(KAFKA_TOPIC, value=article)
                print(f"Sent article to Kafka: {article['title']}")
            # Update the timestamp to the latest article time
            latest_time = max(parser.parse(a["published_at"]) for a in news)
            last_published_at = latest_time + timedelta(seconds=1)
        else:
            print("No new articles found.")
        time.sleep(60)
