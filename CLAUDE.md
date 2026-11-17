# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## Role

This repository holds a **CrewAI-based Python application** that performs tech-interviewing
analysis (skill listings, resume assessments, candidate comparisons, interview questions, and
post-interview summaries) via a CLI, invoked outside of Claude Code.

**Claude Code's role here is strictly software development** — building and maintaining the CLI,
crews, tools, rendering templates, and tests. Claude Code must never read files from the input
folders (`job-descriptions/`, `resumes/`, `interview-notes/`) to perform an actual interviewing
analysis itself, and must never invoke the `interviewer` CLI against real candidate data on the
user's behalf unless explicitly asked to do so for debugging. Treat any PDF in those folders as
application input/test fixture data, not as something to analyze directly.

## Project Layout

```
src/interviewer/
├── cli.py                # Typer app; one subcommand per capability
├── config.py             # env/.env loading, LLM construction, folder paths, profile loading
├── io_utils.py           # PDF text extraction, input-file resolution/picking
├── models.py             # Pydantic schemas for each crew's structured output
├── crews/                # one module per capability: agent(s) + task(s) -> Pydantic model
└── rendering/
    ├── render.py         # Jinja2 environment + render_to_file()
    └── templates/        # one *.html.j2 per capability's output file
tests/                    # pytest; crew calls are stubbed, no live API calls
```

Each capability follows the same shape: `cli.py` resolves input PDFs → extracts text via
`io_utils.extract_pdf_text` → calls the matching `crews/<capability>.run(...)` → gets back a
typed Pydantic model (see `models.py`) → renders it with `rendering/render.render_to_file` using
the matching Jinja2 template → saves the HTML file and prints its path.

`candidate_comparison.py` composes `resume_assessment.run()` per candidate rather than
duplicating assessment logic.

## Output Format Contract

`rendering/templates/resume_assessment.html.j2` has a strict, documented format contract — see
the `resume-assessment-format` skill, which still defines the exact structure, section order,
HTML/CSS, and verdict rules that template must satisfy. If that format ever needs to change,
update the skill and the template together; the skill is the source of truth, the template is
its implementation.

## Development Conventions

- Imports: use `import <module>` and reference names as `<module>.<name>` — never
  `from <module> import <name>` for individual types, classes, or functions. This applies to
  stdlib, third-party, and this project's own `interviewer.*` modules alike. The only exception
  is `from __future__ import annotations`. (`from pkg import submodule` to import a submodule
  is fine — e.g. `from interviewer.crews import resume_assessment` — since that imports a
  module, not an individual name.)
- Dependency management: `uv` (`uv sync`, `uv add <pkg>`, `uv run <cmd>`).
- Run tests: `uv run pytest`.
- Lint: `uv run ruff check src tests`.
- Run the CLI locally: `uv run interviewer <command> --help`.
- New crew outputs should be typed Pydantic models in `models.py`, rendered via a Jinja2
  template — avoid asking an LLM to produce raw HTML directly, since that can't guarantee a
  consistent format run to run.
- Tests must not make live LLM API calls — stub `crews/*.run` at the CLI test layer, as the
  existing tests in `tests/test_cli.py` do.

## Git Contributions

See the `git-contrib-rules` skill (feature branches only, conventional commit messages) — it
applies to all development work in this repository.
