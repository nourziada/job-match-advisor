from io import BytesIO

from pypdf import PdfReader


def load_cv_text(source) -> str:
    """Read a PDF and return all of its text as a single string.

    Accepts a file path or the raw bytes of an uploaded file, so the same
    loader serves both the CLI and the Streamlit uploader.
    """
    if isinstance(source, (bytes, bytearray)):
        source = BytesIO(source)

    reader = PdfReader(source)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text)
