# src/kafka_consumer.py
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "news_articles",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

for message in consumer:
    print("Received:", message.value["title"])