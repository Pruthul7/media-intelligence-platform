# processing/models/narrative.py

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

CLUSTER_STORE_PATH = "processing/narrative_clusters.json"
SIMILARITY_THRESHOLD = 0.72   # tune this — lower = more clusters
MAX_CLUSTERS = 200

_model = None
_clusters: dict = {}   # { cluster_id: { "label": str, "centroid": list[float], "count": int } }


def get_embedding_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformer model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # fast + lightweight
        logger.info("Sentence transformer loaded.")
    return _model


def _load_clusters():
    global _clusters
    if os.path.exists(CLUSTER_STORE_PATH):
        with open(CLUSTER_STORE_PATH, "r") as f:
            _clusters = json.load(f)
        logger.info(f"Loaded {len(_clusters)} existing narrative clusters.")


def _save_clusters():
    with open(CLUSTER_STORE_PATH, "w") as f:
        json.dump(_clusters, f)


def get_narrative(title: str, summary: str) -> dict:
    """
    Match article to an existing narrative cluster or create a new one.
    Returns:
        { "cluster_id": str, "narrative_label": str, "is_new_cluster": bool }
    """
    global _clusters
    if not _clusters:
        _load_clusters()

    model = get_embedding_model()
    text = f"{title}. {summary}"
    embedding = model.encode([text])[0]

    # compare against all existing cluster centroids
    if _clusters:
        cluster_ids = list(_clusters.keys())
        centroids = np.array([_clusters[c]["centroid"] for c in cluster_ids])
        similarities = cosine_similarity([embedding], centroids)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        if best_score >= SIMILARITY_THRESHOLD:
            cid = cluster_ids[best_idx]
            # update centroid (running average)
            old = np.array(_clusters[cid]["centroid"])
            count = _clusters[cid]["count"]
            _clusters[cid]["centroid"] = (
                ((old * count) + embedding) / (count + 1)
            ).tolist()
            _clusters[cid]["count"] += 1
            _save_clusters()
            return {
                "cluster_id":      cid,
                "narrative_label": _clusters[cid]["label"],
                "is_new_cluster":  False,
            }

    # create new cluster
    import uuid
    cid = f"cluster_{str(uuid.uuid4())[:8]}"
    # use first 60 chars of title as initial label
    label = title[:60].strip()
    _clusters[cid] = {
        "label":    label,
        "centroid": embedding.tolist(),
        "count":    1,
    }
    _save_clusters()
    logger.info(f"New narrative cluster: [{cid}] '{label}'")
    return {
        "cluster_id":      cid,
        "narrative_label": label,
        "is_new_cluster":  True,
    }