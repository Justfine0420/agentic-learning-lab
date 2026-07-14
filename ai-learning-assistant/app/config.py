from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class LLMProviderConfig:
    api_key_env: str
    base_url_env: str
    model_env: str
    default_base_url: str
    default_model: str
    default_api_key: str = ""
    requires_api_key: bool = True


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    api_key: str
    api_key_env: str
    base_url: str
    model: str
    requires_api_key: bool


@dataclass(frozen=True)
class OllamaEmbeddingSettings:
    base_url: str
    model: str


DEFAULT_OLLAMA_EMBEDDING_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_EMBEDDING_MODEL = "mxbai-embed-large"


VOLCENGINE_AGENT_PLAN_CONFIG = LLMProviderConfig(
    api_key_env="VOLCENGINE_AGENT_PLAN_API_KEY",
    base_url_env="VOLCENGINE_AGENT_PLAN_BASE_URL",
    model_env="VOLCENGINE_AGENT_PLAN_MODEL",
    default_base_url="https://ark.cn-beijing.volces.com/api/plan/v3",
    default_model="ark-code-latest",
)


LLM_PROVIDERS: dict[str, LLMProviderConfig] = {
    "volcengine_agent_plan": VOLCENGINE_AGENT_PLAN_CONFIG,
    "volcengine_coding": VOLCENGINE_AGENT_PLAN_CONFIG,
    "deepseek": LLMProviderConfig(
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        model_env="DEEPSEEK_MODEL",
        default_base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash",
    ),
    "ollama": LLMProviderConfig(
        api_key_env="OLLAMA_API_KEY",
        base_url_env="OLLAMA_BASE_URL",
        model_env="OLLAMA_MODEL",
        default_base_url="http://localhost:11434/v1",
        default_model="qwen3:8b",
        default_api_key="ollama",
        requires_api_key=False,
    ),
}


def load_project_env(env_file: Path = ENV_FILE) -> None:
    if env_file.exists():
        load_dotenv(env_file, override=False)


def get_env_value(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    return value if value else default


def get_llm_settings(
    provider: str | None = None,
    *,
    load_dotenv_file: bool = True,
) -> LLMSettings:
    if load_dotenv_file:
        load_project_env()

    selected_provider = (provider or get_env_value("LLM_PROVIDER", "volcengine_agent_plan")).strip().lower()

    if selected_provider not in LLM_PROVIDERS:
        supported = ", ".join(sorted(LLM_PROVIDERS))
        raise ValueError(f"Unsupported LLM provider: {selected_provider}. Supported: {supported}.")

    provider_config = LLM_PROVIDERS[selected_provider]

    return LLMSettings(
        provider=selected_provider,
        api_key=get_env_value(provider_config.api_key_env, provider_config.default_api_key),
        api_key_env=provider_config.api_key_env,
        base_url=get_env_value(provider_config.base_url_env, provider_config.default_base_url),
        model=get_env_value(provider_config.model_env, provider_config.default_model),
        requires_api_key=provider_config.requires_api_key,
    )


def normalize_ollama_embedding_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    if normalized.endswith("/v1"):
        normalized = normalized[: -len("/v1")]
    return normalized or DEFAULT_OLLAMA_EMBEDDING_BASE_URL


def get_ollama_embedding_settings(
    *,
    load_dotenv_file: bool = True,
) -> OllamaEmbeddingSettings:
    if load_dotenv_file:
        load_project_env()

    return OllamaEmbeddingSettings(
        base_url=normalize_ollama_embedding_base_url(
            get_env_value("OLLAMA_EMBEDDING_BASE_URL", DEFAULT_OLLAMA_EMBEDDING_BASE_URL)
        ),
        model=get_env_value("OLLAMA_EMBEDDING_MODEL", DEFAULT_OLLAMA_EMBEDDING_MODEL),
    )


def require_llm_api_key(settings: LLMSettings | None = None) -> LLMSettings:
    current_settings = settings or get_llm_settings()

    if current_settings.requires_api_key and not current_settings.api_key:
        raise RuntimeError(f"Missing required environment variable: {current_settings.api_key_env}.")

    return current_settings
