# serving/api/routers/crisis.py

from fastapi import APIRouter, Query
from serving.api.db import get_client

router = APIRouter(prefix="/crisis", tags=["Crisis Detection"])

@router.get("/alerts")
def crisis_alerts(min_level: str = Query("LOW", enum=["LOW", "MEDIUM", "HIGH"])):
    levels = {"LOW": ["LOW", "MEDIUM", "HIGH"],
              "MEDIUM": ["MEDIUM", "HIGH"],
              "HIGH": ["HIGH"]}
    level_list = ", ".join(f"'{l}'" for l in levels[min_level])
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            hour,
            narrative_label,
            article_count,
            round(avg_sentiment, 3)         AS avg_sentiment,
            round(volume_zscore, 2)         AS volume_zscore,
            crisis_probability
        FROM news_pipeline.mart_crisis_signals
        WHERE crisis_probability IN ({level_list})
        ORDER BY hour DESC, volume_zscore DESC
        LIMIT 50
    """).named_results()
    return list(rows)


@router.get("/summary")
def crisis_summary():
    ch = get_client()
    rows = ch.query("""
        SELECT
            crisis_probability,
            count() AS count
        FROM news_pipeline.mart_crisis_signals
        GROUP BY crisis_probability
        ORDER BY count DESC
    """).named_results()
    return list(rows)