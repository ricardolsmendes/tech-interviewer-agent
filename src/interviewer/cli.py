"""CLI entry point: one subcommand per interviewing capability."""

from __future__ import annotations

import pathlib

import typer

from interviewer import config, io_utils
from interviewer.crews import (
    candidate_comparison,
    interview_questions,
    interview_summary,
    resume_assessment,
    skill_listing,
)
from interviewer.rendering import render

app = typer.Typer(add_completion=False, help="Tech interviewer assistant, powered by CrewAI.")


def _interactive_chooser(candidates: list[pathlib.Path], label: str) -> pathlib.Path:
    typer.echo(f"Multiple PDF files found for the {label}:")
    for i, path in enumerate(candidates, start=1):
        typer.echo(f"  {i}. {path.name}")
    choice = typer.prompt("Pick one", type=int)
    if not 1 <= choice <= len(candidates):
        raise typer.BadParameter(f"Choose a number between 1 and {len(candidates)}")
    return candidates[choice - 1]


def _resolve(folder: pathlib.Path, label: str, explicit: pathlib.Path | None) -> pathlib.Path:
    try:
        return io_utils.resolve_file(folder, label, explicit, chooser=_interactive_chooser)
    except (io_utils.NoPdfFoundError, io_utils.AmbiguousPdfError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc


@app.command("skill-listing")
def skill_listing_cmd(
    jd: pathlib.Path | None = typer.Option(None, "--jd", help="Path to the job description PDF"),
) -> None:
    """List the hard and soft skills required by a job description."""
    jd_path = _resolve(config.JOB_DESCRIPTIONS_DIR, "job description", jd)
    jd_text = io_utils.extract_pdf_text(jd_path)

    listing = skill_listing.run(jd_text)

    out_path = config.JOB_DESCRIPTIONS_DIR / f"{jd_path.stem}_skill-listing.html"
    render.render_to_file("skill_listing.html.j2", {"listing": listing}, out_path)
    typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)


@app.command("resume-assessment")
def resume_assessment_cmd(
    jd: pathlib.Path | None = typer.Option(None, "--jd", help="Path to the job description PDF"),
    resume: pathlib.Path | None = typer.Option(
        None, "--resume", help="Path to the candidate resume PDF"
    ),
) -> None:
    """Assess how well a candidate's resume fits a job description."""
    jd_path = _resolve(config.JOB_DESCRIPTIONS_DIR, "job description", jd)
    resume_path = _resolve(config.RESUMES_DIR, "resume", resume)
    jd_text = io_utils.extract_pdf_text(jd_path)
    resume_text = io_utils.extract_pdf_text(resume_path)

    assessment = resume_assessment.run(jd_text, resume_text)

    out_path = config.RESUMES_DIR / f"{resume_path.stem}_resume-assessment.html"
    render.render_to_file("resume_assessment.html.j2", {"assessment": assessment}, out_path)
    typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)


@app.command("compare")
def compare_cmd(
    jd: pathlib.Path | None = typer.Option(None, "--jd", help="Path to the job description PDF"),
    resumes: list[pathlib.Path] = typer.Option(
        None, "--resumes", help="Paths to candidate resume PDFs (default: every PDF in resumes/)"
    ),
) -> None:
    """Rank multiple candidates for the same role and recommend the strongest fit."""
    jd_path = _resolve(config.JOB_DESCRIPTIONS_DIR, "job description", jd)
    jd_text = io_utils.extract_pdf_text(jd_path)

    resume_paths = resumes or io_utils.list_pdfs(config.RESUMES_DIR)
    if len(resume_paths) < 2:
        typer.secho(
            "Need at least two candidate resumes to compare. Add more PDFs to resumes/ or "
            "pass --resumes explicitly.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    assessments = []
    for resume_path in resume_paths:
        resume_text = io_utils.extract_pdf_text(resume_path)
        assessment = resume_assessment.run(jd_text, resume_text)
        assessments.append(assessment)

        out_path = config.RESUMES_DIR / f"{resume_path.stem}_resume-assessment.html"
        render.render_to_file("resume_assessment.html.j2", {"assessment": assessment}, out_path)
        typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)

    comparison = candidate_comparison.run(jd_text, assessments)

    out_path = config.JOB_DESCRIPTIONS_DIR / f"{jd_path.stem}_candidate-comparison.html"
    render.render_to_file("candidate_comparison.html.j2", {"comparison": comparison}, out_path)
    typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)


@app.command("interview-questions")
def interview_questions_cmd(
    jd: pathlib.Path | None = typer.Option(None, "--jd", help="Path to the job description PDF"),
    resume: pathlib.Path | None = typer.Option(
        None, "--resume", help="Path to the candidate resume PDF"
    ),
) -> None:
    """Generate interview questions tailored to a candidate and a role."""
    jd_path = _resolve(config.JOB_DESCRIPTIONS_DIR, "job description", jd)
    resume_path = _resolve(config.RESUMES_DIR, "resume", resume)
    jd_text = io_utils.extract_pdf_text(jd_path)
    resume_text = io_utils.extract_pdf_text(resume_path)

    questions = interview_questions.run(jd_text, resume_text)

    out_path = config.RESUMES_DIR / f"{resume_path.stem}_interview-questions.html"
    render.render_to_file("interview_questions.html.j2", {"questions": questions}, out_path)
    typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)


@app.command("interview-summary")
def interview_summary_cmd(
    jd: pathlib.Path | None = typer.Option(None, "--jd", help="Path to the job description PDF"),
    resume: pathlib.Path | None = typer.Option(
        None, "--resume", help="Path to the candidate resume PDF"
    ),
    notes: pathlib.Path | None = typer.Option(
        None, "--notes", help="Path to the interview notes PDF"
    ),
) -> None:
    """Summarise how a candidate performed in an interview."""
    jd_path = _resolve(config.JOB_DESCRIPTIONS_DIR, "job description", jd)
    resume_path = _resolve(config.RESUMES_DIR, "resume", resume)
    notes_path = _resolve(config.INTERVIEW_NOTES_DIR, "interview notes", notes)
    jd_text = io_utils.extract_pdf_text(jd_path)
    resume_text = io_utils.extract_pdf_text(resume_path)
    notes_text = io_utils.extract_pdf_text(notes_path)

    summary = interview_summary.run(jd_text, resume_text, notes_text)

    out_path = config.RESUMES_DIR / f"{resume_path.stem}_interview-summary.html"
    render.render_to_file("interview_summary.html.j2", {"summary": summary}, out_path)
    typer.secho(f"Saved {out_path}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
