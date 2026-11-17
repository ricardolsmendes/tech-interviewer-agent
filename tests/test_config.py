import pytest

from interviewer.config import get_llm


def test_get_llm_requires_litellm_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LITELLM_BASE_URL", raising=False)
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)
    monkeypatch.delenv("LITELLM_MODEL", raising=False)

    with pytest.raises(RuntimeError, match="LITELLM_BASE_URL"):
        get_llm()


def test_get_llm_routes_through_private_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LITELLM_BASE_URL", "https://litellm.internal.example.com")
    monkeypatch.setenv("LITELLM_API_KEY", "sk-test")
    monkeypatch.setenv("LITELLM_MODEL", "claude-sonnet")

    llm = get_llm()

    assert llm.base_url == "https://litellm.internal.example.com"
    assert llm.api_key == "sk-test"
    assert llm.model == "claude-sonnet"
