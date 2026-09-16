import voyageai
import numpy as np
from config import VOYAGE_API_KEY, VOYAGE_MODEL

client = voyageai.Client(api_key=VOYAGE_API_KEY)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of CV chunks as documents for retrieval."""
    result = client.embed(texts, model=VOYAGE_MODEL, input_type="document")
    return np.array(result.embeddings)


def embed_one(text: str) -> np.ndarray:
    """Embed a single search query."""
    result = client.embed([text], model=VOYAGE_MODEL, input_type="query")
    return np.array(result.embeddings[0])
