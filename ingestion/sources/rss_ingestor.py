# ingestion/sources/rss_ingestor.py

import time
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from loguru import logger

from ingestion.models.article import RawArticle
from ingestion.sources.registry import get_source_meta
from ingestion.utils.producer import get_producer, publish

# Add or remove any RSS feeds you want to track
RSS_FEEDS = [
    # Indian outlets
    "https://www.thehindu.com/news/national/feeder/default.rss",
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "https://www.livemint.com/rss/news",
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
    # International
    "https://feeds.reuters.com/reuters/topNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://techcrunch.com/feed/",
]

TOPIC = "raw-media-events"
POLL_INTERVAL_SECONDS = 300   # poll every 5 minutes


def parse_published_at(entry) -> str:
    """Parse published date from feed entry, fallback to now."""
    try:
        if hasattr(entry, "published"):
            return parsedate_to_datetime(entry.published).isoformat()
    except Exception:
        pass
    return datetime.now(timezone.utc).isoformat()


def extract_full_text(entry) -> str:
    """Try to get the most complete text available from entry."""
    if hasattr(entry, "content") and entry.content:
        return entry.content[0].get("value", "")
    if hasattr(entry, "summary"):
        return entry.summary
    return ""


def run_rss_ingestor():
    producer = get_producer()
    seen_urls: set = set()  # dedup within a session

    logger.info(f"RSS ingestor started. Polling {len(RSS_FEEDS)} feeds every {POLL_INTERVAL_SECONDS}s")

    while True:
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                if feed.bozo:
                    logger.warning(f"Malformed feed: {feed_url}")
                    continue

                new_count = 0
                for entry in feed.entries:
                    url = getattr(entry, "link", None)
                    if not url or url in seen_urls:
                        continue

                    seen_urls.add(url)

                    source_meta = get_source_meta(url)
                    article = RawArticle.create(
                        title            = getattr(entry, "title", ""),
                        url              = url,
                        summary          = getattr(entry, "summary", ""),
                        full_text        = extract_full_text(entry),
                        published_at     = parse_published_at(entry),
                        source_meta      = source_meta,
                        ingestion_source = "rss",
                    )
                    publish(producer, TOPIC, article)
                    new_count += 1

                if new_count:
                    logger.info(f"{feed_url.split('/')[2]} → {new_count} new articles")

            except Exception as e:
                logger.error(f"Error processing feed {feed_url}: {e}")

        producer.flush()
        logger.info(f"Cycle complete. Sleeping {POLL_INTERVAL_SECONDS}s...")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_rss_ingestor()