# tech-interviewer-agent

A CrewAI-powered assistant for tech interviewers.

This agent helps tech interviewers do their job at scale. It has five main capabilities:

1. Describe the required soft and hard skills in different technology stacks, according to a given
job description.
1. Compare candidate resumes with a given job description and describe the candidates' affinity to
the role.
1. Compare multiple candidates against each other for a given role and recommend the best fit.
1. Generate suitable interview questions, tailored to each candidate, considering the job
description and the candidate's experience.
1. After an interview, summarize the candidate's propensity to take the role, given the interview
notes.

It runs entirely as a CLI, backed by [CrewAI](https://www.crewai.com/), routed through a private
Anthropic-compatible endpoint — no chat session required.

## Setup

1. Install [uv](https://docs.astral.sh/uv/).
2. Install dependencies: `uv sync`.
3. Copy `.env.example` to `.env` and set `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, and the
   model id env vars (`ANTHROPIC_MODEL` as a fallback, plus any of the per-tier
   `ANTHROPIC_SMALL_FAST_MODEL` / `ANTHROPIC_DEFAULT_HAIKU_MODEL` /
   `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_OPUS_MODEL` your endpoint serves).

## How to use

Drop the relevant files into the input folders and run the CLI. Here are the usage patterns this
agent supports.

### 1. List skills required for a role

Place the job description PDF in `job-descriptions/`, then run:

```sh
uv run interviewer skill-listing
```

The agent reads the JD and produces a breakdown of required hard and soft skills, saved as
`job-descriptions/Senior-Data-Engineer_skill-listing.html`.

### 2. Assess a candidate's fit for a role

Place the job description in `job-descriptions/` and the resume in `resumes/`, then run:

```sh
uv run interviewer resume-assessment
```

The agent reads both files and produces a structured assessment — verdict, requirements
coverage, standout qualities, concerns, and a hiring recommendation — saved as
`resumes/Alice-Johnson-CV_resume-assessment.html`.

### 3. Compare candidates for a role

With two or more resumes in `resumes/` and a JD in `job-descriptions/`, run:

```sh
uv run interviewer compare
```

The agent ranks the candidates, explains the key differentiators, and recommends the strongest
fit, saved as `job-descriptions/Senior-Data-Engineer_candidate-comparison.html`. It also produces
(or reuses) each candidate's individual resume assessment along the way.

### 4. Generate tailored interview questions

```sh
uv run interviewer interview-questions
```

The agent produces a set of technical and behavioural questions tailored to the candidate's
specific experience and the role's requirements, saved as
`resumes/Bob-Smith-CV_interview-questions.html`.

### 5. Summarise post-interview performance

After an interview, place the interviewer's notes in `interview-notes/`, then run:

```sh
uv run interviewer interview-summary
```

The agent reads the JD, the resume, and the interview notes together and produces a summary
covering performance, fit, and any reservations worth considering before making a decision,
saved as `resumes/Carol-White-CV_interview-summary.html`.

---

### Tips

- **Accepted formats: PDF only.** Word documents must be saved as PDF before placing them in the
  folders.
- **Explicit file paths:** every command accepts `--jd`, `--resume`, `--notes`, or `--resumes`
  (for `compare`) to pick a specific file instead of relying on folder auto-detection, e.g.
  `uv run interviewer resume-assessment --jd job-descriptions/JD.pdf --resume resumes/Alice.pdf`.
- **Multiple files in a folder:** if more than one JD or resume PDF is present and you didn't
  pass an explicit path, the CLI will ask you to pick one from a numbered list.
- **Company context:** copy `company-profile-template.md` to `company-profile.md` in the root
  folder and fill it in. The agent reads it at the start of every run to calibrate
  assessments to your organisation's hiring priorities.
- **Client context:** for consultancies placing candidates at a specific client, copy
  `job-descriptions/client-profile-template.md` to `job-descriptions/client-profile.md` and
  fill it in. The agent uses it to refine assessments for that engagement. Replace it whenever
  you switch to a new client.
- **Printing:** any HTML output file can be opened in a browser and saved as PDF via
  File → Print → Save as PDF.

## How to contribute

Please make sure to take a moment and read the [Code of
Conduct](https://github.com/ricardolsmendes/tech-interviewer-agent/blob/main/.github/CODE_OF_CONDUCT.md).

### Report issues

Please report bugs and suggest features via the [GitHub
Issues](https://github.com/ricardolsmendes/tech-interviewer-agent/issues).

Before opening an issue, search the tracker for possible duplicates. If you find
a duplicate, please add a comment saying that you encountered the problem as
well.

### Contribute code

Please make sure to read the [Contributing
Guide](https://github.com/ricardolsmendes/tech-interviewer-agent/blob/main/.github/CONTRIBUTING.md)
before making a pull request.
