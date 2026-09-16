import numpy as np
from rag.embedder import embed_one
from rag.store import load_index


def cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    """Cosine similarity between the query vector and every chunk vector."""
    query_norm = query_vec / np.linalg.norm(query_vec)
    docs_norm = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
    return docs_norm @ query_norm


def search_cv(query: str, top_k: int = 3) -> list[str]:
    """Return the top_k CV chunks most relevant to the query."""
    chunks, vectors = load_index()
    query_vec = embed_one(query)
    scores = cosine_similarity(query_vec, vectors)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices]
