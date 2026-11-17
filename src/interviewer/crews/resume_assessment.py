"""Crew: assess how well a candidate's resume fits a job description."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from interviewer.config import get_llm, profile_context
from interviewer.models import ResumeAssessment

_VERDICT_RULES = """
Choose exactly one verdict and its CSS class:
- "Strong fit" (class "strong") — meets virtually all requirements and most nice-to-haves
- "Good fit — <one specific caveat>" (class "strong") — strong overall but one thing must be
  validated
- "Partial fit — <reason in a few words>" (class "partial") — meets some requirements but has
  a significant gap
- "Not a fit — <reason in a few words>" (class "no-fit") — does not meet the core requirements
"""


def run(jd_text: str, resume_text: str) -> ResumeAssessment:
    llm = get_llm()

    analyst = Agent(
        role="Technical Recruiter",
        goal="Produce a rigorous, evidence-based assessment of a candidate's fit for a role",
        backstory=(
            "You are an experienced technical recruiter who reads job descriptions and resumes "
            "closely, cites specifics rather than generic claims, and is direct about gaps and "
            "risks so interviewers can make an informed decision."
        ),
        llm=llm,
        verbose=False,
    )

    context = profile_context()
    context_block = f"\n\n{context}" if context else ""

    task = Task(
        description=(
            "Assess how well the candidate's resume fits the job description.\n"
            f"{_VERDICT_RULES}\n"
            "Cover every requirement from the JD in the requirements table, and every "
            "nice-to-have in a separate table (leave nice_to_haves empty if the JD lists none). "
            "Evidence must cite specific roles, dates, tools, or outcomes from the resume — "
            "never generic statements like 'has experience with X'. "
            "Standouts must be genuine differentiators, not a restatement of the requirements "
            "table — list 3 to 5. Concerns should be direct, for the interviewer's eyes only, "
            "covering gaps, risks, or things to validate. The summary must end with a clear "
            "hiring recommendation.\n\n"
            f"Job description:\n\"\"\"\n{jd_text}\n\"\"\"\n\n"
            f"Resume:\n\"\"\"\n{resume_text}\n\"\"\""
            f"{context_block}"
        ),
        expected_output="A complete ResumeAssessment.",
        agent=analyst,
        output_pydantic=ResumeAssessment,
    )

    crew = Crew(agents=[analyst], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.pydantic
