# run_dbt_scheduler.py
import subprocess
import time
import os
import schedule
from loguru import logger

# Use absolute paths
PROJECT_ROOT = os.path.expanduser("~/news-sentiment-pipeline")
DBT_PATH     = os.path.join(PROJECT_ROOT, "venv/bin/dbt")
DBT_DIR      = os.path.join(PROJECT_ROOT, "storage/dbt")
PROFILES_DIR = os.path.expanduser("~/.dbt")

def run_dbt():
    logger.info("Running dbt models...")
    result = subprocess.run(
        [DBT_PATH, "run", "--profiles-dir", PROFILES_DIR],
        cwd=DBT_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        logger.info("dbt run completed successfully")
    else:
        logger.error(f"dbt run failed: {result.stderr}")

schedule.every(30).minutes.do(run_dbt)
run_dbt()

logger.info("dbt scheduler started — running every 30 minutes")
while True:
    schedule.run_pending()
    time.sleep(60)