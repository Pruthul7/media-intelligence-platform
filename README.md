
# Real-Time Media Intelligence & Narrative Risk Platform

A production-grade streaming data platform that ingests news from 15+ sources,
runs AI-powered sentiment analysis, detects emerging narratives, and identifies
potential crises before they go mainstream.

RSS Feeds / NewsAPI / GDELT

↓

Redpanda (Kafka)

raw-media-events

↓

Spark Structured Streaming

├── FinBERT Sentiment

├── Narrative Clustering

├── spaCy Entity Extraction

├── Geographic Inference

└── Influence Weighting

↓

enriched-media topic

↓

ClickHouse + dbt

↓

Grafana Dashboard

<img width="2720" height="3680" alt="media_intelligence_architecture" src="https://github.com/user-attachments/assets/08e63df2-53e3-407a-adfc-3e75c406e900" />


## Features

**Narrative Detection** — Automatically clusters articles into themes using
sentence-transformers embeddings. Discovers "RBI rate decision", "Tamil Nadu
elections", "AI innovation" without any predefined keywords.

**Source Influence Weighting** — Reuters article weighted at 0.95 credibility,
unknown blog at 0.50. One Reuters negative article outweighs 10 low-credibility
negative articles in the weighted sentiment score.

**Geographic Sentiment Heatmap** — Country-level sentiment across 13 countries.
Detects regional narrative shifts for global brand monitoring.

**Competitor Comparison** — Any two entities compared side by side on mentions,
sentiment, and controversy score. BJP vs Congress, Tesla vs BYD, etc.

**Early Crisis Detection** — Z-score anomaly detection on rolling hourly windows.
Fires HIGH/MEDIUM/LOW alert when narrative volume spikes abnormally AND sentiment
goes negative simultaneously.

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, feedparser, NewsAPI, GDELT |
| Message broker | Redpanda (Kafka-compatible) |
| Stream processing | Spark Structured Streaming |
| NLP models | FinBERT, sentence-transformers, spaCy |
| Storage | ClickHouse (columnar, time-series optimized) |
| Transformations | dbt Core |
| Cache | Redis |
| API | FastAPI |
| Dashboard | Grafana |
| Infrastructure | Docker Compose |

## Running Locally

```bash
# Clone and setup
git clone https://github.com/YOURUSERNAME/media-intelligence-platform
cd media-intelligence-platform
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Start infrastructure
docker compose up -d

# Configure
cp .env.example .env
# Add your NEWSAPI_KEY to .env

# Start pipeline
./run_pipeline.sh
```

## Key Design Decisions

**Why Redpanda over direct DB writes?**
Decoupling — ingestor doesn't know about downstream consumers.
New consumers (Slack alerts, ML models) added without touching ingestion.

**Why ClickHouse over Postgres?**
Columnar storage — aggregating 1M rows by country/sentiment runs in
milliseconds vs minutes on row-oriented databases.

**Why sentence-transformers for clustering?**
Keywords break on synonyms. Embeddings capture semantic meaning —
"RBI rate hike" and "India central bank holds rates" cluster together
correctly without any predefined rules.

**Why dbt for transformations?**
Business logic (crisis thresholds, controversy scores, Z-score windows)
lives in version-controlled, testable SQL — not buried in application code.

## Data Pipeline Stats
- 15+ RSS feeds monitored
- ~200 articles/hour at peak
- 13 countries detected and mapped
- Sub-60 second latency from publish to dashboard
