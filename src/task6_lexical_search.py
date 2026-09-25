"""Task 6 - Lexical search with BM25."""

import re

from .task4_chunking_indexing import chunk_documents, load_documents


CORPUS: list[dict] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\w']+", text.lower(), flags=re.UNICODE)


def _load_corpus() -> list[dict]:
    global CORPUS
    if not CORPUS:
        CORPUS = chunk_documents(load_documents())
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Create a BM25 index from the same chunk corpus used by Task 4."""
    from rank_bm25 import BM25Okapi

    tokenized = [_tokenize(item["content"]) for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Return BM25 SearchResult objects sorted by score descending."""
    corpus = _load_corpus()
    if top_k <= 0 or not query.strip() or not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    query_tokens = _tokenize(query)
    raw_scores = bm25.get_scores(query_tokens)

    ranked = []
    for index, item in enumerate(corpus):
        content_tokens = set(_tokenize(item["content"]))
        overlap = sum(1 for token in query_tokens if token in content_tokens)
        # BM25 can produce zero or negative IDF on tiny corpora. Keep a small
        # lexical-overlap component so exact matches still rank deterministically.
        score = max(float(raw_scores[index]), 0.0) + overlap
        ranked.append((score, index))
    ranked.sort(key=lambda pair: pair[0], reverse=True)

    results = []
    for score, index in ranked[:top_k]:
        item = corpus[index]
        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": score,
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )
    return results


if __name__ == "__main__":
    for result in lexical_search("Hoi An ancient town", top_k=3):
        print(result)
