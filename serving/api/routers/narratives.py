# serving/api/routers/narratives.py

from fastapi import APIRouter, Query
from serving.api.db import get_client

router = APIRouter(prefix="/narratives", tags=["Narratives"])

@router.get("/top")
def top_narratives(hours: int = Query(24, le=168), limit: int = Query(20, le=100)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            narrative_cluster_id,
            narrative_label,
            sum(mention_count)              AS total_mentions,
            round(avg(avg_weighted_sentiment), 3) AS avg_sentiment,
            sum(negative_mentions)          AS negative_mentions,
            sum(positive_mentions)          AS positive_mentions
        FROM news_pipeline.mart_narrative_clusters
        WHERE hour >= now() - INTERVAL {hours} HOUR
        GROUP BY narrative_cluster_id, narrative_label
        ORDER BY total_mentions DESC
        LIMIT {limit}
    """).named_results()
    return list(rows)


@router.get("/timeline/{cluster_id}")
def narrative_timeline(cluster_id: str, hours: int = Query(48, le=168)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            hour,
            mention_count,
            avg_weighted_sentiment,
            negative_mentions,
            positive_mentions
        FROM news_pipeline.mart_narrative_clusters
        WHERE narrative_cluster_id = '{cluster_id}'
          AND hour >= now() - INTERVAL {hours} HOUR
        ORDER BY hour ASC
    """).named_results()
    return list(rows)