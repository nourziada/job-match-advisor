import numpy as np
from rag.embedder import embed_one
from rag.store import load_index

def cosine_similarity(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    """
    يحسب تشابه جيب التمام بين متجه السؤال وكل متجهات الـ chunks.
    القيمة بين -1 و 1، الأعلى = الأكثر تشابهًا.
    """
    query_norm = query_vec / np.linalg.norm(query_vec)
    docs_norm = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
    return docs_norm @ query_norm

def search_cv(query: str, top_k: int = 3) -> list[str]:
    """يرجّع أكثر top_k أجزاء من الـ CV صلة بالسؤال."""
    chunks, vectors = load_index()
    query_vec = embed_one(query)
    scores = cosine_similarity(query_vec, vectors)
    # ترتيب الفهارس من الأعلى تشابهًا للأقل، وأخذ أول top_k
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices]

