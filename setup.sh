#!/bin/bash

# Market Sentiment Analyzer - Quick Setup Script
# This script sets up and starts the entire pipeline

set -e

echo "=========================================="
echo "Market Sentiment Analyzer - Setup"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "Please create a .env file with your NewsAPI key:"
    echo "  echo 'NEWS_API_KEY=your_api_key_here' > .env"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo ""

# Start Docker services
echo "🐳 Starting Docker services (Kafka, PostgreSQL, Grafana, Adminer)..."
docker-compose up -d
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30
echo ""

# Pre-download FinBERT model
echo "🧠 Pre-downloading FinBERT model (this may take a few minutes)..."
python -c "from transformers import BertTokenizer, BertForSequenceClassification; BertTokenizer.from_pretrained('yiyanghkust/finbert-tone'); BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')" 2>/dev/null || echo "Model download started..."
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the Kafka Consumer (in a new terminal):"
echo "   python src/kafka_consumer.py"
echo ""
echo "2. Start the News Fetcher (in a new terminal):"
echo "   python src/fetch_news.py"
echo ""
echo "3. Start the API Server (in a new terminal):"
echo "   python src/api.py"
echo ""
echo "Access your services:"
echo "  • API:      http://localhost:8000"
echo "  • Docs:     http://localhost:8000/docs"
echo "  • Grafana:  http://localhost:3000 (admin/admin)"
echo "  • Adminer:  http://localhost:8080"
echo ""
echo "To stop all services:"
echo "   docker-compose down"
echo ""
