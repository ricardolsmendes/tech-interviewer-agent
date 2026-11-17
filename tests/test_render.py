from pathlib import Path

from interviewer.models import (
    BulletItem,
    CandidateComparison,
    InterviewQuestions,
    InterviewSummary,
    NiceToHaveRow,
    QuestionItem,
    RankedCandidate,
    RequirementRow,
    ResumeAssessment,
    SkillListing,
    StackSkills,
)
from interviewer.rendering.render import render_to_file


def _sample_assessment() -> ResumeAssessment:
    return ResumeAssessment(
        candidate_name="Alice Johnson",
        role="Data Analyst — Acme (via Globex)",
        verdict_label="Partial fit — no data domain experience",
        verdict_class="partial",
        opening_paragraph="Alice has strong SQL skills but no data domain experience.",
        requirements=[
            RequirementRow(requirement="SQL", status="Met", evidence="5 years at Acme (2019-2024)"),
            RequirementRow(requirement="dbt", status="Not met", evidence="No mention of dbt"),
        ],
        nice_to_haves=[
            NiceToHaveRow(nice_to_have="Airflow", status="Partial", notes="Mentioned once, unclear depth"),
        ],
        standouts=[BulletItem(label="SQL depth", explanation="Built the core reporting warehouse")],
        concerns=[BulletItem(label="No dbt", explanation="Role requires dbt day one")],
        summary="Recommend a technical screen focused on dbt before proceeding.",
    )


def test_resume_assessment_template_matches_format_contract(tmp_path: Path) -> None:
    out_path = tmp_path / "out.html"
    render_to_file("resume_assessment.html.j2", {"assessment": _sample_assessment()}, out_path)
    html = out_path.read_text()

    assert '<span class="verdict partial">Partial fit — no data domain experience</span>' in html
    assert '<td class="met">Met</td>' in html
    assert '<td class="gap">Not met</td>' in html
    assert '<td class="partial-cell">Partial</td>' in html
    assert '<div class="standout">' in html
    assert '<div class="flag">' in html
    assert '<div class="section-note">' in html
    assert "Comparison to other candidates" not in html


def test_resume_assessment_template_omits_empty_nice_to_haves(tmp_path: Path) -> None:
    assessment = _sample_assessment().model_copy(update={"nice_to_haves": []})
    out_path = tmp_path / "out.html"
    render_to_file("resume_assessment.html.j2", {"assessment": assessment}, out_path)
    html = out_path.read_text()
    assert "Nice-to-Haves Coverage" not in html


def test_skill_listing_template_renders(tmp_path: Path) -> None:
    listing = SkillListing(
        role="Senior Data Engineer",
        hard_skills_by_stack=[StackSkills(stack="Data", hard_skills=["SQL", "Airflow"])],
        soft_skills=["Communication"],
    )
    out_path = tmp_path / "out.html"
    render_to_file("skill_listing.html.j2", {"listing": listing}, out_path)
    html = out_path.read_text()
    assert "Senior Data Engineer" in html
    assert "Airflow" in html
    assert "Communication" in html


def test_candidate_comparison_template_renders(tmp_path: Path) -> None:
    comparison = CandidateComparison(
        role="Data Engineer",
        ranked_candidates=[
            RankedCandidate(
                rank=1,
                candidate_name="Alice Johnson",
                verdict_label="Strong fit",
                key_strengths=["dbt expertise"],
                key_risks=["Limited cloud experience"],
            )
        ],
        differentiators="Alice has deeper dbt experience than other candidates.",
        recommendation="Proceed with Alice Johnson.",
    )
    out_path = tmp_path / "out.html"
    render_to_file("candidate_comparison.html.j2", {"comparison": comparison}, out_path)
    html = out_path.read_text()
    assert "Alice Johnson" in html
    assert "dbt expertise" in html


def test_interview_questions_template_renders(tmp_path: Path) -> None:
    questions = InterviewQuestions(
        candidate_name="Bob Smith",
        role="Tech Lead",
        technical_questions=[QuestionItem(question="Explain CAP theorem", rationale="Tests fundamentals")],
        behavioural_questions=[QuestionItem(question="Describe a conflict", rationale="Tests leadership")],
    )
    out_path = tmp_path / "out.html"
    render_to_file("interview_questions.html.j2", {"questions": questions}, out_path)
    html = out_path.read_text()
    assert "Explain CAP theorem" in html
    assert "Describe a conflict" in html


def test_interview_summary_template_renders(tmp_path: Path) -> None:
    summary = InterviewSummary(
        candidate_name="Carol White",
        role="Data Product Manager",
        performance_summary="Carol communicated clearly and answered all technical questions.",
        fit_assessment="Strong fit for the role.",
        reservations=["Limited experience with enterprise clients"],
        recommendation="Proceed to offer.",
    )
    out_path = tmp_path / "out.html"
    render_to_file("interview_summary.html.j2", {"summary": summary}, out_path)
    html = out_path.read_text()
    assert "Carol White" in html
    assert "Limited experience with enterprise clients" in html
