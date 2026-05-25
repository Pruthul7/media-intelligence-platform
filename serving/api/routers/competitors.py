# serving/api/routers/competitors.py

from fastapi import APIRouter, Query
from typing import List
from serving.api.db import get_client

router = APIRouter(prefix="/competitors", tags=["Competitors"])

@router.get("/compare")
def compare_entities(
    entities: List[str] = Query(..., description="e.g. BJP,Congress or Tesla,BYD"),
    hours: int = Query(24, le=168)
):
    entity_list = ", ".join(f"'{e}'" for e in entities)
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            entity,
            sum(mention_count)              AS total_mentions,
            round(avg(avg_weighted_sentiment), 3) AS avg_sentiment,
            sum(positive_mentions)          AS positive,
            sum(negative_mentions)          AS negative,
            round(avg(controversy_score), 1) AS controversy_score,
            round(avg(avg_source_credibility), 3) AS avg_source_credibility
        FROM news_pipeline.mart_competitor_tracker
        WHERE entity IN ({entity_list})
          AND hour >= now() - INTERVAL {hours} HOUR
        GROUP BY entity
        ORDER BY total_mentions DESC
    """).named_results()
    return list(rows)


@router.get("/leaderboard")
def entity_leaderboard(limit: int = Query(20, le=100)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            entity,
            sum(mention_count)              AS total_mentions,
            round(avg(avg_weighted_sentiment), 3) AS avg_sentiment,
            round(avg(controversy_score), 1) AS controversy_score
        FROM news_pipeline.mart_competitor_tracker
        GROUP BY entity
        ORDER BY total_mentions DESC
        LIMIT {limit}
    """).named_results()
    return list(rows)