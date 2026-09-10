from tools.analyzer import analyze_job
from eval.grader import grade
import json


def run_prompt(job_text: str) -> str:
    """يشغّل الأداة على وظيفة واحدة، ويرجّع المخرَج كنص JSON للتقييم."""
    decision = analyze_job(job_text)
    return json.dumps(decision, ensure_ascii=False, indent=2)

def run_test_case(test_case: dict) -> dict:
    """يشغّل الأداة على حالة، ويقيّم مخرَجها بالـ Model Grader."""
    job_text = test_case["prompt_inputs"]["job_posting"]
    output = run_prompt(job_text)
    print(f"Run the Eval Prompt , and make the decision")
    evaluation = grade(test_case, output)
    print(f"Run the Grading")
    return {
        "scenario": test_case["scenario"],
        "source": test_case.get("source", "—"),
        "job_posting": job_text,
        "solution_criteria": test_case["solution_criteria"],
        "output": output,
        "score": evaluation["score"],
        "strengths": evaluation["strengths"],
        "weaknesses": evaluation["weaknesses"],
        "reasoning": evaluation["reasoning"],
    }


def run_eval(dataset: list) -> list:
    """يشغّل كل الحالات ويرجّع النتائج."""
    return [run_test_case(tc) for tc in dataset]