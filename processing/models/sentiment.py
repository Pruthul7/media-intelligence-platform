from transformers import pipeline
from loguru import logger

_sentiment_pipeline = None

def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        logger.info("Loading FinBERT sentiment model — first load takes ~30s...")
        _sentiment_pipeline = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            top_k=None,           # return all three scores
            truncation=True,
            max_length=512,
        )
        logger.info("FinBERT loaded.")
    return _sentiment_pipeline


def score_sentiment(text: str) -> dict:
    """
    Returns:
        {
          "label": "positive" | "negative" | "neutral",
          "score": float,          # confidence of winning label
          "positive": float,
          "negative": float,
          "neutral": float,
        }
    """
    if not text or len(text.strip()) < 10:
        return {
            "label": "neutral", "score": 1.0,
            "positive": 0.0, "negative": 0.0, "neutral": 1.0
        }
    try:
        pipe = get_sentiment_pipeline()
        # use first 512 tokens worth of text
        results = pipe(text[:1500])[0]
        scores = {r["label"].lower(): round(r["score"], 4) for r in results}
        winning = max(scores, key=scores.get)
        return {
            "label":    winning,
            "score":    scores[winning],
            "positive": scores.get("positive", 0.0),
            "negative": scores.get("negative", 0.0),
            "neutral":  scores.get("neutral",  0.0),
        }
    except Exception as e:
        logger.error(f"Sentiment scoring failed: {e}")
        return {
            "label": "neutral", "score": 1.0,
            "positive": 0.0, "negative": 0.0, "neutral": 1.0
        }