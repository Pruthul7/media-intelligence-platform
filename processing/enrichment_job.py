# processing/enrichment_job.py

import os
import json
import time
from datetime import datetime, timezone
from confluent_kafka import Consumer, Producer, KafkaException
from dotenv import load_dotenv
from loguru import logger

from processing.models.sentiment import score_sentiment
from processing.models.narrative import get_narrative
from processing.models.entities import extract_entities
from processing.utils.geo import infer_country

load_dotenv()

INPUT_TOPIC  = "raw-media-events"
OUTPUT_TOPIC = "enriched-media"

GROUP_ID = f"enrichment-group-{int(time.time())}"

def get_consumer() -> Consumer:
    broker = os.getenv("REDPANDA_BROKER_LOCAL", "localhost:9092")
    c = Consumer({
        "bootstrap.servers":        broker,
        "group.id":                 GROUP_ID,
        "auto.offset.reset":        "earliest",
        "enable.auto.commit":       True,
        "fetch.wait.max.ms":        1000,
        "socket.timeout.ms":        10000,
        "session.timeout.ms":       10000,
        "broker.address.family":    "v4",   # force IPv4 — fixes WSL2 resolution issues
    })
    c.subscribe([INPUT_TOPIC])
    return c


def get_producer() -> Producer:
    broker = os.getenv("REDPANDA_BROKER_LOCAL", "localhost:9092")
    return Producer({
        "bootstrap.servers":     broker,
        "acks":                  "all",
        "compression.type":      "gzip",
        "broker.address.family": "v4",   # force IPv4
    })


def compute_weighted_sentiment(sentiment_score: float,
                                sentiment_label: str,
                                credibility: float) -> float:
    signed = sentiment_score if sentiment_label == "positive" \
             else -sentiment_score if sentiment_label == "negative" \
             else 0.0
    return round(signed * credibility, 4)


def enrich(raw: dict) -> dict:
    text = f"{raw.get('title', '')}. {raw.get('summary', '')}"

    sentiment = score_sentiment(text)
    narrative = get_narrative(raw.get("title", ""), raw.get("summary", ""))
    entities  = extract_entities(text)
    country   = infer_country(
        entities["locations"],
        raw.get("source_region", "")
    ) or raw.get("country_hint")
    weighted  = compute_weighted_sentiment(
        sentiment["score"],
        sentiment["label"],
        raw.get("source_credibility", 0.5),
    )

    return {
        **raw,
        "sentiment_label":      sentiment["label"],
        "sentiment_score":      sentiment["score"],
        "sentiment_positive":   sentiment["positive"],
        "sentiment_negative":   sentiment["negative"],
        "sentiment_neutral":    sentiment["neutral"],
        "weighted_sentiment":   weighted,
        "narrative_cluster_id": narrative["cluster_id"],
        "narrative_label":      narrative["narrative_label"],
        "is_new_cluster":       narrative["is_new_cluster"],
        "entities_orgs":        entities["organizations"],
        "entities_people":      entities["people"],
        "entities_locations":   entities["locations"],
        "country_code":         country,
        "enriched_at":          datetime.now(timezone.utc).isoformat(),
    }


def run_enrichment_job():
    logger.info("Enrichment job starting...")
    consumer = get_consumer()
    producer = get_producer()
    processed = 0

    try:
        while True:
            msg = consumer.poll(timeout=5.0)

            if msg is None:
                logger.debug("No new messages, polling...")
                continue

            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            try:
                raw = json.loads(msg.value().decode("utf-8"))
                enriched = enrich(raw)
                producer.produce(
                    OUTPUT_TOPIC,
                    key=enriched.get("source_domain", ""),
                    value=json.dumps(enriched, ensure_ascii=False),
                )
                processed += 1
                if processed % 10 == 0:
                    producer.flush()
                    logger.info(f"Enriched {processed} articles so far...")

            except Exception as e:
                logger.error(f"Failed to enrich article: {e}")
                continue

    except KeyboardInterrupt:
        logger.info(f"Enrichment job stopped. Total enriched: {processed}")
    finally:
        producer.flush()
        consumer.close()


if __name__ == "__main__":
    run_enrichment_job()