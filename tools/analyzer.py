from tools.claude_client import ask_claude
from rag.search import search_cv

from tools.claude_client import get_client
from config import CLAUDE_MODEL, MAX_TOKENS
from prompts.decision import DECISION_SYSTEM_PROMPT, DECISION_TOOL
from tools.claude_client import stream_claude


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

# ---------------------------------------------------------------------------
# مثال إرشادي: مدخل نموذجي ومخرَج مثالي.
#
# مكتوب كنص عادي مش f-string، عشان أقواس الـ JSON تفضل زي ما هي
# من غير ما نضطر نضاعفها. بيتحقن في الطلب كعنصر واحد.
# ---------------------------------------------------------------------------

DECISION_EXAMPLE = """    <sample_input>
        Senior Backend Engineer - Checkout
        
         Remote , Saudi Arabia About the job
        We are looking for a Senior Backend Engineer - Checkout to join our engineering team focused on Fintech, Checkout, and Promotions. You will design, build, and scale highly available backend systems that power mission-critical payment experiences, checkout flows, promotions, loyalty, pricing, and financial services.
        
        This role is ideal for engineers who enjoy solving complex distributed systems problems, building high-performance services, and designing software that operates reliably at scale. You'll work closely with Product, Design, Data, and Engineering teams to deliver resilient, observable, and maintainable systems that directly impact millions of transactions.
        
        We value engineers with strong software engineering fundamentals who embrace modern development practices, including leveraging AI to improve engineering productivity, software quality, testing, debugging, and delivery speed.
        
        Responsibilities
        
        Design, build, and operate scalable backend services supporting Fintech, Checkout, Promotions, Loyalty, and Payment systems
        Develop clean, maintainable, and high-performance production code with readability and long-term ownership in mind
        Design and evolve RESTful APIs and integrations with internal platforms, payment gateways, and third-party services
        Build reliable distributed systems capable of handling high traffic, failures, and asynchronous workloads
        Drive architectural decisions with scalability, resilience, maintainability, and operational excellence in mind
        Optimize application performance across services, databases, caching layers, queues, and background workers
        Participate in architecture discussions, technical design reviews, RFCs, and engineering planning
        Ensure services are production-ready through monitoring, logging, alerting, testing, and observability best practices
        Write comprehensive unit and integration tests while maintaining high engineering standards through code reviews
        Leverage AI-assisted engineering tools responsibly to accelerate development, debugging, testing, documentation, and code quality
        Mentor junior and mid-level engineers through technical leadership, design discussions, and engineering best practices
        Contribute throughout the full software development lifecycle, from design through deployment and production support
        Continuously improve system reliability, developer experience, and engineering standards across the team
        
        Requirements
        
        6+ years of professional software engineering experience building production backend systems
        Strong experience building scalable backend services in at least one modern language such as PHP, Go, Java, or C#
        Experience with PHP and Laravel is preferred but not required
        Strong understanding of distributed systems fundamentals, including consistency, availability, concurrency, fault tolerance, idempotency, asynchronous processing, messaging, and caching
        Experience designing and operating high-scale, highly available backend systems
        Proven ability to write clean, maintainable, efficient, and high-performance production code
        Strong understanding of software engineering principles, including SOLID, design patterns, clean architecture, and domain-driven design concepts
        Experience designing RESTful APIs and integrating with third-party platforms and payment providers
        Strong SQL knowledge with experience designing and optimizing MySQL or PostgreSQL databases
        Experience with caching technologies, queues, background workers, and performance optimization
        Experience writing automated tests, participating in code reviews, and working within modern CI/CD pipelines
        Comfortable using AI-assisted development tools to improve productivity, software design, implementation, testing, debugging, documentation, and code reviews
        
        Preferred Qualifications
        
        Experience building Fintech, Payments, Checkout, Loyalty, Pricing, Promotions, or other high-volume transactional systems
        Experience with event-driven architectures and distributed messaging systems
        Experience with Docker, Kubernetes, cloud platforms (AWS, GCP, or Azure), and Infrastructure as Code
        Experience with observability platforms, distributed tracing, metrics, and production monitoring
        Experience working within microservices or service-oriented architectures
        Bachelor's or Master's degree in Computer Science, Software Engineering, or a related field is a plus
    </sample_input>
    
    <ideal_output>
        {
          "decision": "قدم",
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
            "AI-assisted development tools usage not mentioned",
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
              "source": "Not explicitly mentioned in CV, though implied by senior architecture role at Rafeeq"
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
              "criterion": "AI-assisted development tools (CORE)",
              "verdict": "missing",
              "source": "No mention in CV"
            },
            {
              "criterion": "Fintech/Payments/Checkout experience (SECONDARY/Preferred)",
              "verdict": "partial",
              "source": "CV describes Rafeeq as shared mobility/ride-sharing platform with B2B/B2C model, not explicitly fintech/checkout, though may involve payment flows"
            },
            {
              "criterion": "Docker/Kubernetes/Cloud (SECONDARY/Preferred)",
              "verdict": "partial match",
              "source": "CV lists AWS and Docker under Cloud & DevOps skills; Kubernetes not mentioned"
            }
          ]
        }

    </ideal_output>"""

