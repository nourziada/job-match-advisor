import hashlib

from rag.pdf_loader import load_cv_text
from rag.chunker import chunk_cv
from rag.embedder import embed_texts
from rag.store import save_index, save_index_meta, load_index_meta, index_exists


def file_fingerprint(file_bytes: bytes) -> str:
    """Content hash used to tell whether a CV has actually changed."""
    return hashlib.sha256(file_bytes).hexdigest()


def needs_rebuild(fingerprint: str) -> bool:
    """True when the stored index was not built from this exact file.

    Embedding a CV costs time and money, so the index is only rebuilt when the
    uploaded file differs from the one already indexed.
    """
    if not index_exists():
        return True
    return load_index_meta().get("fingerprint") != fingerprint


def build_index_from_text(text: str, fingerprint: str = "", source_name: str = "") -> int:
    """Chunk, embed and store a CV given its extracted text."""
    chunks = chunk_cv(text)
    if not chunks:
        raise ValueError("No text could be extracted from the CV.")

    vectors = embed_texts(chunks)
    save_index(chunks, vectors)
    save_index_meta(fingerprint, source_name, len(chunks))
    return len(chunks)


def build_index_from_bytes(pdf_bytes: bytes, source_name: str = "") -> int:
    """Build the index from an uploaded PDF's raw bytes."""
    return build_index_from_text(
        load_cv_text(pdf_bytes),
        fingerprint=file_fingerprint(pdf_bytes),
        source_name=source_name,
    )


def build_index_from_path(pdf_path: str) -> int:
    """Build the index from a PDF on disk."""
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return build_index_from_bytes(pdf_bytes, source_name=pdf_path)
