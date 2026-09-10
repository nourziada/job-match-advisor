from textwrap import dedent
import json
from tools.claude_client import get_client
from config import CLAUDE_MODEL

EVAL_TEMPLATE = dedent("""
Your task is to evaluate the following AI-generated solution with EXTREME RIGOR.

Original task description:
<task_description>
{task_description}
</task_description>

Original task inputs:
<task_inputs>
{prompt_inputs}
</task_inputs>

Solution to Evaluate:
<solution>
{output}
</solution>

Criteria you should use to evaluate the solution:
<criteria>
{solution_criteria}
</criteria>

Scoring Guidelines:
* Score 1-3: Solution fails to meet one or more MANDATORY requirements
* Score 4-6: Solution meets all mandatory requirements but has significant deficiencies in secondary criteria
* Score 7-8: Solution meets all mandatory requirements and most secondary criteria, with minor issues
* Score 9-10: Solution meets all mandatory and secondary criteria

IMPORTANT SCORING INSTRUCTIONS:
* Grade the output based ONLY on the listed criteria. Do not add your own extra requirements.
* If a solution meets all of the mandatory and secondary criteria give it a 10.
* ANY violation of a mandatory requirement MUST result in a score of 3 or lower.
* The full 1-10 scale should be utilized - don't hesitate to give low scores when warranted.

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON only.
""")

GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "strengths":  {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "reasoning":  {"type": "string"},
        "score":      {"type": "integer", "description": "A number between 1 and 10"},
    },
    "required": ["strengths", "weaknesses", "reasoning", "score"],
    "additionalProperties": False,
}

def grade(test_case: dict, output: str) -> dict:
    """Model Grader: يقيّم مخرَج الأداة مقابل معايير الحالة، ويرجّع score من 10 + الأسباب."""
    client = get_client()
    prompt = EVAL_TEMPLATE.format(
        task_description=test_case["task_description"],
        prompt_inputs=json.dumps(test_case["prompt_inputs"], ensure_ascii=False),
        output=output,
        solution_criteria="\n".join(test_case["solution_criteria"]),
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "disabled"},
        output_config={"format": {"type": "json_schema", "schema": GRADE_SCHEMA}},
    )
    return json.loads("".join(b.text for b in response.content if b.type == "text"))
