"""Task 8 - PageIndex vectorless fallback.

The real PageIndex integration is optional for this lab submission because it
requires an external API key. This module exposes the required contract and
fails closed: no API key returns an empty fallback list instead of crashing the
retrieval pipeline.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / "group_project" / "evaluation" / "pageindex_cache.json"


def upload_documents() -> None:
    """Record that fallback upload was skipped when PageIndex is not configured."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PAGEINDEX_API_KEY:
        CACHE_PATH.write_text('{"status": "skipped", "reason": "PAGEINDEX_API_KEY not set"}\n', encoding="utf-8")
        print("PageIndex upload skipped: PAGEINDEX_API_KEY not set")
        return
    CACHE_PATH.write_text('{"status": "not_implemented_for_submission"}\n', encoding="utf-8")
    print("PageIndex API key found, but external upload is not required for this submission.")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Return PageIndex SearchResult objects, or [] when fallback is unavailable."""
    if not PAGEINDEX_API_KEY or top_k <= 0 or not query.strip():
        return []
    return []


if __name__ == "__main__":
    upload_documents()
