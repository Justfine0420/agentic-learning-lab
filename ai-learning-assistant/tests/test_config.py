import pytest

from app.config import (
    LLMSettings,
    get_llm_settings,
    get_ollama_embedding_settings,
    normalize_ollama_embedding_base_url,
    require_llm_api_key,
)


PROVIDER_ENV_NAMES = [
    "LLM_PROVIDER",
    "VOLCENGINE_AGENT_PLAN_API_KEY",
    "VOLCENGINE_AGENT_PLAN_BASE_URL",
    "VOLCENGINE_AGENT_PLAN_MODEL",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "OLLAMA_API_KEY",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "OLLAMA_EMBEDDING_BASE_URL",
    "OLLAMA_EMBEDDING_MODEL",
]


@pytest.fixture(autouse=True)
def clean_provider_env(monkeypatch):
    for name in PROVIDER_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_default_provider_uses_volcengine_agent_plan():
    settings = get_llm_settings(load_dotenv_file=False)

    assert settings.provider == "volcengine_agent_plan"
    assert settings.api_key == ""
    assert settings.api_key_env == "VOLCENGINE_AGENT_PLAN_API_KEY"
    assert settings.base_url == "https://ark.cn-beijing.volces.com/api/plan/v3"
    assert settings.model == "ark-code-latest"
    assert settings.requires_api_key is True


def test_volcengine_coding_alias_uses_agent_plan_config():
    settings = get_llm_settings(provider="volcengine_coding", load_dotenv_file=False)

    assert settings.provider == "volcengine_coding"
    assert settings.api_key_env == "VOLCENGINE_AGENT_PLAN_API_KEY"
    assert settings.base_url == "https://ark.cn-beijing.volces.com/api/plan/v3"


def test_reads_deepseek_provider_from_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://example.deepseek.test")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-test-model")

    settings = get_llm_settings(load_dotenv_file=False)

    assert settings.provider == "deepseek"
    assert settings.api_key == "test-deepseek-key"
    assert settings.base_url == "https://example.deepseek.test"
    assert settings.model == "deepseek-test-model"
    assert settings.requires_api_key is True


def test_ollama_provider_does_not_require_real_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")

    settings = get_llm_settings(load_dotenv_file=False)

    assert settings.provider == "ollama"
    assert settings.api_key == "ollama"
    assert settings.api_key_env == "OLLAMA_API_KEY"
    assert settings.base_url == "http://localhost:11434/v1"
    assert settings.model == "qwen3:8b"
    assert settings.requires_api_key is False
    assert require_llm_api_key(settings) == settings


def test_default_ollama_embedding_settings_use_local_ollama():
    settings = get_ollama_embedding_settings(load_dotenv_file=False)

    assert settings.base_url == "http://localhost:11434"
    assert settings.model == "mxbai-embed-large"


def test_reads_ollama_embedding_settings_from_environment(monkeypatch):
    monkeypatch.setenv("OLLAMA_EMBEDDING_BASE_URL", "http://127.0.0.1:11434/v1/")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "qwen3-embedding:latest")

    settings = get_ollama_embedding_settings(load_dotenv_file=False)

    assert settings.base_url == "http://127.0.0.1:11434"
    assert settings.model == "qwen3-embedding:latest"


@pytest.mark.parametrize(
    ("base_url", "expected"),
    [
        ("http://localhost:11434", "http://localhost:11434"),
        ("http://localhost:11434/", "http://localhost:11434"),
        ("http://localhost:11434/v1", "http://localhost:11434"),
        ("   ", "http://localhost:11434"),
    ],
)
def test_normalize_ollama_embedding_base_url(base_url, expected):
    assert normalize_ollama_embedding_base_url(base_url) == expected


def test_rejects_unsupported_provider():
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_settings(provider="unknown", load_dotenv_file=False)


def test_requires_api_key_for_cloud_provider():
    settings = LLMSettings(
        provider="deepseek",
        api_key="",
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        requires_api_key=True,
    )

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        require_llm_api_key(settings)
