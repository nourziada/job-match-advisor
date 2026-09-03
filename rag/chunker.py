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
    "خبرات", "الخبرات", "المهارات", "التعليم", "المؤهلات",
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
    """
    يحوّل أي سطر لصيغة موحّدة للمقارنة: حروف/أرقام بس، من غير مسافات ولا رموز.
    ده اللي بيحل مشكلة الـ PDF اللي بيخزّن العناوين مكسورة.
    مثال: "T ECHNICAL   Skills" → "technicalskills"
          "PROFESSIONAL  EXPERIENC E" → "professionalexperience"
    """
    return re.sub(r"[\W_]+", "", s.lower())


# نجهّز نسخة منظّفة من قائمة العناوين مرة واحدة (بدل ما ننظّفها كل مرة)
_HEADER_KEYS = {_key(h) for h in SECTION_HEADERS}

def split_by_headers(text: str) -> list[str]:
    """
    يقسّم النص عند الأسطر اللي هي عناوين أقسام فعلية.
    بيمشي سطر سطر: لو لقى سطر عنوان (بعد التنظيف)، يبدأ قسم جديد.
    """
    sections, current = [], []
    for line in text.splitlines():
        # لو السطر ده عنوان معروف، وفيه محتوى متجمّع قبله → اقفل القسم اللي فات
        if _key(line) in _HEADER_KEYS and current:
            sections.append("\n".join(current))
            current = []
        current.append(line)
    # اضف آخر قسم متبقّي بعد نهاية اللوب
    if current:
        sections.append("\n".join(current))
    return [s.strip() for s in sections if s.strip()]

def chunk_cv(text: str, max_section_length: int = 1200, min_length: int = 50) -> list[str]:
    """
       التقطيع الهجين:
       1. حاول التقسيم بالعناوين الفعلية (Structure-based حقيقي)
       2. أي قسم أطول من الحد الأقصى → يتقطّع تاني بالحجم + overlap
       3. لو مفيش عناوين اتلقت خالص → fallback كامل لـ Size-based
       """

    sections = split_by_headers(text)

    # مفيش عناوين واضحة؟ ارجع للـ fallback الآمن مباشرة
    if len(sections) <= 1:
        return chunk_by_size(text)

    chunks = []
    for section in sections:
        if len(section) < min_length:
            continue
        if len(section) > max_section_length:
            # القسم طويل زيادة (زي خبرة عمل مفصّلة) → قطّعه بالحجم
            chunks.extend(chunk_by_size(section))
        else:
            chunks.append(section)

    return chunks