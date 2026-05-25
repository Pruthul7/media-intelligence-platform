# serving/api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from serving.api.routers import sentiment, narratives, geo, competitors, crisis

app = FastAPI(
    title="Media Intelligence Platform API",
    description="Real-time narrative risk and sentiment intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sentiment.router)
app.include_router(narratives.router)
app.include_router(geo.router)
app.include_router(competitors.router)
app.include_router(crisis.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "platform": "Media Intelligence API",
        "status": "running",
        "endpoints": [
            "/sentiment/by-source",
            "/sentiment/trend",
            "/narratives/top",
            "/geo/heatmap",
            "/competitors/compare",
            "/competitors/leaderboard",
            "/crisis/alerts",
            "/crisis/summary",
            "/docs",
        ]
    }


@app.get("/health", tags=["Health"])
def health():
    from serving.api.db import get_client
    try:
        ch = get_client()
        count = ch.query("SELECT count() FROM news_pipeline.enriched_articles").first_row[0]
        return {"status": "healthy", "articles_indexed": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}