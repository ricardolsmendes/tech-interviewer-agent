"""Crew: list the hard and soft skills required by a job description."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from interviewer.config import get_llm
from interviewer.models import SkillListing


def run(jd_text: str) -> SkillListing:
    llm = get_llm()

    analyst = Agent(
        role="Job Description Analyst",
        goal="Extract a clear, complete breakdown of the skills a job description requires",
        backstory=(
            "You read job descriptions for a technical recruiting team and translate them "
            "into skill breakdowns that are easy for non-technical interviewers to scan."
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            "Read the job description below and list the hard and soft skills it requires. "
            "Group hard skills by technology stack or category (e.g. Backend, Data, Cloud, "
            "Leadership) where that grouping is meaningful; otherwise use a single sensible "
            "group. List soft skills separately.\n\n"
            f"Job description:\n\"\"\"\n{jd_text}\n\"\"\""
        ),
        expected_output=(
            "A SkillListing with the role title, hard skills grouped by stack, and soft skills."
        ),
        agent=analyst,
        output_pydantic=SkillListing,
    )

    crew = Crew(agents=[analyst], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.pydantic
