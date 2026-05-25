# serving/api/routers/sentiment.py

from fastapi import APIRouter, Query
from serving.api.db import get_client

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])

@router.get("/by-source")
def sentiment_by_source(limit: int = Query(20, le=100)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            source_domain,
            source_tier,
            sum(article_count)              AS total_articles,
            round(avg(avg_weighted_sentiment), 3) AS avg_sentiment,
            sum(positive_count)             AS positive,
            sum(negative_count)             AS negative,
            round(avg(positivity_pct), 1)   AS positivity_pct
        FROM news_pipeline.mart_sentiment_by_source
        GROUP BY source_domain, source_tier
        ORDER BY total_articles DESC
        LIMIT {limit}
    """).named_results()
    return list(rows)


@router.get("/trend")
def sentiment_trend(hours: int = Query(24, le=168)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            toStartOfHour(hour)             AS hour,
            sum(article_count)              AS articles,
            round(avg(avg_weighted_sentiment), 3) AS avg_sentiment,
            sum(positive_count)             AS positive,
            sum(negative_count)             AS negative
        FROM news_pipeline.mart_sentiment_by_source
        WHERE hour >= now() - INTERVAL {hours} HOUR
        GROUP BY hour
        ORDER BY hour ASC
    """).named_results()
    return list(rows)