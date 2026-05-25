# ingestion/sources/newsapi_ingestor.py

import os
import time
from datetime import datetime, timezone, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
from loguru import logger

from ingestion.models.article import RawArticle
from ingestion.sources.registry import get_source_meta
from ingestion.utils.producer import get_producer, publish

load_dotenv()

TOPIC = "raw-media-events"
POLL_INTERVAL_SECONDS = 900   # 15 min — respects free tier rate limits

# Topics to track — maps to your narrative detection later
TRACKED_QUERIES = [
    "data breach OR data leak",
    "CEO scandal OR executive fraud",
    "AI artificial intelligence",
    "layoffs OR job cuts",
    "election fraud OR election results",
    "product recall",
    "IPO startup funding",
]


def run_newsapi_ingestor():
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        logger.error("NEWSAPI_KEY not set in .env — skipping NewsAPI ingestor")
        return

    client = NewsApiClient(api_key=api_key)
    producer = get_producer()
    seen_urls: set = set()

    logger.info(f"NewsAPI ingestor started. Tracking {len(TRACKED_QUERIES)} queries.")

    while True:
        from_time = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S")

        for query in TRACKED_QUERIES:
            try:
                response = client.get_everything(
                    q=query,
                    language="en",
                    sort_by="publishedAt",
                    from_param=from_time,
                    page_size=20,   # max on free tier
                )

                articles = response.get("articles", [])
                new_count = 0

                for item in articles:
                    url = item.get("url", "")
                    if not url or url in seen_urls or "[Removed]" in url:
                        continue

                    seen_urls.add(url)
                    source_meta = get_source_meta(url)

                    published_raw = item.get("publishedAt", "")
                    try:
                        published_at = datetime.fromisoformat(
                            published_raw.replace("Z", "+00:00")
                        ).isoformat()
                    except Exception:
                        published_at = datetime.now(timezone.utc).isoformat()

                    article = RawArticle.create(
                        title            = item.get("title") or "",
                        url              = url,
                        summary          = item.get("description") or "",
                        full_text        = item.get("content") or item.get("description") or "",
                        published_at     = published_at,
                        source_meta      = source_meta,
                        ingestion_source = "newsapi",
                    )
                    publish(producer, TOPIC, article)
                    new_count += 1

                if new_count:
                    logger.info(f"Query '{query[:40]}' → {new_count} articles")

            except Exception as e:
                logger.error(f"NewsAPI error for query '{query}': {e}")
                time.sleep(10)  # back off on error

        producer.flush()
        logger.info(f"NewsAPI cycle complete. Sleeping {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_newsapi_ingestor()