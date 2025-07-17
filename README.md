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

