"""Crew: summarise how a candidate performed in an interview."""

from __future__ import annotations

import crewai

from interviewer import config, models


def run(jd_text: str, resume_text: str, notes_text: str) -> models.InterviewSummary:
    llm = config.get_llm("sonnet")

    summarizer = crewai.Agent(
        role="Hiring Decision Advisor",
        goal="Summarise interview performance and fit so a hiring decision can be made",
        backstory=(
            "You read interview notes alongside the job description and resume, and give "
            "interviewers a clear, honest read on performance and fit before they decide."
        ),
        llm=llm,
        verbose=False,
    )

    context = config.profile_context()
    context_block = f"\n\n{context}" if context else ""

    task = crewai.Task(
        description=(
            "Summarise how the candidate performed in the interview, whether they are a good "
            "fit for the role, and any reservations worth considering before making a decision. "
            "Ground everything in the interview notes, the job description, and the resume. "
            "End with a clear recommendation: hire, pass, or conditional on a specific "
            "validation.\n\n"
            f"Job description:\n\"\"\"\n{jd_text}\n\"\"\"\n\n"
            f"Resume:\n\"\"\"\n{resume_text}\n\"\"\"\n\n"
            f"Interview notes:\n\"\"\"\n{notes_text}\n\"\"\""
            f"{context_block}"
        ),
        expected_output="A complete InterviewSummary.",
        agent=summarizer,
        output_pydantic=models.InterviewSummary,
    )

    crew = crewai.Crew(
        agents=[summarizer], tasks=[task], process=crewai.Process.sequential, verbose=False
    )
    result = crew.kickoff()
    return result.pydantic
