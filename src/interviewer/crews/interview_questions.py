"""Crew: generate interview questions tailored to a candidate and a role."""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task

from interviewer.config import get_llm
from interviewer.models import InterviewQuestions


def run(jd_text: str, resume_text: str) -> InterviewQuestions:
    llm = get_llm()

    interviewer = Agent(
        role="Interview Designer",
        goal="Design interview questions that probe a candidate's specific experience",
        backstory=(
            "You design interview loops for technical roles, tailoring questions to what a "
            "candidate's resume actually claims so interviewers can verify or challenge it, "
            "while also probing the behavioural traits the role needs."
        ),
        llm=llm,
        verbose=False,
    )

    task = Task(
        description=(
            "Generate interview questions tailored to this candidate and role. Technical "
            "questions should probe the candidate's specific claimed experience (named "
            "technologies, projects, or outcomes) rather than being generic. Behavioural "
            "questions should probe traits the role requires. For every question, give a short "
            "rationale for why it matters given the JD and resume.\n\n"
            f"Job description:\n\"\"\"\n{jd_text}\n\"\"\"\n\n"
            f"Resume:\n\"\"\"\n{resume_text}\n\"\"\""
        ),
        expected_output="A complete InterviewQuestions with technical and behavioural questions.",
        agent=interviewer,
        output_pydantic=InterviewQuestions,
    )

    crew = Crew(agents=[interviewer], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.pydantic
