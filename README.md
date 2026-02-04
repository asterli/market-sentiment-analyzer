# 📰 Real-Time Market Sentiment Analyzer

A production-ready AI pipeline that ingests financial news in real-time, performs sentiment analysis using FinBERT, and provides comprehensive analytics through a REST API and Grafana dashboards.

## 🚀 Overview

This system provides end-to-end sentiment analysis of financial news:
- **NewsAPI** fetches the latest market news every minute
- **Apache Kafka** streams articles for processing
- **FinBERT** (fine-tuned BERT for financial text) analyzes sentiment
- **PostgreSQL** stores articles with sentiment scores
- **FastAPI** exposes data through a comprehensive REST API
- **Grafana** visualizes sentiment trends and market indicators

---

## ✨ Features

### Data Pipeline
- Live article fetching every minute from NewsAPI
- Real-time streaming with Apache Kafka
- Sentiment analysis using FinBERT (positive/negative/neutral)
- Confidence scoring for each prediction
- Deduplication to prevent duplicate articles

### REST API
- Get articles with filtering (by sentiment, source, date)
- Search functionality across titles and descriptions
- Pagination support
- Overall market sentiment score calculation
- Sentiment statistics and trends
- Time-based aggregations

### Monitoring & Analytics
- Real-time Grafana dashboards
- Sentiment distribution charts
- Historical trend analysis
- Market bullish/bearish indicators
- Article volume tracking

### Quality Assurance
- Comprehensive unit tests for all components
- API endpoint testing
- Sentiment classification validation

---

## 🧱 Technologies

- **Python 3.8+** - Core programming language
- **Apache Kafka** - Message streaming
- **PostgreSQL** - Data storage
- **FinBERT** - Sentiment analysis model (HuggingFace Transformers)
- **FastAPI** - REST API framework
- **Grafana** - Visualization and monitoring
- **Docker Compose** - Container orchestration
- **pytest** - Testing framework

---

## 🗂️ Project Structure

```
.
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Test configuration
├── .env                        # Environment variables
├── src/
│   ├── fetch_news.py          # News fetcher (Kafka Producer)
│   ├── kafka_consumer.py      # Kafka consumer with sentiment analysis
│   └── api.py                 # FastAPI REST API
├── sentiment_classification.py # FinBERT sentiment model
├── grafana/
│   └── provisioning/          # Grafana auto-provisioning configs
│       ├── datasources/       # PostgreSQL datasource config
│       └── dashboards/        # Pre-built sentiment dashboard
└── tests/
    ├── test_sentiment.py      # Sentiment analysis tests
    ├── test_api.py            # API endpoint tests
    └── test_fetch_news.py     # News fetcher tests
```

---

## 🐳 Getting Started

