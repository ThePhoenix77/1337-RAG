from __future__ import annotations

import hashlib
from pathlib import Path


def compute_file_hash(path: str | Path) -> str:
    """Compute SHA256 hash of a file."""
    path = Path(path)
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_cache_path(doc_path: str | Path) -> Path:
    """Get the cache file path for a document."""
    doc_path = Path(doc_path)
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / f"{doc_path.stem}.hash"
    return cache_file


def has_file_changed(doc_path: str | Path) -> bool:
    """Check if a document has changed since last indexing."""
    doc_path = Path(doc_path)
    if not doc_path.exists():
        return False

    current_hash = compute_file_hash(doc_path)
    cache_path = get_cache_path(doc_path)

    if not cache_path.exists():
        return True

    cached_hash = cache_path.read_text().strip()
    return current_hash != cached_hash


def update_cache(doc_path: str | Path) -> None:
    """Update the cached hash for a document."""
    doc_path = Path(doc_path)
    current_hash = compute_file_hash(doc_path)
    cache_path = get_cache_path(doc_path)
    cache_path.write_text(current_hash)
