"""Crew: rank multiple candidates for the same role and recommend the strongest fit.

Reuses the resume-assessment crew per candidate, then ranks the resulting structured
assessments against each other and the job description.
"""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from interviewer.config import get_llm
from interviewer.crews import resume_assessment
from interviewer.models import CandidateComparison, ResumeAssessment


def _assessment_summary(assessment: ResumeAssessment) -> str:
    requirements = "\n".join(
        f"  - {row.requirement}: {row.status} ({row.evidence})" for row in assessment.requirements
    )
    standouts = "\n".join(f"  - {item.label}: {item.explanation}" for item in assessment.standouts)
    concerns = "\n".join(f"  - {item.label}: {item.explanation}" for item in assessment.concerns)
    return (
        f"Candidate: {assessment.candidate_name}\n"
        f"Verdict: {assessment.verdict_label}\n"
        f"Requirements:\n{requirements}\n"
        f"Standouts:\n{standouts}\n"
        f"Concerns:\n{concerns}\n"
        f"Summary: {assessment.summary}"
    )


def assess_candidates(jd_text: str, resumes: list[str]) -> list[ResumeAssessment]:
    """Run the resume-assessment crew for each candidate's resume text."""
    return [resume_assessment.run(jd_text, resume_text) for resume_text in resumes]


def run(jd_text: str, assessments: list[ResumeAssessment]) -> CandidateComparison:
    llm = get_llm("opus")

    ranker = Agent(
        role="Hiring Panel Lead",
        goal="Rank candidates for the same role and recommend the strongest fit",
        backstory=(
            "You chair hiring panels and compare candidate assessments side by side, "
            "explaining precisely what separates them rather than restating each one."
        ),
        llm=llm,
        verbose=False,
    )

    assessments_block = "\n\n".join(_assessment_summary(a) for a in assessments)

    task = Task(
        description=(
            "Rank the following candidates for the same role, from strongest to weakest fit. "
            "Explain the key differentiators between them — what actually separates them, not "
            "a restatement of each individual assessment — and recommend the strongest fit.\n\n"
            f"Job description:\n\"\"\"\n{jd_text}\n\"\"\"\n\n"
            f"Candidate assessments:\n{assessments_block}"
        ),
        expected_output="A complete CandidateComparison with every candidate ranked.",
        agent=ranker,
        output_pydantic=CandidateComparison,
    )

    crew = Crew(agents=[ranker], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.pydantic
