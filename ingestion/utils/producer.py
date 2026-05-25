# ingestion/utils/producer.py

import os
from confluent_kafka import Producer
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def get_producer() -> Producer:
    broker = os.getenv("REDPANDA_BROKER_LOCAL", "localhost:9092")
    producer = Producer({
        "bootstrap.servers": broker,
        "acks": "all",
        "compression.type": "gzip",
        "linger.ms": 10,
        "retries": 3,
    })
    logger.info(f"Kafka producer connected to {broker}")
    return producer


def publish(producer: Producer, topic: str, article) -> None:
    producer.produce(
        topic,
        key=article.source_domain,
        value=article.to_json(),
    )
    logger.debug(f"Published [{article.source_domain}] → {topic}: {article.title[:60]}")