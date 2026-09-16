import os
import sys
import json

from tools.claude_client import get_client
from config import CLAUDE_MODEL, BASE_DIR

# Resolved from the project root so the script works from any working directory.
DEFAULT_SAVE_PATH = os.path.join(BASE_DIR, "eval", "dataset_generated.json")

GENERATION_PROMPT = """Generate an evaluation dataset for a job-matching tool.

<task_description>
Given a candidate's CV and a job posting, decide whether the candidate should
apply. The decision is exactly one of: "apply", "apply_with_caution",
"do_not_apply".
</task_description>

Each test case must be SELF-CONTAINED: you invent BOTH the candidate's CV and
the job posting. The tool is judged only on the CV and the posting inside the
case, so never assume any fact that is not written in the CV you wrote.

<hard_constraints>
The tool rejects a posting outright ("do_not_apply") when the posting EXPLICITLY
states any of these, no matter how well the skills match:
1. The work arrangement is Hybrid or On-site (it must be fully Remote).
2. The location is outside Europe, North America, or the Gulf countries (GCC).
3. The job is based in India or Egypt.

If the posting is SILENT about the arrangement or the location, that is NOT a
violation - the decision is capped at "apply_with_caution", never "apply".
</hard_constraints>

<decision_rule>
The tool classifies every requirement as CORE or SECONDARY, then applies the
first rule that matches. Your solution_criteria MUST agree with this rule.

- CORE: named in the job title, or a primary language / framework, or listed
  under a "Requirements" / "Required" / "Must have" heading.
- SECONDARY: everything else - tools, items under "Nice to have" / "Preferred"
  / "Bonus", and any item offered as one of several alternatives ("X or Y").

Decision:
- "do_not_apply": any hard constraint fails, OR 2 or more CORE requirements are
  absent from the CV.
- "apply_with_caution": all hard constraints pass AND exactly 1 CORE requirement
  is absent, OR the CV shows 1-2 years less experience than requested.
- "apply": all hard constraints pass AND every CORE requirement is present in the
  CV. Missing SECONDARY items NEVER prevent "apply".
</decision_rule>

Generate {n} diverse test cases. Cover these shapes, and vary the seniority,
domain, country and tech stack across cases so they are not near-duplicates:
- A perfect match -> "apply"
- Exactly one CORE requirement absent from the CV -> "apply_with_caution"
- A wrong tech stack: 2 or more CORE requirements absent -> "do_not_apply"
- A hard-constraint failure (On-site, or based in India/Egypt) with an
  otherwise perfect CV -> "do_not_apply"

Rules you MUST follow:
- Every job_posting must state the work arrangement AND the location explicitly.
- Write each CV as realistic plain text with clear section headers on their own
  lines: SUMMARY, TECHNICAL SKILLS, PROFESSIONAL EXPERIENCE, EDUCATION.
- Before writing the criteria, re-read the CV you just wrote and COUNT how many
  CORE requirements are genuinely absent from it. The decision you assert must
  be the one <decision_rule> produces from that count.
- Never claim a skill is missing if you wrote it into the CV, and never claim a
  skill is present if you did not.
- Never write a criterion the tool cannot satisfy from the CV and the posting
  alone. It has no memory of other postings, and it reports no salary figures.

For each test case return an object with EXACTLY these fields:
- "task_description": the task (identical for all cases)
- "scenario": one short line describing what this case tests
- "prompt_inputs": an object with a "cv" field and a "job_posting" field
- "solution_criteria": 2-4 criteria, each one prefixed with "[MANDATORY] " or
  "[SECONDARY] ". Exactly one [MANDATORY] criterion must state the expected
  decision verbatim (for example: "[MANDATORY] Concludes with 'apply_with_caution'").
  Mark as [MANDATORY] only what a correct answer MUST contain; everything else
  is [SECONDARY]."""

# Constraining the response shape guarantees valid JSON without relying on
# "respond with JSON only" or stripping code fences.
DATASET_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "task_description": {"type": "string"},
            "scenario": {"type": "string"},
            "prompt_inputs": {
                "type": "object",
                "properties": {
                    "cv": {
                        "type": "string",
                        "description": "The full synthetic CV this case is about.",
                    },
                    "job_posting": {"type": "string"},
                },
                "required": ["cv", "job_posting"],
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
    save_path: str = DEFAULT_SAVE_PATH,
) -> list:
    """Generate extra test cases with Claude and save them to a separate file.

    Each case carries its own synthetic CV, so these cases measure the system's
    logic rather than the fit of one particular CV. Saving to
    dataset_generated.json keeps the manual cases in dataset.json untouched;
    load_all_datasets merges the two.
    """
    client = get_client()

    # Streaming avoids HTTP timeouts at this max_tokens: every case carries a
    # full CV and a full posting, so a batch can run well past 20k tokens.
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=64000,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": GENERATION_PROMPT.format(n=n)}],
        output_config={"format": {"type": "json_schema", "schema": DATASET_SCHEMA}},
    ) as stream:
        response = stream.get_final_message()

    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            "The response was cut off - try fewer cases or raise max_tokens."
        )

    dataset = json.loads(
        "".join(b.text for b in response.content if b.type == "text")
    )

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(dataset)} cases to {save_path}")

    return dataset


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    generate_dataset(n=n)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
