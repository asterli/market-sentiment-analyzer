# src/api.py
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import os

app = FastAPI(
    title="Market Sentiment Analyzer API",
    description="Real-time financial news sentiment analysis API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="newsdb",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )

# Pydantic models
class Article(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: Optional[str]
    source: str
    url: str
    published_at: datetime
    fetched_at: datetime
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None

class SentimentStats(BaseModel):
    sentiment: str
    count: int
    avg_confidence: float
    percentage: float

class MarketSentiment(BaseModel):
    overall_score: float
    sentiment_label: str
    positive_count: int
    negative_count: int
    neutral_count: int
    total_articles: int
    time_period: str

# Endpoints
@app.get("/")
def root():
    return {
        "message": "Market Sentiment Analyzer API",
        "endpoints": {
            "articles": "/articles",
            "sentiment_stats": "/sentiment/stats",
            "market_sentiment": "/sentiment/market",
            "trends": "/sentiment/trends"
        }
    }

@app.get("/articles", response_model=List[Article])
def get_articles(
    sentiment: Optional[str] = Query(None, description="Filter by sentiment: positive, negative, neutral"),
    limit: int = Query(50, ge=1, le=500, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    source: Optional[str] = Query(None, description="Filter by news source"),
    search: Optional[str] = Query(None, description="Search in title and description")
):
    """Get articles with optional filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM news_articles WHERE 1=1"
    params = []

    if sentiment:
        query += " AND sentiment = %s"
        params.append(sentiment.lower())

    if source:
        query += " AND source ILIKE %s"
        params.append(f"%{source}%")

    if search:
        query += " AND (title ILIKE %s OR description ILIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    query += " ORDER BY published_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor.execute(query, params)
    articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return articles

@app.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: int):
    """Get a specific article by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM news_articles WHERE id = %s", (article_id,))
    article = cursor.fetchone()

    cursor.close()
    conn.close()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return article

@app.get("/sentiment/stats", response_model=List[SentimentStats])
def get_sentiment_stats(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours")
):
    """Get sentiment statistics for a time period"""
    conn = get_db_connection()
    cursor = conn.cursor()

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    cursor.execute("""
        WITH total AS (
            SELECT COUNT(*) as total_count
            FROM news_articles
            WHERE fetched_at >= %s
        )
        SELECT
            sentiment,
            COUNT(*) as count,
            AVG(sentiment_confidence) as avg_confidence,
            (COUNT(*) * 100.0 / (SELECT total_count FROM total)) as percentage
        FROM news_articles
        WHERE fetched_at >= %s
        GROUP BY sentiment
        ORDER BY count DESC
    """, (time_threshold, time_threshold))

    stats = cursor.fetchall()

    cursor.close()
    conn.close()

    return stats

@app.get("/sentiment/market", response_model=MarketSentiment)
def get_market_sentiment(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours")
):
    """Calculate overall market sentiment score"""
    conn = get_db_connection()
    cursor = conn.cursor()

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    cursor.execute("""
        SELECT
            sentiment,
            COUNT(*) as count
        FROM news_articles
        WHERE fetched_at >= %s
        GROUP BY sentiment
    """, (time_threshold,))

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    # Calculate counts
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for row in results:
        sentiment_counts[row["sentiment"]] = row["count"]

    total = sum(sentiment_counts.values())

    if total == 0:
        raise HTTPException(status_code=404, detail="No articles found in the specified time period")

    # Calculate sentiment score: (positive - negative) / total
    # Range: -1 (all negative) to +1 (all positive)
    sentiment_score = (sentiment_counts["positive"] - sentiment_counts["negative"]) / total

    # Determine label
    if sentiment_score > 0.15:
        label = "bullish"
    elif sentiment_score < -0.15:
        label = "bearish"
    else:
        label = "neutral"

    return {
        "overall_score": round(sentiment_score, 3),
        "sentiment_label": label,
        "positive_count": sentiment_counts["positive"],
        "negative_count": sentiment_counts["negative"],
        "neutral_count": sentiment_counts["neutral"],
        "total_articles": total,
        "time_period": f"last {hours} hours"
    }

@app.get("/sentiment/trends")
def get_sentiment_trends(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    interval: int = Query(1, ge=1, le=24, description="Interval in hours for grouping")
):
    """Get sentiment trends over time"""
    conn = get_db_connection()
    cursor = conn.cursor()

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)

    cursor.execute("""
        SELECT
            DATE_TRUNC('hour', fetched_at) +
            INTERVAL '1 hour' * FLOOR(EXTRACT(HOUR FROM fetched_at - DATE_TRUNC('hour', fetched_at)) / %s) * %s as time_bucket,
            sentiment,
            COUNT(*) as count,
            AVG(sentiment_confidence) as avg_confidence
        FROM news_articles
        WHERE fetched_at >= %s
        GROUP BY time_bucket, sentiment
        ORDER BY time_bucket DESC, sentiment
    """, (interval, interval, time_threshold))

    trends = cursor.fetchall()

    cursor.close()
    conn.close()

    # Format results
    formatted_trends = []
    for row in trends:
        formatted_trends.append({
            "timestamp": row["time_bucket"].isoformat(),
            "sentiment": row["sentiment"],
            "count": row["count"],
            "avg_confidence": round(float(row["avg_confidence"]), 3)
        })

    return formatted_trends

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        count = cursor.fetchone()["count"]
        cursor.close()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected",
            "total_articles": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
