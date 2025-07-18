# 📰 Real-Time Market Sentiment Analyzer for High-Frequency Trading Signals - News Ingestion Pipeline

This project implements a basic data ingestion pipeline to collect, stream, and store news articles related to the stock market using Kafka and PostgreSQL.

## 🚀 Overview

- **NewsAPI** is used to fetch the latest news about the stock market.
- Articles are streamed into **Apache Kafka** as individual messages.
- A Kafka **consumer** reads each article and writes it into a **PostgreSQL** database.
- **Adminer** is included for visualizing and querying the database via web UI.

---

## 📦 Features

- Live article fetching every minute
- JSON serialization and Kafka message streaming
- Deduplication logic to avoid inserting the same article twice
- Dockerized setup for Kafka, Zookeeper, PostgreSQL, and Adminer
- Easily extendable for sentiment analysis and ML pipelines

---

## 🧱 Technologies

- Python
- Kafka (Confluent Platform)
- PostgreSQL
- Docker + Docker Compose
- Adminer
- NewsAPI

---

## 🗂️ Project Structure
```
.
├── docker-compose.yml
├── .env
├── src/
│ ├── fetch_news.py # News fetcher (Producer)
│ └── kafka_consumer.py # Kafka consumer & DB writer
```

---

## 🐳 Getting Started

### 1. Clone the repo
```
git clone https://github.com/your-username/market-sentiment-analyzer.git
cd market-sentiment-analyzer
```

### 2. Add your .env file
```
NEWS_API_KEY=your_api_key_here
```

### 3. Start the system
```
docker-compose up -d
```

### 4. Run the Kafka consumer
```
python src/kafka_consumer.py
```

### 5. Run the news fetcher
```
python src/fetch_news.py
```

---

## 🛠️ Adminer Interface

- Visit http://localhost:8080
- Login with:
    - **System**: PostgreSQL
    - **Server**: postgre
    - **Username**: postgres
    - **Password**: postgres
    - **Database**: newsdb

---

## 🧹 Resetting Kafka Topic
```
docker exec -it <kafka_container_name> bash
kafka-topics --bootstrap-server localhost:9092 --delete --topic news_articles
kafka-topics --bootstrap-server localhost:9092 --create --topic news_articles --partitions 1 --replication-factor 1
```

---

## ✅ To Do / Next Steps

- Add unit tests for producer and consumer
- Integrate article sentiment analysis
- Expose data as a REST API
- Add Grafana dashboards for monitoring

---

## 🧠 Author Notes
- This project is part of an AI/ML systems capstone for learning end-to-end data engineering workflows using open-source tools! Thank you for reading :)
