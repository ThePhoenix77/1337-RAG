from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import ollama

try:
    from .embeddings import generate_embedding
    from .pinecone_service import get_index
except ImportError:  # pragma: no cover - fallback for direct script execution
    from embeddings import generate_embedding
    from pinecone_service import get_index


DEFAULT_MODEL = "mistral"
DEFAULT_TOP_K = 3


@dataclass(slots=True)
class RetrievedChunk:
    score: float | None
    text: str


def retrieve_chunks(query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievedChunk]:
    query_embedding = generate_embedding(query)
    index = get_index()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    if isinstance(results, dict):
        matches = results.get("matches", [])
    elif hasattr(results, "matches"):
        matches = results.matches
    else:
        matches = []

    chunks: list[RetrievedChunk] = []

    for match in matches:
        metadata = match.get("metadata", {}) or {}
        text = metadata.get("text", "")
        if text:
            chunks.append(
                RetrievedChunk(
                    score=match.get("score"),
                    text=text,
                )
            )

    return chunks


def build_context(chunks: Iterable[RetrievedChunk]) -> str:
    return "\n\n".join(chunk.text for chunk in chunks)


def build_prompt(query: str, context: str) -> str:
    return f"""You are a helpful AI assistant.

Answer the question ONLY using the provided context.

If the answer is not found in the context, say "I don't know."

Context:
{context}

Question:
{query}

Answer:
"""


def answer_query(
    query: str,
    model: str = DEFAULT_MODEL,
    top_k: int = DEFAULT_TOP_K,
) -> tuple[str, list[RetrievedChunk]]:
    chunks = retrieve_chunks(query, top_k=top_k)
    context = build_context(chunks)
    prompt = build_prompt(query, context)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response["message"]["content"]
    return content, chunks


def stream_answer_query(
    query: str,
    model: str = DEFAULT_MODEL,
    top_k: int = DEFAULT_TOP_K,
):
    chunks = retrieve_chunks(query, top_k=top_k)
    context = build_context(chunks)
    prompt = build_prompt(query, context)

    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    def chunk_stream():
        for part in stream:
            yield part["message"]["content"]

    return chunk_stream(), chunks