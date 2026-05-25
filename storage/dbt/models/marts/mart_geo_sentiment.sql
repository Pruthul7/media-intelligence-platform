-- storage/dbt/models/marts/mart_geo_sentiment.sql
-- Feature: geographic sentiment heatmap
SELECT
    country_code,
    toStartOfDay(enriched_at)           AS day,
    count()                             AS article_count,
    avg(weighted_sentiment)             AS avg_sentiment,
    countIf(sentiment_label='negative') AS negative_count,
    countIf(sentiment_label='positive') AS positive_count,
    round(
        countIf(sentiment_label='negative') * 100.0 / count(), 2
    )                                   AS negativity_pct,
    groupArray(5)(narrative_label)      AS top_narratives
FROM {{ ref('stg_enriched_articles') }}
WHERE country_code != ''
GROUP BY country_code, day
ORDER BY day DESC, article_count DESC