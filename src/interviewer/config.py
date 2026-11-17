"""Environment, folder layout, and profile loading."""

from __future__ import annotations

import os
import pathlib
import typing

import crewai
import dotenv

dotenv.load_dotenv()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
JOB_DESCRIPTIONS_DIR = PROJECT_ROOT / "job-descriptions"
RESUMES_DIR = PROJECT_ROOT / "resumes"
INTERVIEW_NOTES_DIR = PROJECT_ROOT / "interview-notes"

COMPANY_PROFILE_PATH = PROJECT_ROOT / "company-profile.md"
CLIENT_PROFILE_PATH = JOB_DESCRIPTIONS_DIR / "client-profile.md"

ModelTier = typing.Literal["small_fast", "haiku", "sonnet", "opus"]

_TIER_ENV_VARS: dict[ModelTier, str] = {
    "small_fast": "ANTHROPIC_SMALL_FAST_MODEL",
    "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
}


def get_llm(tier: ModelTier) -> crewai.LLM:
    """Build the Anthropic-native LLM for a given model tier, routed at the private endpoint.

    Uses CrewAI's native Anthropic provider (`model="anthropic/<id>"`) pointed at
    ANTHROPIC_BASE_URL. Auth is ANTHROPIC_AUTH_TOKEN (sent as a Bearer token via
    `auth_token`), not ANTHROPIC_API_KEY (sent as an `x-api-key` header) — this project's
    private endpoint requires Bearer auth. CrewAI's native Anthropic provider always
    requires a non-empty `api_key` field internally before it will build the real client;
    `client_params` overrides that back to `None` at the point the `anthropic.Anthropic`
    client is actually constructed, so only `auth_token` is ever sent on the wire.

    `tier` picks which ANTHROPIC_DEFAULT_*_MODEL / ANTHROPIC_SMALL_FAST_MODEL env var
    supplies the model id; if that var isn't set, falls back to ANTHROPIC_MODEL.
    """
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    missing = [
        name
        for name, value in (
            ("ANTHROPIC_BASE_URL", base_url),
            ("ANTHROPIC_AUTH_TOKEN", auth_token),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"{', '.join(missing)} not set. Copy .env.example to .env and fill it in."
        )

    tier_var = _TIER_ENV_VARS[tier]
    model = os.environ.get(tier_var) or os.environ.get("ANTHROPIC_MODEL")
    if not model:
        raise RuntimeError(
            f"Neither {tier_var} nor ANTHROPIC_MODEL is set. Copy .env.example to .env and "
            "fill it in."
        )

    return crewai.LLM(
        model=f"anthropic/{model}",
        base_url=base_url,
        api_key="unused",  # placeholder only; nulled out below, never sent on the wire
        client_params={"api_key": None, "auth_token": auth_token},
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
