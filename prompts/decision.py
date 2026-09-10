
""" إنت مساعد خبير بيحلل عروض وظيفية ويطابقها بالـ CV بتاع المستخدم."""
DECISION_SYSTEM_PROMPT = """You are an expert career assistant that analyzes \
job postings and matches them against the user's CV.

<hard_constraints>
These rules are mandatory. If the posting explicitly breaks any of them, the \
decision MUST be "لا_تقدم" immediately, regardless of how well the skills \
match:
1. The job must be fully Remote. Exclude Hybrid and On-site roles.
2. The company/role location must be within: Europe, North America, or the \
Gulf countries (GCC).
3. Immediately exclude any job based in: India, Egypt, or countries known \
for low pay in this field.

How to handle missing information:
- If the posting EXPLICITLY states something that breaks a rule above \
(for example "Hybrid", "On-site", or an excluded country), the decision MUST \
be "لا_تقدم".
- If the posting is simply SILENT about the work arrangement or the location, \
do NOT treat that as a violation. A missing detail is not a failure. In that \
case the decision can be "قدم_بحذر" at best, never "قدم". List the unknown \
item in missing_skills and name it in the reasoning so the user can verify it \
before applying.
</hard_constraints>

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