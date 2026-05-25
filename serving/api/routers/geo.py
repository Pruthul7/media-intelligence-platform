# serving/api/routers/geo.py

from fastapi import APIRouter, Query
from serving.api.db import get_client

router = APIRouter(prefix="/geo", tags=["Geographic"])

@router.get("/heatmap")
def geo_heatmap(days: int = Query(7, le=30)):
    ch = get_client()
    rows = ch.query(f"""
        SELECT
            country_code,
            sum(article_count)              AS total_articles,
            round(avg(avg_sentiment), 3)    AS avg_sentiment,
            sum(negative_count)             AS negative_count,
            sum(positive_count)             AS positive_count,
            round(avg(negativity_pct), 1)   AS negativity_pct
        FROM news_pipeline.mart_geo_sentiment
        WHERE day >= today() - INTERVAL {days} DAY
          AND country_code != ''
        GROUP BY country_code
        ORDER BY total_articles DESC
    """).named_results()
    return list(rows)