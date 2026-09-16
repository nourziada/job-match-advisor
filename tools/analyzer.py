from tools.claude_client import ask_claude
from rag.search import search_cv

from tools.claude_client import get_client
from config import CLAUDE_MODEL, MAX_TOKENS
from prompts.decision import build_system_prompt, DECISION_TOOL
from prompts.guidelines import load_guidelines
from tools.claude_client import stream_claude


def extract_requirements(job_text: str) -> str:
    """Read a job posting and extract its core requirements as structured text."""

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


def gather_cv_evidence(requirements: str) -> str:
    """Retrieve the CV sections most relevant to the given requirements."""

    relevant_chunks = search_cv(requirements, top_k=5)
    return "\n\n---\n\n".join(relevant_chunks)


# A worked example of one input and its ideal output. Kept as a plain string so
# the JSON braces do not need escaping.
DECISION_EXAMPLE = """    <sample_input>
        Senior Backend Engineer - Checkout

        Remote, Saudi Arabia

        We are looking for a Senior Backend Engineer - Checkout to join our engineering team focused on Fintech, Checkout, and Promotions. You will design, build, and scale highly available backend systems that power mission-critical payment experiences, checkout flows, promotions, loyalty, pricing, and financial services.

        Responsibilities

        Design, build, and operate scalable backend services supporting Fintech, Checkout, Promotions, Loyalty, and Payment systems
        Design and evolve RESTful APIs and integrations with internal platforms, payment gateways, and third-party services
        Build reliable distributed systems capable of handling high traffic, failures, and asynchronous workloads
        Optimize application performance across services, databases, caching layers, queues, and background workers
        Write comprehensive unit and integration tests while maintaining high engineering standards through code reviews
        Mentor junior and mid-level engineers through technical leadership, design discussions, and engineering best practices

        Requirements

        6+ years of professional software engineering experience building production backend systems
        Strong experience building scalable backend services in at least one modern language such as PHP, Go, Java, or C#
        Experience with PHP and Laravel is preferred but not required
        Strong understanding of distributed systems fundamentals, including consistency, availability, concurrency, fault tolerance, idempotency, asynchronous processing, messaging, and caching
        Strong understanding of software engineering principles, including SOLID, design patterns, clean architecture, and domain-driven design concepts
        Experience designing RESTful APIs and integrating with third-party platforms and payment providers
        Strong SQL knowledge with experience designing and optimizing MySQL or PostgreSQL databases
        Experience with caching technologies, queues, background workers, and performance optimization
        Experience writing automated tests, participating in code reviews, and working within modern CI/CD pipelines

        Preferred Qualifications

        Experience building Fintech, Payments, Checkout, Loyalty, Pricing, Promotions, or other high-volume transactional systems
        Experience with Docker, Kubernetes, cloud platforms (AWS, GCP, or Azure), and Infrastructure as Code
        Experience working within microservices or service-oriented architectures
    </sample_input>

    <ideal_output>
        {
          "decision": "apply",
          "confidence": 78,
          "matched_skills": [
            "PHP/Laravel experience (9+ years)",
            "MySQL, PostgreSQL",
            "AWS, Docker, CI/CD",
            "API design and scalable system architecture",
            "Team leadership / mentoring (led teams of 8-20+ engineers)",
            "Backend systems experience 9+ years (exceeds 6+ requirement)"
          ],
          "missing_skills": [
            "Explicit mention of distributed systems concepts (idempotency, fault tolerance, concurrency) not detailed in CV",
            "SOLID/design patterns/DDD not explicitly mentioned in CV",
            "Caching/queues/background workers not explicitly mentioned",
            "Automated testing/code reviews not explicitly detailed",
            "Fintech/Payments/Checkout specific experience not shown (Preferred only)",
            "Kubernetes, event-driven architecture, observability tools (Preferred only)"
          ],
          "reasoning": [
            {
              "criterion": "Remote work (Hard constraint)",
              "verdict": "pass",
              "source": "Job posting explicitly states 'Remote, Saudi Arabia'"
            },
            {
              "criterion": "Location within Europe/NA/GCC (Hard constraint)",
              "verdict": "pass",
              "source": "Saudi Arabia is a GCC country, explicitly stated in posting"
            },
            {
              "criterion": "6+ years backend experience (CORE)",
              "verdict": "match",
              "source": "CV states 'over 9 years of expertise' in backend development, with roles since 2018"
            },
            {
              "criterion": "PHP/Laravel or modern language (CORE)",
              "verdict": "match",
              "source": "CV lists PHP (Laravel, Lumen) as primary skill, with multiple Laravel Developer roles"
            },
            {
              "criterion": "RESTful API design (CORE)",
              "verdict": "match",
              "source": "CV states 'API Design' skill and 'managing over 100 API interfaces'"
            },
            {
              "criterion": "Strong SQL/MySQL/PostgreSQL (CORE)",
              "verdict": "match",
              "source": "CV lists MySQL, PostgreSQL under Database Management; also mentions 'optimizing database queries to improve performance by 30%'"
            },
            {
              "criterion": "Distributed systems fundamentals (CORE)",
              "verdict": "unclear/partial",
              "source": "CV mentions 'Scalable System Architecture' generally but does not explicitly detail consistency, concurrency, fault tolerance, idempotency, messaging"
            },
            {
              "criterion": "SOLID/design patterns/clean architecture/DDD (CORE)",
              "verdict": "unclear/partial",
              "source": "Not explicitly mentioned in CV, though implied by the senior architecture role"
            },
            {
              "criterion": "Caching, queues, background workers (CORE)",
              "verdict": "missing",
              "source": "Not explicitly mentioned in CV skills or experience"
            },
            {
              "criterion": "Automated testing, code reviews, CI/CD (CORE)",
              "verdict": "partial match",
              "source": "CV lists 'CI/CD Pipelines' under Cloud & DevOps, but no explicit mention of automated testing or code reviews"
            },
            {
              "criterion": "Docker/Kubernetes/Cloud (SECONDARY/Preferred)",
              "verdict": "partial match",
              "source": "CV lists AWS and Docker under Cloud & DevOps skills; Kubernetes not mentioned"
            }
          ]
        }
    </ideal_output>"""


