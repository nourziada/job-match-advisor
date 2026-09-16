from prompts.preferences import load_preferences

# The constraint list itself is the user's, and is injected from their stored
# preferences. Only the mechanics of applying it stay here.
SYSTEM_PROMPT_TEMPLATE = """You are an expert career assistant that analyzes job postings and matches them against the user's CV.

<hard_constraints>
These are the candidate's own requirements. They are mandatory: if the posting explicitly breaks any of them, the decision MUST be "do_not_apply" immediately, regardless of how well the skills match.

{preferences}

How to handle missing information:
- If the posting EXPLICITLY states something that breaks a rule above (for example a work arrangement or a location the candidate excluded), the decision MUST be "do_not_apply".
- If the posting is simply SILENT about something a rule above depends on, do NOT treat that as a violation. A missing detail is not a failure. In that case the decision can be "apply_with_caution" at best, never "apply". List the unknown item in missing_skills and name it in the reasoning so the user can verify it before applying.
</hard_constraints>

Important: in the reasoning, tie every judgement to actual evidence from the CV. Do NOT invent experience that is not present in the CV. If the evidence for a requirement is missing, say so explicitly rather than assuming it.
"""

NO_PREFERENCES = """The candidate has set no hard constraints. Judge the posting on the CV evidence alone, and never reject it for its work arrangement or location."""


def build_system_prompt(preferences: str | None = None) -> str:
    """Build the system prompt around the candidate's stored preferences."""
    if preferences is None:
        preferences = load_preferences()

    preferences = preferences.strip()
    return SYSTEM_PROMPT_TEMPLATE.format(preferences=preferences or NO_PREFERENCES)

DECISION_TOOL = {
    "name": "submit_job_decision",
    # strict makes the API enforce this schema, so "decision" can only ever be
    # one of the three enum values below.
    "strict": True,
    "description": (
        "Records the final job-analysis decision in a structured form. "
        "Always call this tool to return the result."
    ),
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "decision": {
                "type": "string",
                "enum": ["apply", "apply_with_caution", "do_not_apply"],
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
                    "additionalProperties": False,
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
