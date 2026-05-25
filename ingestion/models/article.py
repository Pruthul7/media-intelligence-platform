# ingestion/models/article.py

import uuid
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RawArticle:
    article_id:          str
    title:               str
    url:                 str
    source_domain:       str
    source_tier:         int
    source_credibility:  float
    source_region:       str
    published_at:        str        # ISO 8601
    fetched_at:          str        # ISO 8601
    summary:             str
    full_text:           str
    language:            str
    ingestion_source:    str        # "rss" | "newsapi"
    country_hint:        Optional[str] = None   # from feed metadata if available

    @staticmethod
    def create(
        title: str,
        url: str,
        summary: str,
        full_text: str,
        published_at: str,
        source_meta: dict,
        ingestion_source: str,
        language: str = "en",
        country_hint: str = None,
    ) -> "RawArticle":
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        return RawArticle(
            article_id        = str(uuid.uuid4()),
            title             = title.strip(),
            url               = url,
            source_domain     = domain,
            source_tier       = source_meta["tier"],
            source_credibility= source_meta["credibility"],
            source_region     = source_meta["region"],
            published_at      = published_at,
            fetched_at        = datetime.now(timezone.utc).isoformat(),
            summary           = summary.strip()[:1000],  # cap at 1000 chars
            full_text         = full_text.strip()[:5000], # cap at 5000 chars
            language          = language,
            ingestion_source  = ingestion_source,
            country_hint      = country_hint,
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)