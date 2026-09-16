import re

SECTION_HEADERS = [
    "experience",
    "work experience",
    "professional experience",
    "education",
    "academic background",
    "extracurricular & volunteer activities",
    "skills",
    "technical skills",
    "core competencies",
    "projects",
    "certifications",
    "summary",
    "profile",
    "career profile",
]


def chunk_by_size(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else len(text)
    return chunks


def _key(s: str) -> str:
    """Normalise a line to letters and digits only, for header matching.

    PDF extraction often breaks headers apart, so "T ECHNICAL  Skills"
    and "TECHNICAL SKILLS" both collapse to "technicalskills".
    """
    return re.sub(r"[\W_]+", "", s.lower())


_HEADER_KEYS = {_key(h) for h in SECTION_HEADERS}


def split_by_headers(text: str) -> list[str]:
    """Split the text at lines that are recognised section headers."""
    sections, current = [], []
    for line in text.splitlines():
        if _key(line) in _HEADER_KEYS and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        sections.append("\n".join(current))
    return [s.strip() for s in sections if s.strip()]


def chunk_cv(text: str, max_section_length: int = 1200, min_length: int = 50) -> list[str]:
    """Split a CV by section headers, falling back to fixed-size chunks.

    Sections longer than max_section_length are split again by size, and a CV
    with no recognisable headers is chunked by size throughout.
    """
    sections = split_by_headers(text)

    if len(sections) <= 1:
        return chunk_by_size(text)

    chunks = []
    for section in sections:
        if len(section) < min_length:
            continue
        if len(section) > max_section_length:
            chunks.extend(chunk_by_size(section))
        else:
            chunks.append(section)

    return chunks
