-- storage/clickhouse/schema.sql

-- Main events table — append-only, ordered by time
CREATE DATABASE IF NOT EXISTS news_pipeline;

USE news_pipeline;

CREATE TABLE IF NOT EXISTS enriched_articles (
    -- identifiers
    article_id          String,
    url                 String,
    title               String,
    summary             String,

    -- source metadata
    source_domain       String,
    source_tier         UInt8,
    source_credibility  Float32,
    source_region       String,
    ingestion_source    String,

    -- sentiment
    sentiment_label     LowCardinality(String),
    sentiment_score     Float32,
    sentiment_positive  Float32,
    sentiment_negative  Float32,
    sentiment_neutral   Float32,
    weighted_sentiment  Float32,

    -- narrative
    narrative_cluster_id    String,
    narrative_label         String,

    -- entities (stored as arrays)
    entities_orgs       Array(String),
    entities_people     Array(String),
    entities_locations  Array(String),

    -- geo
    country_code        LowCardinality(String),

    -- timestamps
    published_at        DateTime64(3, 'UTC'),
    fetched_at          DateTime64(3, 'UTC'),
    enriched_at         DateTime64(3, 'UTC'),

    -- partitioning key (for fast time-based queries)
    event_date          Date MATERIALIZED toDate(enriched_at)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (enriched_at, source_domain, sentiment_label)
SETTINGS index_granularity = 8192;


-- Materialized view for crisis detection
-- Continuously computes per-hour sentiment stats per narrative
CREATE TABLE IF NOT EXISTS narrative_hourly_stats (
    hour                DateTime,
    narrative_cluster_id String,
    narrative_label      String,
    article_count        UInt32,
    avg_weighted_sentiment Float64,
    negative_count       UInt32,
    positive_count       UInt32,
    top_sources          Array(String)
)
ENGINE = SummingMergeTree()
ORDER BY (hour, narrative_cluster_id)
TTL hour + INTERVAL 30 DAY;


CREATE MATERIALIZED VIEW IF NOT EXISTS mv_narrative_hourly
TO narrative_hourly_stats
AS SELECT
    toStartOfHour(enriched_at)  AS hour,
    narrative_cluster_id,
    narrative_label,
    count()                     AS article_count,
    avg(weighted_sentiment)     AS avg_weighted_sentiment,
    countIf(sentiment_label = 'negative') AS negative_count,
    countIf(sentiment_label = 'positive') AS positive_count,
    groupArray(10)(source_domain) AS top_sources
FROM enriched_articles
GROUP BY hour, narrative_cluster_id, narrative_label;