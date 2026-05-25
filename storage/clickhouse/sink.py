# storage/clickhouse/sink.py

import os
import json
import time
from datetime import datetime, timezone
from confluent_kafka import Consumer
from dotenv import load_dotenv
from loguru import logger
import clickhouse_connect

load_dotenv()

GROUP_ID = f"clickhouse-sink-{int(time.time())}"
INPUT_TOPIC = "enriched-media"
BATCH_SIZE = 50


def get_consumer() -> Consumer:
    broker = os.getenv("REDPANDA_BROKER_LOCAL", "localhost:9092")
    c = Consumer({
        "bootstrap.servers":     broker,
        "group.id":              GROUP_ID,
        "auto.offset.reset":     "earliest",
        "enable.auto.commit":    True,
        "broker.address.family": "v4",
    })
    c.subscribe([INPUT_TOPIC])
    return c


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host     = os.getenv("CLICKHOUSE_HOST", "localhost"),
        port     = int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username = os.getenv("CLICKHOUSE_USER", "admin"),
        password = os.getenv("CLICKHOUSE_PASSWORD", "admin123"),
        database = os.getenv("CLICKHOUSE_DB", "news_pipeline"),
    )


def parse_dt(val: str):
    """Parse ISO datetime string to Python datetime."""
    if not val:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def msg_to_row(a: dict) -> list:
    return [
        a.get("article_id") or "",
        a.get("url") or "",
        a.get("title") or "",
        a.get("summary") or "",
        a.get("source_domain") or "",
        int(a.get("source_tier") or 4),
        float(a.get("source_credibility") or 0.5),
        a.get("source_region") or "",
        a.get("ingestion_source") or "",
        a.get("sentiment_label") or "neutral",
        float(a.get("sentiment_score") or 0.0),
        float(a.get("sentiment_positive") or 0.0),
        float(a.get("sentiment_negative") or 0.0),
        float(a.get("sentiment_neutral") or 1.0),
        float(a.get("weighted_sentiment") or 0.0),
        a.get("narrative_cluster_id") or "",
        a.get("narrative_label") or "",
        a.get("entities_orgs") or [],
        a.get("entities_people") or [],
        a.get("entities_locations") or [],
        a.get("country_code") or "",      # ← was None for geo-unknown articles
        parse_dt(a.get("published_at")),
        parse_dt(a.get("fetched_at")),
        parse_dt(a.get("enriched_at")),
    ]

COLUMNS = [
    "article_id", "url", "title", "summary",
    "source_domain", "source_tier", "source_credibility", "source_region",
    "ingestion_source", "sentiment_label", "sentiment_score",
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "weighted_sentiment", "narrative_cluster_id", "narrative_label",
    "entities_orgs", "entities_people", "entities_locations",
    "country_code", "published_at", "fetched_at", "enriched_at",
]


def run_sink():
    logger.info("ClickHouse sink starting...")
    consumer = get_consumer()
    ch = get_clickhouse_client()
    batch = []
    total = 0

    try:
        while True:
            msg = consumer.poll(timeout=5.0)

            if msg is None:
                if batch:
                    ch.insert("enriched_articles", batch, column_names=COLUMNS)
                    total += len(batch)
                    logger.info(f"Flushed {len(batch)} rows (total: {total})")
                    batch = []
                continue

            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            try:
                article = json.loads(msg.value().decode("utf-8"))
                batch.append(msg_to_row(article))

                if len(batch) >= BATCH_SIZE:
                    ch.insert("enriched_articles", batch, column_names=COLUMNS)
                    total += len(batch)
                    logger.info(f"Inserted batch of {len(batch)} (total: {total})")
                    batch = []

            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                continue

    except KeyboardInterrupt:
        if batch:
            ch.insert("enriched_articles", batch, column_names=COLUMNS)
            total += len(batch)
        logger.info(f"Sink stopped. Total rows inserted: {total}")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_sink()