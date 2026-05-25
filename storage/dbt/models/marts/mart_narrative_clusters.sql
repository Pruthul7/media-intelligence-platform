-- storage/dbt/models/marts/mart_narrative_clusters.sql
-- Feature: narrative detection dashboard
SELECT
    narrative_cluster_id,
    narrative_label,
    toStartOfHour(enriched_at)          AS hour,
    count()                             AS mention_count,
    avg(weighted_sentiment)             AS avg_weighted_sentiment,
    countIf(sentiment_label='negative') AS negative_mentions,
    countIf(sentiment_label='positive') AS positive_mentions,
    groupArray(10)(source_domain)       AS sources,
    groupArray(5)(title)                AS sample_titles
FROM {{ ref('stg_enriched_articles') }}
GROUP BY narrative_cluster_id, narrative_label, hour
ORDER BY hour DESC, mention_count DESC