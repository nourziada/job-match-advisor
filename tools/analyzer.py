from tools.claude_client import ask_claude
from rag.search import search_cv

from tools.claude_client import get_client
from config import CLAUDE_MODEL, MAX_TOKENS
from prompts.decision import DECISION_SYSTEM_PROMPT, DECISION_TOOL

# ---------------------------------------------------------------------------
# Chain link 1 — extract the job requirements
# ---------------------------------------------------------------------------

def extract_requirements(job_text: str) -> str:
    """الحلقة 1: يقرأ عرض الوظيفة ويطلّع المتطلبات الأساسية كنص منظّم."""

    prompt = f"""Extract the core requirements from this job posting.
Focus on:
- Required technical skills
- Required years of experience
- Work type (Remote / Hybrid / On-site)
- Company or job location

<job_posting>
{job_text}
</job_posting>

Write the requirements as clear, concise bullet points."""

    return ask_claude(prompt)

# ---------------------------------------------------------------------------
# Chain link 2 — gather supporting evidence from the CV (RAG)
# ---------------------------------------------------------------------------

def gather_cv_evidence(requirements: str) -> str:
    """الحلقة 2: يدوّر في الـ CV عن أجزاء ليها علاقة بالمتطلبات. من RAG """

    relevant_chunks = search_cv(requirements, top_k=5)
    return "\n\n---\n\n".join(relevant_chunks)

# ---------------------------------------------------------------------------
# Chain link 3 — produce the final decision (forced tool use)
# ---------------------------------------------------------------------------

def make_decision(requirements: str, cv_evidence: str) -> dict:
    """الحلقة 3: يقارن المتطلبات بأدلة الـ CV ويرجّع قرار منظّم عبر Tool Use."""

    client = get_client()

    user_content = f"""Analyze how well this job matches the CV, and apply the hard constraints.

<job_requirements>
{requirements}
</job_requirements>

<cv_evidence>
{cv_evidence}
</cv_evidence>

Record your final decision using the submit_job_decision tool."""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=DECISION_SYSTEM_PROMPT,
        tools=[DECISION_TOOL],
        tool_choice={"type": "tool", "name": "submit_job_decision"},
        messages=[{"role": "user", "content": user_content}],
    )

    # Claude's reply comes back as content blocks. When we force tool use,
    # one of them is a "tool_use" block whose .input holds our structured decision.
    for block in response.content:
        if block.type == "tool_use":
            return block.input

    return None  # no tool_use block was returned (unexpected)

# ---------------------------------------------------------------------------
# The full chain
# ---------------------------------------------------------------------------

def analyze_job(job_text: str) -> dict:
    """يشغّل سلسلة التحليل الكاملة من عرض الوظيفة للقرار النهائي."""

    requirements = extract_requirements(job_text)       # link 1
    cv_evidence = gather_cv_evidence(requirements)       # link 2
    decision = make_decision(requirements, cv_evidence)  # link 3
    return decision