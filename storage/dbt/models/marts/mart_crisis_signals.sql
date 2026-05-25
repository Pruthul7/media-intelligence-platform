-- mart_crisis_signals.sql
-- Z-score computed only within the relevant rolling window
WITH hourly AS (
    SELECT
        narrative_cluster_id,
        narrative_label,
        toStartOfHour(enriched_at)          AS hour,
        count()                             AS article_count,
        avg(weighted_sentiment)             AS avg_sentiment,
        countIf(sentiment_label='negative') AS negative_count
    FROM {{ ref('stg_enriched_articles') }}
    GROUP BY narrative_cluster_id, narrative_label, hour
),
-- rolling 7-day stats as baseline (not all-time)
stats AS (
    SELECT
        narrative_cluster_id,
        avg(article_count)                  AS mean_count,
        stddevPop(article_count)            AS std_count,
        avg(avg_sentiment)                  AS mean_sentiment
    FROM hourly
    WHERE hour >= now() - INTERVAL 7 DAY    -- baseline window
    GROUP BY narrative_cluster_id
)
SELECT
    h.hour,
    h.narrative_cluster_id,
    h.narrative_label,
    h.article_count,
    h.negative_count,
    h.avg_sentiment,
    s.mean_count,
    s.std_count,
    round(
        if(s.std_count > 0,
           (h.article_count - s.mean_count) / s.std_count,
           0), 3
    )                                       AS volume_zscore,
    CASE
        WHEN (h.article_count - s.mean_count) / nullIf(s.std_count, 0) > 2.0
             AND h.avg_sentiment < -0.3
        THEN 'HIGH'
        WHEN (h.article_count - s.mean_count) / nullIf(s.std_count, 0) > 1.5
             AND h.avg_sentiment < -0.1
        THEN 'MEDIUM'
        WHEN (h.article_count - s.mean_count) / nullIf(s.std_count, 0) > 1.0
        THEN 'LOW'
        ELSE 'NORMAL'
    END                                     AS crisis_probability
FROM hourly h
JOIN stats s USING (narrative_cluster_id)
ORDER BY h.hour DESC, volume_zscore DESC