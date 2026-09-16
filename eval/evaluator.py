from tools.analyzer import analyze_job, extract_requirements, make_decision
from eval.grader import grade
import json


def run_prompt(job_text: str, cv_text: str | None = None) -> str:
    """Run the tool on one posting and return its output as JSON text.

    With no cv_text, analyze_job runs the normal path against the stored CV.
    With a cv_text, the same chain is composed here so a case can supply its
    own CV, which keeps the generated cases independent of any single CV.
    """
    if cv_text is None:
        decision = analyze_job(job_text)
    else:
        requirements = extract_requirements(job_text)
        decision = make_decision(job_text, requirements, cv_text)

    return json.dumps(decision, ensure_ascii=False, indent=2)


def run_test_case(test_case: dict) -> dict:
    """Run the tool on one case and grade its output with the model grader."""
    inputs = test_case["prompt_inputs"]
    job_text = inputs["job_posting"]
    cv_text = inputs.get("cv")

    print(f"> {test_case.get('scenario', '')[:70]}")
    output = run_prompt(job_text, cv_text)
    evaluation = grade(test_case, output)
    print(f"  score: {evaluation['score']}/10")

    return {
        "scenario": test_case["scenario"],
        "source": test_case.get("source", "-"),
        "job_posting": job_text,
        "cv": cv_text or "(stored CV in data/ - manual case)",
        "solution_criteria": test_case["solution_criteria"],
        "output": output,
        "score": evaluation["score"],
        "strengths": evaluation["strengths"],
        "weaknesses": evaluation["weaknesses"],
        "reasoning": evaluation["reasoning"],
    }


def run_eval(dataset: list) -> list:
    """Run every case and return the results."""
    return [run_test_case(tc) for tc in dataset]
