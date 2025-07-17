# src/kafka_consumer.py
from kafka import KafkaConsumer
import json
import psycopg2
from datetime import datetime

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

# Create table if it doesn't exist — now includes UNIQUE constraint on url
cursor.execute("""
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    content TEXT,
    source TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ
)
""")
conn.commit()

print("Waiting for articles...")

for message in consumer:
    article = message.value

    try:
        cursor.execute("""
        INSERT INTO news_articles (title, description, content, source, url, published_at, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """, (
            article.get("title"),
            article.get("description"),
            article.get("content"),
            article.get("source"),
            article.get("url"),  # Make sure your producer includes 'url'
            article.get("published_at"),
            article.get("timestamp", datetime.utcnow())  # fallback if missing
        ))
        conn.commit()
        print(f"Inserted article: {article.get('title')}")
    except Exception as e:
        print(f"Failed to insert article: {e}")
        conn.rollback()
