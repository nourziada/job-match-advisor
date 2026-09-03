from pypdf import PdfReader

def load_cv_text(pdf_path: str) -> str:
    """يقرأ ملف PDF ويرجّع كل النص كـ string واحد."""
    reader = PdfReader(pdf_path)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:  # بعض الصفحات ممكن ترجع None
            pages_text.append(text)
    return "\n".join(pages_text)