#!/bin/bash
echo "Starting Media Intelligence Pipeline..."

source venv/bin/activate

# Start ingestion
python -m ingestion.sources.rss_ingestor &
RSS_PID=$!
echo "RSS ingestor started (PID $RSS_PID)"

sleep 5

# Start enrichment
python -m processing.enrichment_job &
ENRICH_PID=$!
echo "Enrichment job started (PID $ENRICH_PID)"

sleep 3

# Start ClickHouse sink
python -m storage.clickhouse.sink &
SINK_PID=$!
echo "ClickHouse sink started (PID $SINK_PID)"

sleep 3

# Start dbt scheduler
python run_dbt_scheduler.py &
DBT_PID=$!
echo "dbt scheduler started (PID $DBT_PID)"

echo ""
echo "All components running:"
echo "  RSS Ingestor    PID: $RSS_PID"
echo "  Enrichment Job  PID: $ENRICH_PID"
echo "  ClickHouse Sink PID: $SINK_PID"
echo "  dbt Scheduler   PID: $DBT_PID"
echo ""
echo "Press Ctrl+C to stop all."

trap "kill $RSS_PID $ENRICH_PID $SINK_PID $DBT_PID; echo 'Pipeline stopped.'" SIGINT
wait
