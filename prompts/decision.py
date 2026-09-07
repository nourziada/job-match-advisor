
""" إنت مساعد خبير بيحلل عروض وظيفية ويطابقها بالـ CV بتاع المستخدم."""
DECISION_SYSTEM_PROMPT = """You are an expert career assistant that analyzes \
job postings and matches them against the user's CV.

<hard_constraints>
These rules are mandatory. If ANY of them fails, the decision MUST be \
"لا_تقدم" immediately, regardless of how well the skills match:
1. The job must be fully Remote. Exclude Hybrid and On-site roles.
2. The company/role location must be within: Europe, North America, or the \
Gulf countries (GCC).
3. Immediately exclude any job based in: India, Egypt, or countries known \
for low pay in this field.
</hard_constraints>

<decision_rules>
- "قدم": all hard constraints pass AND there is a strong match on the core \
required skills.
- "قدم_بحذر": all hard constraints pass BUT the match is partial (a missing \
secondary skill, or one-to-two years less experience than requested).
- "لا_تقدم": any hard constraint fails, OR there is a fundamental gap in a \
core required skill.
</decision_rules>

Important: in the reasoning, tie every judgement to actual evidence from the \
CV. Do NOT invent experience that is not present in the CV. If the evidence \
for a requirement is missing, say so explicitly rather than assuming it.
"""

# ---------------------------------------------------------------------------
# 2. Decision tool: the fixed JSON Schema Claude must fill in
# ---------------------------------------------------------------------------

DECISION_TOOL = {
    "name": "submit_job_decision",
    "description": (
        "Records the final job-analysis decision in a structured form. "
        "Always call this tool to return the result."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "decision": {
                "type": "string",
                "enum": ["قدم", "قدم_بحذر", "لا_تقدم"],
                "description": "The final decision.",
            },
            "confidence": {
                "type": "integer",
                "description": "Confidence in the decision, from 0 to 100.",
            },
            "matched_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required skills that ARE present in the CV.",
            },
            "missing_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required skills that are missing from the CV.",
            },
            "reasoning": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion": {
                            "type": "string",
                            "description": "The criterion being evaluated "
                                           "(e.g. a skill, experience level, remote, location).",
                        },
                        "verdict": {
                            "type": "string",
                            "description": "The outcome of evaluating this "
                                           "criterion (e.g. match / partial / fail).",
                        },
                        "source": {
                            "type": "string",
                            "description": "The supporting evidence from the CV, "
                                           "or a note that no evidence was found.",
                        },
                    },
                    "required": ["criterion", "verdict", "source"],
                },
                "description": "Per-criterion breakdown; each judgement tied "
                               "to its evidence.",
            },
        },
        "required": [
            "decision",
            "confidence",
            "matched_skills",
            "missing_skills",
            "reasoning",
        ],
    },
}