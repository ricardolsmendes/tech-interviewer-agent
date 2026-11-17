"""Structured outputs produced by the crews, consumed by the Jinja2 renderer."""

from __future__ import annotations

import typing

import pydantic

Status = typing.Literal["Met", "Partial", "Not met"]


class StackSkills(pydantic.BaseModel):
    stack: str = pydantic.Field(description="Technology stack or category, e.g. 'Backend', 'Data'")
    hard_skills: list[str]


class SkillListing(pydantic.BaseModel):
    role: str
    hard_skills_by_stack: list[StackSkills]
    soft_skills: list[str]


class RequirementRow(pydantic.BaseModel):
    requirement: str
    status: Status
    evidence: str = pydantic.Field(
        description="Specific roles, dates, tools, or outcomes from the resume"
    )


class NiceToHaveRow(pydantic.BaseModel):
    nice_to_have: str
    status: Status
    notes: str


class BulletItem(pydantic.BaseModel):
    label: str
    explanation: str


class ResumeAssessment(pydantic.BaseModel):
    candidate_name: str
    role: str
    verdict_label: str = pydantic.Field(
        description=(
            "One of: 'Strong fit', 'Good fit — <caveat>', 'Partial fit — <reason>', "
            "'Not a fit — <reason>'"
        )
    )
    verdict_class: typing.Literal["strong", "partial", "no-fit"]
    opening_paragraph: str = pydantic.Field(
        description="2-4 sentences naming the key strength and concern"
    )
    requirements: list[RequirementRow]
    nice_to_haves: list[NiceToHaveRow] = []
    standouts: list[BulletItem] = pydantic.Field(description="3-5 genuine differentiators")
    concerns: list[BulletItem]
    summary: str = pydantic.Field(description="3-5 sentences ending with a hiring recommendation")


class RankedCandidate(pydantic.BaseModel):
    rank: int
    candidate_name: str
    verdict_label: str
    key_strengths: list[str]
    key_risks: list[str]


class CandidateComparison(pydantic.BaseModel):
    role: str
    ranked_candidates: list[RankedCandidate]
    differentiators: str = pydantic.Field(
        description="Paragraph(s) explaining what sets candidates apart"
    )
    recommendation: str = pydantic.Field(description="The strongest fit and why")


class QuestionItem(pydantic.BaseModel):
    question: str
    rationale: str = pydantic.Field(
        description="What this question probes and why, given the JD/resume"
    )


class InterviewQuestions(pydantic.BaseModel):
    candidate_name: str
    role: str
    technical_questions: list[QuestionItem]
    behavioural_questions: list[QuestionItem]


class InterviewSummary(pydantic.BaseModel):
    candidate_name: str
    role: str
    performance_summary: str
    fit_assessment: str
    reservations: list[str]
    recommendation: str = pydantic.Field(
        description="Clear recommendation: hire, pass, or conditional on a specific validation"
    )