### 1. Prerequisites
- Docker and Docker Compose
- Python 3.8 or higher
- NewsAPI key (get free at https://newsapi.org)

### 2. Clone the repository
```bash
git clone https://github.com/your-username/market-sentiment-analyzer.git
cd market-sentiment-analyzer
```

### 3. Create .env file
```bash
echo "NEWS_API_KEY=your_api_key_here" > .env
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Start Docker services
```bash
docker-compose up -d
```

This starts:
- Kafka + Zookeeper (port 9092)
- PostgreSQL (port 5432)
- Adminer (port 8080)
- Grafana (port 3000)

### 6. Run the Kafka consumer
```bash
python src/kafka_consumer.py
```

This will:
- Create the database table with sentiment columns
- Listen for incoming articles
- Analyze sentiment using FinBERT
- Store results in PostgreSQL

### 7. Run the news fetcher
```bash
python src/fetch_news.py
```

This will:
- Fetch news every 60 seconds
- Send articles to Kafka
- Track the latest article timestamp to avoid duplicates

### 8. Start the API server
```bash
python src/api.py
```

API will be available at http://localhost:8000

---

## 🔌 API Endpoints

### Base URL
`http://localhost:8000`

### Documentation
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Endpoints

#### Get Articles
```bash
GET /articles
```
Query parameters:
- `sentiment` (optional): Filter by "positive", "negative", or "neutral"
- `limit` (default: 50, max: 500): Number of articles
- `offset` (default: 0): Pagination offset
- `source` (optional): Filter by news source
- `search` (optional): Search in title and description

Example:
```bash
curl "http://localhost:8000/articles?sentiment=positive&limit=10"
```

#### Get Single Article
```bash
GET /articles/{article_id}
```

#### Sentiment Statistics
```bash
GET /sentiment/stats?hours=24
```
Returns count, average confidence, and percentage for each sentiment type.

#### Market Sentiment Score
```bash
GET /sentiment/market?hours=24
```
Returns overall market sentiment score (-1 to +1) with bullish/bearish/neutral label.

Example response:
```json
{
  "overall_score": 0.234,
  "sentiment_label": "bullish",
  "positive_count": 45,
  "negative_count": 23,
  "neutral_count": 32,
  "total_articles": 100,
  "time_period": "last 24 hours"
}
```

#### Sentiment Trends
```bash
GET /sentiment/trends?hours=24&interval=1
```
Returns time-series sentiment data grouped by hour.

#### Health Check
```bash
GET /health
```

---

## 📊 Grafana Dashboards

Access Grafana at http://localhost:3000

**Default credentials:**
- Username: `admin`
- Password: `admin`

### Pre-built Dashboard: "Market Sentiment Analysis Dashboard"

Features:
- **Market Sentiment Gauge** - Overall bullish/bearish indicator
- **Sentiment Distribution Pie Chart** - Breakdown of positive/negative/neutral
- **Sentiment Trend Graph** - Historical trends over time
- **Recent Articles Table** - Latest news with sentiment labels
- **Statistics Cards** - Total, positive, negative, and neutral article counts

The dashboard auto-refreshes every 30 seconds and shows data from the last 24 hours by default.

---

## 🛠️ Adminer Database Interface

Access PostgreSQL via Adminer at http://localhost:8080

**Connection details:**
- System: PostgreSQL
- Server: `postgres`
- Username: `postgres`
- Password: `postgres`
- Database: `newsdb`

### Database Schema

**Table:** `news_articles`

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| title | TEXT | Article title |
| description | TEXT | Article description |
| content | TEXT | Full article content |
| source | TEXT | News source name |
| url | TEXT | Article URL (unique) |
| published_at | TIMESTAMPTZ | Publication timestamp |
| fetched_at | TIMESTAMPTZ | When article was fetched |
| sentiment | TEXT | positive/negative/neutral |
| sentiment_confidence | REAL | Model confidence score (0-1) |

---

## 🧪 Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_api.py
```

Run with coverage:
```bash
pytest --cov=src --cov=sentiment_classification
```

Run tests verbosely:
```bash
pytest -v
```

---

## 🧹 Maintenance

### Reset Kafka Topic
```bash
# Get Kafka container name
docker ps | grep kafka

# Enter container
docker exec -it <kafka_container_name> bash

# Delete and recreate topic
kafka-topics --bootstrap-server localhost:9092 --delete --topic news_articles
kafka-topics --bootstrap-server localhost:9092 --create --topic news_articles --partitions 1 --replication-factor 1
```

### Clear Database
```bash
docker exec -it <postgres_container_name> psql -U postgres -d newsdb -c "TRUNCATE TABLE news_articles;"
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f kafka
```

---

## 🎯 Usage Examples

### Get Latest Positive News
```bash
curl "http://localhost:8000/articles?sentiment=positive&limit=5"
```

### Check Market Sentiment for Last 6 Hours
```bash
curl "http://localhost:8000/sentiment/market?hours=6"
```

### Search for Bitcoin Articles
```bash
curl "http://localhost:8000/articles?search=bitcoin"
```

### Get Hourly Sentiment Trends
```bash
curl "http://localhost:8000/sentiment/trends?hours=48&interval=1"
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:
```bash
NEWS_API_KEY=your_newsapi_key
```

### Kafka Configuration

Modify `docker-compose.yml` to change Kafka settings:
- Port mapping
- Replication factor
- Partition count

### API Configuration

In [src/api.py](src/api.py:14-16), modify:
- CORS settings
- Database connection parameters
- Default query limits

### News Fetching Interval

In [src/fetch_news.py](src/fetch_news.py:67), modify:
```python
time.sleep(60)  # Change to desired interval in seconds
```

---

## 📈 Performance Considerations

- **FinBERT Model**: First run downloads ~440MB model from HuggingFace
- **Sentiment Analysis**: ~50-200ms per article depending on hardware
- **Database**: Consider adding indexes on `sentiment` and `fetched_at` for large datasets
- **Kafka**: Single partition suitable for moderate loads; increase for higher throughput

---

## 🚀 Production Deployment

For production environments:

1. **Security**
   - Change default PostgreSQL and Grafana passwords
   - Use environment-specific `.env` files
   - Enable SSL/TLS for API endpoints
   - Add authentication to API endpoints

2. **Scalability**
   - Run multiple Kafka consumers for parallel processing
   - Increase Kafka partitions
   - Use PostgreSQL connection pooling
   - Deploy API with gunicorn/uvicorn workers

3. **Monitoring**
   - Add Prometheus metrics
   - Set up alerts in Grafana
   - Monitor Kafka lag
   - Track API response times

4. **Data Retention**
   - Implement data archival strategy
   - Add database partitioning
   - Set up automated backups

---

## 🐛 Troubleshooting

### FinBERT Model Download Issues
```bash
# Pre-download the model
python -c "from transformers import BertTokenizer, BertForSequenceClassification; BertTokenizer.from_pretrained('yiyanghkust/finbert-tone'); BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"
```

### Kafka Connection Issues
```bash
# Check if Kafka is running
docker-compose ps

# View Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Test connection
docker exec -it <postgres_container> psql -U postgres -d newsdb -c "SELECT COUNT(*) FROM news_articles;"
```

### API Not Starting
```bash
# Check for port conflicts
lsof -i :8000

# Run with debug mode
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

---

## 📚 Learn More

- [FinBERT Paper](https://arxiv.org/abs/1908.10063)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🧠 Author Notes

This project demonstrates an end-to-end AI/ML data engineering pipeline, showcasing:
- Real-time data ingestion and streaming
- State-of-the-art NLP model integration
- RESTful API design
- Data visualization and monitoring
- Test-driven development
- Containerized deployment

This project is part of an AI/ML systems capstone for learning end-to-end data engineering workflows. Built for learning and production use cases in quantitative finance and algorithmic trading.

---

## 🔮 Future Enhancements

- [ ] Add stock ticker extraction and tracking
- [ ] Implement real-time WebSocket streaming
- [ ] Add sentiment-based trading signals
- [ ] Integrate with additional news sources (Twitter, Reddit)
- [ ] Implement caching layer (Redis)
- [ ] Add machine learning model retraining pipeline
- [ ] Create mobile dashboard app
- [ ] Add email/SMS alerts for significant sentiment shifts
- [ ] Implement A/B testing for different sentiment models
- [ ] Add multi-language support

---

**Built with ❤️ using open-source tools**
