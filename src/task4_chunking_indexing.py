"""Task 4 - Chunking, embedding and indexing."""

from pathlib import Path
import re


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "sklearn-hashing-vectorizer"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Create deterministic local embeddings shared by indexing and querying."""
    if not texts:
        return []

    from sklearn.feature_extraction.text import HashingVectorizer

    vectorizer = HashingVectorizer(
        n_features=EMBEDDING_DIM,
        alternate_sign=False,
        norm="l2",
        lowercase=True,
        ngram_range=(1, 2),
    )
    matrix = vectorizer.transform(texts)
    return matrix.astype(float).toarray().tolist()


def get_collection():
    """Open a Chroma collection configured for cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _metadata_from_markdown(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    first_heading = next(
        (line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")),
        path.stem.replace("-", " ").title(),
    )
    source_match = re.search(r"\*\*Source:\*\*\s*(.+)", text)
    source = source_match.group(1).strip() if source_match else path.name
    url = source if source.startswith(("http://", "https://")) else None
    doc_type = "legal" if path.parent.name == "legal" else "news"
    return {
        "source": source,
        "title": first_heading,
        "doc_type": doc_type,
        "url": url,
    }


def load_documents() -> list[dict]:
    """Read standardized Markdown files into Document dictionaries."""
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        documents.append(
            {
                "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
                "content": content,
                "metadata": _metadata_from_markdown(path),
            }
        )
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split documents into stable chunks with chunk_index metadata."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        split_text = splitter.split_text
    except ImportError:
        # Keep contract tests and basic offline use available in restricted
        # environments. Normal installations use the declared LangChain
        # splitter above.
        def split_text(text: str) -> list[str]:
            step = CHUNK_SIZE - CHUNK_OVERLAP
            return [text[start : start + CHUNK_SIZE] for start in range(0, len(text), step)]

    chunks = []
    for document in documents:
        for index, text in enumerate(split_text(document["content"])):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunks.append(
                {
                    "id": f"{document['id']}::chunk-{index}",
                    "content": clean_text,
                    "metadata": {**document["metadata"], "chunk_index": index},
                }
            )
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Attach embeddings to each chunk without mutating the input list."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks into ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    chroma_metadatas = [
        {key: ("" if value is None else value) for key, value in chunk["metadata"].items()}
        for chunk in chunks
    ]
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=chroma_metadatas,
    )


def run_pipeline() -> None:
    """Run load, chunk, embed and index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
