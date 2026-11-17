"""Structured outputs produced by the crews, consumed by the Jinja2 renderer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["Met", "Partial", "Not met"]


class StackSkills(BaseModel):
    stack: str = Field(description="Technology stack or category, e.g. 'Backend', 'Data'")
    hard_skills: list[str]


class SkillListing(BaseModel):
    role: str
    hard_skills_by_stack: list[StackSkills]
    soft_skills: list[str]


class RequirementRow(BaseModel):
    requirement: str
    status: Status
    evidence: str = Field(description="Specific roles, dates, tools, or outcomes from the resume")


class NiceToHaveRow(BaseModel):
    nice_to_have: str
    status: Status
    notes: str


class BulletItem(BaseModel):
    label: str
    explanation: str


class ResumeAssessment(BaseModel):
    candidate_name: str
    role: str
    verdict_label: str = Field(
        description=(
            "One of: 'Strong fit', 'Good fit — <caveat>', 'Partial fit — <reason>', "
            "'Not a fit — <reason>'"
        )
    )
    verdict_class: Literal["strong", "partial", "no-fit"]
    opening_paragraph: str = Field(description="2-4 sentences naming the key strength and concern")
    requirements: list[RequirementRow]
    nice_to_haves: list[NiceToHaveRow] = []
    standouts: list[BulletItem] = Field(description="3-5 genuine differentiators")
    concerns: list[BulletItem]
    summary: str = Field(description="3-5 sentences ending with a hiring recommendation")


class RankedCandidate(BaseModel):
    rank: int
    candidate_name: str
    verdict_label: str
    key_strengths: list[str]
    key_risks: list[str]


class CandidateComparison(BaseModel):
    role: str
    ranked_candidates: list[RankedCandidate]
    differentiators: str = Field(description="Paragraph(s) explaining what sets candidates apart")
    recommendation: str = Field(description="The strongest fit and why")


class QuestionItem(BaseModel):
    question: str
    rationale: str = Field(description="What this question probes and why, given the JD/resume")


class InterviewQuestions(BaseModel):
    candidate_name: str
    role: str
    technical_questions: list[QuestionItem]
    behavioural_questions: list[QuestionItem]


class InterviewSummary(BaseModel):
    candidate_name: str
    role: str
    performance_summary: str
    fit_assessment: str
    reservations: list[str]
    recommendation: str = Field(
        description="Clear recommendation: hire, pass, or conditional on a specific validation"
    )
