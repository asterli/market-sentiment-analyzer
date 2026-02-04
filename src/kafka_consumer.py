# src/kafka_consumer.py
from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime
import sys
import os

# Add parent directory to path to import sentiment_classification
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentiment_classification import classify_sentiment

# Kafka setup
consumer = KafkaConsumer(
    "news_articles",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

# PostgreSQL connection
conn = psycopg2.connect(
    dbname="newsdb",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create table if it doesn't exist — includes sentiment and confidence columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    content TEXT,
    source TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ,
    sentiment TEXT,
    sentiment_confidence REAL
)
""")
conn.commit()

# Add sentiment columns to existing table if they don't exist
cursor.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='news_articles' AND column_name='sentiment') THEN
        ALTER TABLE news_articles ADD COLUMN sentiment TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='news_articles' AND column_name='sentiment_confidence') THEN
        ALTER TABLE news_articles ADD COLUMN sentiment_confidence REAL;
    END IF;
END $$;
""")
conn.commit()

print("Waiting for articles...")

for message in consumer:
    article = message.value

    try:
        # Analyze sentiment on article content
        text_to_analyze = article.get("content") or article.get("description") or article.get("title")
        sentiment, confidence = classify_sentiment(text_to_analyze) if text_to_analyze else ("neutral", 0.0)

        cursor.execute("""
        INSERT INTO news_articles (title, description, content, source, url, published_at, fetched_at, sentiment, sentiment_confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """, (
            article.get("title"),
            article.get("description"),
            article.get("content"),
            article.get("source"),
            article.get("url"),
            article.get("published_at"),
            article.get("timestamp", datetime.utcnow()),
            sentiment,
            confidence
        ))
        conn.commit()
        print(f"Inserted article: {article.get('title')} | Sentiment: {sentiment} ({confidence:.2f})")
    except Exception as e:
        print(f"Failed to insert article: {e}")
        conn.rollback()
