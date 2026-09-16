import json
import os

from config import BASE_DIR

# Paths are resolved from the project root rather than the working directory,
# so the evaluation runs the same from a terminal or from an IDE run button.
MANUAL_PATH = os.path.join(BASE_DIR, "eval", "dataset.json")
GENERATED_PATH = os.path.join(BASE_DIR, "eval", "dataset_generated.json")


def load_dataset(path: str = MANUAL_PATH) -> list:
    """Read test cases from a JSON file and return them as a list."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_tagged(path: str, source: str) -> list:
    """Read a dataset file and tag every case with its source.

    A missing file yields an empty list so the evaluation still runs before
    any cases have been generated.
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
    """Merge the manual and generated cases into a single list.

    Manual cases come first and win on duplicates, compared by job posting
    text, since they are the more trustworthy source.
    """
    manual = _load_tagged(manual_path, "manual")
    generated = _load_tagged(generated_path, "generated")

    merged = []
    seen = set()
    for case in manual + generated:
        key = case.get("prompt_inputs", {}).get("job_posting", "").strip()
        if key and key in seen:
            continue
        seen.add(key)
        merged.append(case)

    print(f"Datasets loaded successfully: {len(merged)} records")
    return merged
