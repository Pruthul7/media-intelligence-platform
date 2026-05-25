-- storage/dbt/models/marts/mart_competitor_tracker.sql
-- Feature: competitor comparison
-- Tracks any entity appearing in entities_orgs
SELECT
    entity,
    toStartOfHour(enriched_at)          AS hour,
    count()                             AS mention_count,
    avg(weighted_sentiment)             AS avg_weighted_sentiment,
    countIf(sentiment_label='negative') AS negative_mentions,
    countIf(sentiment_label='positive') AS positive_mentions,
    countIf(sentiment_label='neutral')  AS neutral_mentions,
    avg(source_credibility)             AS avg_source_credibility,
    round(
        countIf(sentiment_label='negative') * 100.0 / count(), 2
    )                                   AS controversy_score
FROM `news_pipeline`.`stg_enriched_articles`
ARRAY JOIN entities_orgs AS entity
WHERE entity != ''
GROUP BY entity, hour
ORDER BY hour DESC, mention_count DESC