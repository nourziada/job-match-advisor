import numpy as np
import json
import os
from config import DATA_DIR

CHUNKS_PATH = os.path.join(DATA_DIR, "cv_chunks.json")
VECTORS_PATH = os.path.join(DATA_DIR, "cv_vectors.npy")
META_PATH = os.path.join(DATA_DIR, "cv_index_meta.json")


def save_index(chunks: list[str], vectors: np.ndarray) -> None:
    """Store the chunk texts as JSON and their vectors as a numpy file."""
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(VECTORS_PATH, vectors)


def load_index() -> tuple[list[str], np.ndarray]:
    """Load the stored chunk texts and their vectors."""
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load(VECTORS_PATH)
    return chunks, vectors


def index_exists() -> bool:
    """True when a usable index is already on disk."""
    return os.path.exists(CHUNKS_PATH) and os.path.exists(VECTORS_PATH)


def save_index_meta(fingerprint: str, source_name: str = "", chunk_count: int = 0) -> None:
    """Record which CV the current index was built from."""
    meta = {
        "fingerprint": fingerprint,
        "source_name": source_name,
        "chunk_count": chunk_count,
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def load_index_meta() -> dict:
    """Return the stored index metadata, or an empty dict if there is none."""
    if not os.path.exists(META_PATH):
        return {}
    try:
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
