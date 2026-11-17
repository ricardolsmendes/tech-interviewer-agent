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

DEFAULT_MODEL = "anthropic/claude-sonnet-4-5-20250929"


def get_llm() -> LLM:
    """Build the Anthropic-backed LLM shared by all crews."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
    return LLM(model=model, api_key=api_key)


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
