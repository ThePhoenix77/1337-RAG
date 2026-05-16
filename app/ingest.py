from __future__ import annotations
from pathlib import Path

try:
    from .chunking import chunk_text
    from .embeddings import generate_embedding
    from .pinecone_service import get_index
except ImportError:  # pragma: no cover - fallback for direct script execution
    from chunking import chunk_text
    from embeddings import generate_embedding
    from pinecone_service import get_index


def ingest_document(path: str | Path = "data/notes.txt") -> int:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")

    chunks = chunk_text(text)
    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)
        vectors.append(
            {
                "id": f"chunk-{i}",
                "values": embedding,
                "metadata": {"text": chunk},
            }
        )

    index = get_index()
    index.upsert(vectors=vectors)
    return len(vectors)


if __name__ == "__main__":
    count = ingest_document()
    print(f"Document indexed successfully. {count} chunks uploaded.")