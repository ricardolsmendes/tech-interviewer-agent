import pathlib

import pytest
import typer.testing

from interviewer import cli, config, models

runner = typer.testing.CliRunner()


def _touch_pdf(folder: pathlib.Path, name: str) -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(b"%PDF-1.4\n")
    return path


@pytest.fixture(autouse=True)
def _folders(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, pathlib.Path]:
    jd_dir = tmp_path / "job-descriptions"
    resumes_dir = tmp_path / "resumes"
    notes_dir = tmp_path / "interview-notes"
    monkeypatch.setattr(config, "JOB_DESCRIPTIONS_DIR", jd_dir)
    monkeypatch.setattr(config, "RESUMES_DIR", resumes_dir)
    monkeypatch.setattr(config, "INTERVIEW_NOTES_DIR", notes_dir)
    monkeypatch.setattr(cli.io_utils, "extract_pdf_text", lambda path: f"text of {path.name}")
    return {"jd": jd_dir, "resumes": resumes_dir, "notes": notes_dir}


def test_skill_listing_cmd_saves_output(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    monkeypatch.setattr(
        cli.skill_listing,
        "run",
        lambda jd_text: models.SkillListing(
            role="Data Engineer",
            hard_skills_by_stack=[models.StackSkills(stack="Data", hard_skills=["SQL"])],
            soft_skills=["Communication"],
        ),
    )

    result = runner.invoke(cli.app, ["skill-listing"])

    assert result.exit_code == 0, result.output
    out_path = _folders["jd"] / "JD_skill-listing.html"
    assert out_path.is_file()
    assert "Data Engineer" in out_path.read_text()


def test_resume_assessment_cmd_saves_output(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Alice-Johnson.pdf")
    monkeypatch.setattr(
        cli.resume_assessment,
        "run",
        lambda jd_text, resume_text: models.ResumeAssessment(
            candidate_name="Alice Johnson",
            role="Data Analyst",
            verdict_label="Strong fit",
            verdict_class="strong",
            opening_paragraph="Great fit overall.",
            requirements=[
                models.RequirementRow(requirement="SQL", status="Met", evidence="5 years")
            ],
            standouts=[models.BulletItem(label="SQL", explanation="Deep expertise")],
            concerns=[models.BulletItem(label="None", explanation="No concerns")],
            summary="Proceed to interview.",
        ),
    )

    result = runner.invoke(cli.app, ["resume-assessment"])

    assert result.exit_code == 0, result.output
    out_path = _folders["resumes"] / "Alice-Johnson_resume-assessment.html"
    assert out_path.is_file()
    assert "Alice Johnson" in out_path.read_text()


def test_interview_questions_cmd_saves_output(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Bob-Smith.pdf")
    monkeypatch.setattr(
        cli.interview_questions,
        "run",
        lambda jd_text, resume_text: models.InterviewQuestions(
            candidate_name="Bob Smith",
            role="Tech Lead",
            technical_questions=[
                models.QuestionItem(question="Explain X", rationale="Probes depth")
            ],
            behavioural_questions=[
                models.QuestionItem(question="Describe Y", rationale="Probes leadership")
            ],
        ),
    )

    result = runner.invoke(cli.app, ["interview-questions"])

    assert result.exit_code == 0, result.output
    out_path = _folders["resumes"] / "Bob-Smith_interview-questions.html"
    assert out_path.is_file()


def test_interview_summary_cmd_saves_output(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Carol-White.pdf")
    _touch_pdf(_folders["notes"], "Carol-White-notes.pdf")
    monkeypatch.setattr(
        cli.interview_summary,
        "run",
        lambda jd_text, resume_text, notes_text: models.InterviewSummary(
            candidate_name="Carol White",
            role="Data Product Manager",
            performance_summary="Performed well.",
            fit_assessment="Good fit.",
            reservations=[],
            recommendation="Proceed to offer.",
        ),
    )

    result = runner.invoke(cli.app, ["interview-summary"])

    assert result.exit_code == 0, result.output
    out_path = _folders["resumes"] / "Carol-White_interview-summary.html"
    assert out_path.is_file()


def test_compare_cmd_requires_at_least_two_resumes(_folders: dict[str, pathlib.Path]) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Only.pdf")

    result = runner.invoke(cli.app, ["compare"])

    assert result.exit_code == 1


def test_compare_cmd_saves_individual_and_comparison_output(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Alice.pdf")
    _touch_pdf(_folders["resumes"], "Bob.pdf")

    names = iter(["Alice Johnson", "Bob Smith"])

    def fake_assessment_run(jd_text: str, resume_text: str) -> models.ResumeAssessment:
        return models.ResumeAssessment(
            candidate_name=next(names),
            role="Data Analyst",
            verdict_label="Strong fit",
            verdict_class="strong",
            opening_paragraph="Fit.",
            requirements=[
                models.RequirementRow(requirement="SQL", status="Met", evidence="5 years")
            ],
            standouts=[models.BulletItem(label="SQL", explanation="Deep expertise")],
            concerns=[],
            summary="Proceed.",
        )

    monkeypatch.setattr(cli.resume_assessment, "run", fake_assessment_run)
    monkeypatch.setattr(
        cli.candidate_comparison,
        "run",
        lambda jd_text, assessments: models.CandidateComparison(
            role="Data Analyst",
            ranked_candidates=[
                models.RankedCandidate(
                    rank=1,
                    candidate_name=a.candidate_name,
                    verdict_label=a.verdict_label,
                    key_strengths=["SQL"],
                    key_risks=[],
                )
                for a in assessments
            ],
            differentiators="Both strong, Alice has more SQL depth.",
            recommendation="Proceed with Alice.",
        ),
    )

    result = runner.invoke(cli.app, ["compare"])

    assert result.exit_code == 0, result.output
    assert (_folders["resumes"] / "Alice_resume-assessment.html").is_file()
    assert (_folders["resumes"] / "Bob_resume-assessment.html").is_file()
    assert (_folders["jd"] / "JD_candidate-comparison.html").is_file()


def test_resume_assessment_cmd_prompts_when_multiple_resumes(
    _folders: dict[str, pathlib.Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")
    _touch_pdf(_folders["resumes"], "Alice.pdf")
    _touch_pdf(_folders["resumes"], "Bob.pdf")
    monkeypatch.setattr(
        cli.resume_assessment,
        "run",
        lambda jd_text, resume_text: models.ResumeAssessment(
            candidate_name="Bob Smith",
            role="Data Analyst",
            verdict_label="Strong fit",
            verdict_class="strong",
            opening_paragraph="Fit.",
            requirements=[],
            standouts=[],
            concerns=[],
            summary="Proceed.",
        ),
    )

    result = runner.invoke(cli.app, ["resume-assessment"], input="2\n")

    assert result.exit_code == 0, result.output
    assert (_folders["resumes"] / "Bob_resume-assessment.html").is_file()


def test_resume_assessment_cmd_fails_when_no_resume_pdfs(
    _folders: dict[str, pathlib.Path],
) -> None:
    _touch_pdf(_folders["jd"], "JD.pdf")

    result = runner.invoke(cli.app, ["resume-assessment"])

    assert result.exit_code == 1