def make_decision(job_text: str, requirements: str, cv_evidence: str) -> dict:
    """
    الحلقة 3: يقارن المتطلبات بأدلة الـ CV ويرجّع قرار منظّم عبر Tool Use.

    بياخد نص الإعلان الأصلي كمان مش الملخّص بس، عشان يتأكد من الشروط
    الإلزامية (الدوام والموقع) من المصدر مباشرةً بدل ما يعتمد على وسيط.
    """

    client = get_client()

    user_content = f"""Analyze how well this job matches the CV, and apply the hard constraints.

<job_posting> below is the ORIGINAL posting and is the source of truth. Verify \
the hard constraints (work arrangement and location) against it directly. \
<job_requirements> is only a helper summary extracted from it - if the two ever \
disagree, trust <job_posting>. Do NOT mark a hard constraint as "unclear" or \
"not confirmed" when <job_posting> actually states it.

    <guidelines>
        Follow these three steps in order.
        
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
        - "لا_تقدم": any hard constraint fails, OR two or more CORE requirements \
        are missing.
        - "قدم_بحذر": all hard constraints pass AND exactly one CORE requirement is \
        missing, OR the CV shows one to two years less experience than requested.
        - "قدم": all hard constraints pass AND every CORE requirement is present in \
        the CV. Missing SECONDARY items do not prevent this decision.
        
        Apply the hard constraints exactly as defined in your system instructions. In \
        particular, a hard constraint that the posting never mentions caps the \
        decision at "قدم_بحذر" - it does not force "لا_تقدم".
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
    
    This solution meets all the specified criteria: it identifies the strong 9-year Laravel developer match, recommends applying (قدم), and explicitly cites Laravel, MySQL, PostgreSQL, and API design as matching skills. The job posting explicitly states 'Remote, Saudi Arabia' and the solution acknowledges this as a pass for location/remote constraints, aligning with the Jeddah+Remote GCC filter criterion (Saudi Arabia is GCC). All mandatory requirements appear satisfied. The solution is thorough and well-structured with detailed reasoning per criterion, distinguishing core vs secondary/preferred requirements appropriately. Minor deductions are due to not explicitly cross-referencing the candidate's own location (Jeddah) against the remote constraint, and slightly verbose emphasis on gaps that are preferred-only qualifications, which could be tightened for clarity. Overall this is a strong, accurate solution with only minor room for improvement.
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

def stream_decision_summary(decision: dict):
    """يبثّ شرح بشري مختصر للقرار."""
    prompt = f"""This is a structured job analysis decision:
{decision}

Write a brief, human-readable explanation (3-4 sentences) explaining why this decision was made,
using a friendly and direct tone. In English"""
    yield from stream_claude(prompt)

# ---------------------------------------------------------------------------
# The full chain
# ---------------------------------------------------------------------------

def analyze_job(job_text: str) -> dict:
    """يشغّل سلسلة التحليل الكاملة من عرض الوظيفة للقرار النهائي."""

    requirements = extract_requirements(job_text)       # link 1
    cv_evidence = gather_cv_evidence(requirements)       # link 2
    decision = make_decision(job_text, requirements, cv_evidence)  # link 3
    return decision

