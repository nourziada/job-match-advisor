import sys
import json

from tools.claude_client import get_client
from config import CLAUDE_MODEL

GENERATION_PROMPT = """Generate an evaluation dataset for the following task.

<task_description>
Analyze a job posting against a Senior Laravel/PHP developer's CV
(9+ years experience, ex-Team Lead) and give a clear apply / apply-with-caution
/ do-not-apply decision.
</task_description>

Generate {n} diverse test cases. Vary the scenarios to cover:
- A perfect match (should clearly apply)
- A partial match (missing a secondary skill or slightly less experience)
- A wrong-framework candidate (strong but in Node/Python, not Laravel)
- A hard-constraint failure (on-site, or a location that should be excluded)

For each test case return an object with EXACTLY these fields:
- "task_description": the task (same for all)
- "scenario": a short description of what this case tests
- "prompt_inputs": an object with a "job_posting" field containing a realistic full posting
- "solution_criteria": an array of 2-4 criteria a good answer must satisfy"""

# شكل ثابت بنفرضه على الرد — بيضمن إن الناتج JSON صالح دايمًا،
# فمش محتاجين نعتمد على "Respond ONLY with JSON" ولا ننضّف علامات ```
DATASET_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "task_description": {"type": "string"},
            "scenario": {"type": "string"},
            "prompt_inputs": {
                "type": "object",
                "properties": {"job_posting": {"type": "string"}},
                "required": ["job_posting"],
                "additionalProperties": False,
            },
            "solution_criteria": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "task_description",
            "scenario",
            "prompt_inputs",
            "solution_criteria",
        ],
        "additionalProperties": False,
    },
}


def generate_dataset(
    n: int = 6,
    save_path: str = "eval/dataset_generated.json",
) -> list:
    """
    يخلّي Claude يولّد حالات اختبار إضافية ويحفظها في ملف منفصل.

    ملاحظة مهمة: بيحفظ في dataset_generated.json — مش dataset.json —
    عشان ميمسحش حالاتك اليدوية. الاتنين بيتدمجوا في load_all_datasets().
    """
    client = get_client()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": GENERATION_PROMPT.format(n=n)}],
        output_config={"format": {"type": "json_schema", "schema": DATASET_SCHEMA}},
    )

    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            "الرد اتقطع قبل ما يخلص — جرّب عدد حالات أقل أو زوّد max_tokens."
        )

    dataset = json.loads(
        "".join(b.text for b in response.content if b.type == "text")
    )

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"تم حفظ {len(dataset)} حالة في {save_path}")

    return dataset


def main():
    # uv run eval/generate_dataset.py        -> 6 حالات
    # uv run eval/generate_dataset.py 4      -> 4 حالات
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    generate_dataset(n=n)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
