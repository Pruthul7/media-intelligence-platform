-- storage/dbt/models/marts/mart_sentiment_by_source.sql
-- Feature: source influence dashboard
SELECT
    source_domain,
    source_tier,
    source_credibility,
    toStartOfHour(enriched_at)          AS hour,
    count()                             AS article_count,
    countIf(sentiment_label='positive') AS positive_count,
    countIf(sentiment_label='negative') AS negative_count,
    countIf(sentiment_label='neutral')  AS neutral_count,
    avg(weighted_sentiment)             AS avg_weighted_sentiment,
    round(
        countIf(sentiment_label='positive') * 100.0 / count(), 2
    )                                   AS positivity_pct
FROM {{ ref('stg_enriched_articles') }}
GROUP BY source_domain, source_tier, source_credibility, hour
ORDER BY hour DESC, article_count DESC