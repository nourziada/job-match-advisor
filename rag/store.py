import numpy as np
import json
import os
from config import DATA_DIR

CHUNKS_PATH = os.path.join(DATA_DIR, "cv_chunks.json")
VECTORS_PATH = os.path.join(DATA_DIR, "cv_vectors.npy")

def save_index(chunks: list[str], vectors: np.ndarray) -> None:
    """يخزّن النصوص في ملف JSON والمتجهات في ملف numpy."""
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(VECTORS_PATH, vectors)


def load_index() -> tuple[list[str], np.ndarray]:
    """يحمّل النصوص والمتجهات المخزّنة."""
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load(VECTORS_PATH)
    return chunks, vectors