-- storage/dbt/models/staging/stg_enriched_articles.sql
SELECT
    article_id,
    title,
    url,
    source_domain,
    source_tier,
    source_credibility,
    source_region,
    sentiment_label,
    sentiment_score,
    weighted_sentiment,
    narrative_cluster_id,
    narrative_label,
    entities_orgs,
    entities_people,
    entities_locations,
    country_code,
    enriched_at,
    published_at,
    toDate(enriched_at) AS event_date
FROM `news_pipeline`.`enriched_articles`