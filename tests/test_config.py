import pytest

from interviewer.config import get_llm


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://private-gateway.example.com")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "sk-ant-token")


def test_get_llm_requires_base_url_and_auth_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="ANTHROPIC_BASE_URL"):
        get_llm("sonnet")


def test_get_llm_requires_a_model_for_the_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    monkeypatch.delenv("ANTHROPIC_DEFAULT_SONNET_MODEL", raising=False)

    with pytest.raises(RuntimeError, match="ANTHROPIC_DEFAULT_SONNET_MODEL"):
        get_llm("sonnet")


def test_get_llm_falls_back_to_anthropic_model(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.delenv("ANTHROPIC_DEFAULT_HAIKU_MODEL", raising=False)
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-haiku-fallback")

    llm = get_llm("haiku")

    assert llm.model == "claude-haiku-fallback"


def test_get_llm_prefers_tier_specific_model(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-fallback")
    monkeypatch.setenv("ANTHROPIC_DEFAULT_OPUS_MODEL", "claude-opus-tier")

    llm = get_llm("opus")

    assert llm.model == "claude-opus-tier"


def test_get_llm_authenticates_with_bearer_token_not_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_DEFAULT_SONNET_MODEL", "claude-sonnet-test")

    llm = get_llm("sonnet")
    client = llm._get_sync_client()

    assert client.api_key is None
    assert client.auth_token == "sk-ant-token"
    assert client.base_url == "https://private-gateway.example.com"
