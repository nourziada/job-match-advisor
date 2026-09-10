import json
import os

# الملفان اللي بنقرأ منهم:
#   dataset.json           -> حالاتك اليدوية (من تجاربك الحقيقية)
#   dataset_generated.json -> الحالات اللي Claude ولّدها (generate_dataset.py)
MANUAL_PATH = "eval/dataset.json"
GENERATED_PATH = "eval/dataset_generated.json"


def load_dataset(path: str = MANUAL_PATH) -> list:
    """يقرأ حالات الاختبار من ملف JSON ويرجّعها كـ list."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_tagged(path: str, source: str) -> list:
    """
    يقرأ ملف حالات ويحطّ على كل حالة علامة مصدرها.
    لو الملف مش موجود بيرجّع list فاضية بدل ما يقع — عشان التقييم يشتغل
    حتى لو لسه ماولّدتش حالات.
    """
    if not os.path.exists(path):
        return []

    cases = load_dataset(path)
    for case in cases:
        case["source"] = source
    return cases


def load_all_datasets(
    manual_path: str = MANUAL_PATH,
    generated_path: str = GENERATED_PATH,
) -> list:
    """
    يدمج المصدرين في list واحدة: الحالات اليدوية الأول، وبعدها المولّدة.

    - كل حالة بتتوسم بـ source = "يدوي" أو "مولّد" عشان تعرف في التقرير
      إذا كانت الدرجة الواطية جاية من حالة حقيقية ولا من حالة صناعية.
    - الحالات المكرّرة (نفس نص الوظيفة) بتتشال، والنسخة اليدوية هي اللي بتفضل
      لأنها الأوثق.
    """
    manual = _load_tagged(manual_path, "يدوي")
    generated = _load_tagged(generated_path, "مولّد")

    merged = []
    seen = set()
    for case in manual + generated:
        # بنقارن بنص الوظيفة نفسه عشان نمسك التكرار
        key = case.get("prompt_inputs", {}).get("job_posting", "").strip()
        if key and key in seen:
            continue
        seen.add(key)
        merged.append(case)

    print(f"Datasets loaded successfully: {len(merged)} records")
    return merged
