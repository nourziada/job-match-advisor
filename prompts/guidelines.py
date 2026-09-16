import os

from config import DATA_DIR

GUIDELINES_PATH = os.path.join(DATA_DIR, "guidelines.txt")

# Only the decision policy lives here, because this is what a user may
# reasonably want to tune. The operational parts of the prompt - the tool
# schema, "the posting is the source of truth", and the rule to tie every
# judgement to CV evidence - stay in the code, since editing them by mistake
# would break the tool.
DEFAULT_GUIDELINES = """Follow these three steps in order.

Step 1 - Classify every requirement in the posting as CORE or SECONDARY:
- CORE: named in the job title, or listed as a primary language or framework, \
or written under a "Requirements" / "Required" / "Must have" heading.
- SECONDARY: everything else. This includes tools and IDEs, items under a \
"Nice to have" / "Preferred" / "Bonus" heading, and any item offered as one \
of several alternatives ("X or Y or similar").

Step 2 - Count how many CORE requirements are missing from the CV.
Missing SECONDARY requirements are normal and expected in almost every \
posting. They MUST NOT lower the decision on their own. List them under \
missing_skills for the user's awareness, but do not let them change the \
decision.

Step 3 - Apply the first rule below that matches. The rules are mutually \
exclusive, so exactly one of them applies:
- "do_not_apply": any hard constraint fails, OR two or more CORE requirements \
are missing.
- "apply_with_caution": all hard constraints pass AND exactly one CORE \
requirement is missing, OR the CV shows one to two years less experience \
than requested.
- "apply": all hard constraints pass AND every CORE requirement is present in \
the CV. Missing SECONDARY items do not prevent this decision.

Apply the hard constraints exactly as defined in your system instructions. In \
particular, a hard constraint that the posting never mentions caps the \
decision at "apply_with_caution" - it does not force "do_not_apply"."""


def load_guidelines() -> str:
    """Return the stored guidelines, writing the defaults on first use."""
    if not os.path.exists(GUIDELINES_PATH):
        save_guidelines(DEFAULT_GUIDELINES)
        return DEFAULT_GUIDELINES

    with open(GUIDELINES_PATH, "r", encoding="utf-8") as f:
        text = f.read().strip()

    return text or DEFAULT_GUIDELINES


def save_guidelines(text: str) -> None:
    """Persist the guidelines so they load automatically next time."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(GUIDELINES_PATH, "w", encoding="utf-8") as f:
        f.write(text.strip())


def reset_guidelines() -> str:
    """Restore and return the default guidelines."""
    save_guidelines(DEFAULT_GUIDELINES)
    return DEFAULT_GUIDELINES
