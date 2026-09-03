import voyageai
import numpy as np
from config import VOYAGE_API_KEY, VOYAGE_MODEL

client = voyageai.Client(api_key=VOYAGE_API_KEY)

def embed_texts(texts: list[str]) -> np.ndarray:
    """
    يحوّل قائمة نصوص (chunks الـ CV) لمصفوفة متجهات.
    input_type='document' مهم: بيقول لـ Voyage إن دي مستندات هتتخزّن للاسترجاع،
    فبيحسّن التمثيل لهذا الغرض.
    """
    result = client.embed(texts, model=VOYAGE_MODEL, input_type="document")
    return np.array(result.embeddings)

def embed_one(text: str) -> np.ndarray:

    # Embedding User Prompt
    """
    يحوّل نص واحد (سؤال المستخدم) لمتجه.
    input_type='query' هنا — مختلف عن 'document' فوق:
    بيقول لـ Voyage إن ده سؤال بحث، مش مستند للتخزين.
    """
    result = client.embed([text], model=VOYAGE_MODEL, input_type="query")
    return np.array(result.embeddings[0])