# serving/api/db.py

import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

def get_client():
    return clickhouse_connect.get_client(
        host     = os.getenv("CLICKHOUSE_HOST", "localhost"),
        port     = int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username = os.getenv("CLICKHOUSE_USER", "admin"),
        password = os.getenv("CLICKHOUSE_PASSWORD", "admin123"),
        database = os.getenv("CLICKHOUSE_DB", "news_pipeline"),
    )