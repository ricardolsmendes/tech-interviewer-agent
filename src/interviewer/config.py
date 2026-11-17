"""Environment, folder layout, and profile loading."""

from __future__ import annotations

import os
from pathlib import Path

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOB_DESCRIPTIONS_DIR = PROJECT_ROOT / "job-descriptions"
RESUMES_DIR = PROJECT_ROOT / "resumes"
INTERVIEW_NOTES_DIR = PROJECT_ROOT / "interview-notes"

COMPANY_PROFILE_PATH = PROJECT_ROOT / "company-profile.md"
CLIENT_PROFILE_PATH = JOB_DESCRIPTIONS_DIR / "client-profile.md"

_REQUIRED_LITELLM_VARS = ("LITELLM_BASE_URL", "LITELLM_API_KEY", "LITELLM_MODEL")


def get_llm() -> LLM:
    """Build the LLM shared by all crews, routed through the private LiteLLM endpoint.

    The endpoint is treated as a custom OpenAI-compatible provider: CrewAI's LLM class
    uses the native OpenAI client whenever `base_url` is set and the model is prefixed
    with "openai/", regardless of which model the endpoint actually serves.
    """
    missing = [name for name in _REQUIRED_LITELLM_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"{', '.join(missing)} not set. Copy .env.example to .env and fill it in."
        )
    return LLM(
        model=f"openai/{os.environ['LITELLM_MODEL']}",
        base_url=os.environ["LITELLM_BASE_URL"],
        api_key=os.environ["LITELLM_API_KEY"],
    )


def read_company_profile() -> str | None:
    """Raw contents of company-profile.md, if the interviewer created one."""
    if COMPANY_PROFILE_PATH.is_file():
        return COMPANY_PROFILE_PATH.read_text().strip()
    return None


def read_client_profile() -> str | None:
    """Raw contents of job-descriptions/client-profile.md, if present."""
    if CLIENT_PROFILE_PATH.is_file():
        return CLIENT_PROFILE_PATH.read_text().strip()
    return None


def profile_context() -> str:
    """Company/client profile text to inject into fit-judgment prompts, or "" if none exist.

    Client-level preferences take precedence over company-level defaults when they differ.
    """
    company = read_company_profile()
    client = read_client_profile()
    parts = []
    if company:
        parts.append(f"Company profile (use to calibrate overall assessment weighting):\n{company}")
    if client:
        parts.append(
            "Client profile (preferences here take precedence over the company profile "
            f"when they differ):\n{client}"
        )
    return "\n\n".join(parts)
