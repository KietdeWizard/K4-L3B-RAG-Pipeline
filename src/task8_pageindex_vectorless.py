"""Task 8 - Local vectorless fallback with the PageIndex result contract."""

import os
from pathlib import Path
import re

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / "group_project" / "evaluation" / "pageindex_cache.json"


def upload_documents() -> None:
    """Record which vectorless fallback mode is available."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PAGEINDEX_API_KEY:
        CACHE_PATH.write_text('{"status": "local_vectorless"}\n', encoding="utf-8")
        print("Using local vectorless fallback: PAGEINDEX_API_KEY not set")
        return
    CACHE_PATH.write_text('{"status": "local_vectorless", "external_key_detected": true}\n', encoding="utf-8")
    print("Using local vectorless fallback; no external upload is required.")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Search headings and text directly, without embeddings or an external API."""
    if top_k <= 0 or not query.strip():
        return []

    from .task4_chunking_indexing import chunk_documents, load_documents

    stopwords = {
        "about", "and", "are", "can", "for", "from", "how", "the", "what",
        "when", "where", "which", "with", "các", "cho", "của", "là", "một",
        "những", "theo", "trong", "và",
    }
    query_tokens = [
        token
        for token in re.findall(r"[\w-]+", query.lower(), flags=re.UNICODE)
        if len(token) > 1 and token not in stopwords
    ]
    if not query_tokens:
        return []

    ranked = []
    for chunk in chunk_documents(load_documents()):
        metadata = chunk["metadata"]
        title = metadata.get("title", "").lower()
        haystack = f"{title} {metadata.get('source', '')} {chunk['content']}".lower()
        matched = sum(token in haystack for token in query_tokens)
        if not matched:
            continue
        title_matches = sum(token in title for token in query_tokens)
        score = (matched + 0.5 * title_matches) / len(query_tokens)
        ranked.append(
            {
                "id": chunk["id"],
                "content": chunk["content"],
                "score": float(score),
                "metadata": metadata,
                "retrieval_method": "pageindex",
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    return ranked[:top_k]


if __name__ == "__main__":
    upload_documents()