def make_decision(
    job_text: str,
    requirements: str,
    cv_evidence: str,
    guidelines: str | None = None,
    preferences: str | None = None,
) -> dict:
    """Compare the requirements against the CV evidence and return a decision.

    The original posting is passed in alongside the extracted summary so the
    hard constraints are verified against the source rather than a paraphrase.
    The decision policy comes from the stored guidelines, and the hard
    constraints from the stored preferences, unless either is given.
    """

    if guidelines is None:
        guidelines = load_guidelines()

    client = get_client()

    user_content = f"""Analyze how well this job matches the CV, and apply the hard constraints.

<job_posting> below is the ORIGINAL posting and is the source of truth. Verify \
the hard constraints (work arrangement and location) against it directly. \
<job_requirements> is only a helper summary extracted from it - if the two ever \
disagree, trust <job_posting>. Do NOT mark a hard constraint as "unclear" or \
"not confirmed" when <job_posting> actually states it.

    <guidelines>
    {guidelines}
    </guidelines>

    <job_posting>
    {job_text}
    </job_posting>

    <job_requirements>
    {requirements}
    </job_requirements>

    <cv_evidence>
    {cv_evidence}
    </cv_evidence>

    {DECISION_EXAMPLE}

    Record your final decision using the submit_job_decision tool."""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=build_system_prompt(preferences),
        tools=[DECISION_TOOL],
        tool_choice={"type": "tool", "name": "submit_job_decision"},
        messages=[{"role": "user", "content": user_content}],
    )

    # Forcing tool use means one of the returned blocks is a tool_use block
    # whose .input holds the structured decision.
    for block in response.content:
        if block.type == "tool_use":
            return block.input

    return None


def stream_decision_summary(decision: dict):
    """Stream a short human-readable explanation of the decision."""
    prompt = f"""This is a structured job analysis decision:
{decision}

Write a brief, human-readable explanation (3-4 sentences) explaining why this decision was made,
using a friendly and direct tone. In English"""
    yield from stream_claude(prompt)


def analyze_job(
    job_text: str,
    guidelines: str | None = None,
    preferences: str | None = None,
) -> dict:
    """Run the full analysis chain from job posting to final decision."""

    requirements = extract_requirements(job_text)
    cv_evidence = gather_cv_evidence(requirements)
    decision = make_decision(
        job_text, requirements, cv_evidence, guidelines, preferences
    )
    return decision
