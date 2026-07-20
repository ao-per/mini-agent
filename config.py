import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    model_timeout_seconds: float
    model_max_retries: int
    notes_root: Path
    log_level: str


def load_settings() -> Settings:
    api_key = os.getenv("ZAI_API_KEY")
    base_url = os.getenv(
        "ZAI_BASE_URL",
        "https://open.bigmodel.cn/api/paas/v4/",
    )
    model = os.getenv(
        "ZAI_MODEL",
        "glm-5.2",
    )
    model_timeout_seconds = float(
        os.getenv(
            "MODEL_TIMEOUT_SECONDS",
            "60",
        )
    )

    model_max_retries = int(
        os.getenv(
            "MODEL_MAX_RETRIES",
            "2",
        )
    )

    notes_root_value = Path(os.getenv("NOTES_ROOT", "notes")).expanduser()
    if not notes_root_value.is_absolute():
        notes_root_value = PROJECT_ROOT / notes_root_value
    notes_root = notes_root_value.resolve()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if model_timeout_seconds <= 0:
        raise RuntimeError("MODEL_TIMEOUT_SECONDS 必须大于 0")

    if model_max_retries < 0:
        raise RuntimeError("MODEL_MAX_RETRIES 不能小于 0")

    if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise RuntimeError("LOG_LEVEL 必须是 DEBUG、INFO、WARNING、ERROR 或 CRITICAL")

    if not api_key:
        raise RuntimeError("缺少 ZAI_API_KEY，请检查项目根目录下的 .env")

    return Settings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        model_timeout_seconds=model_timeout_seconds,
        model_max_retries=model_max_retries,
        notes_root=notes_root,
        log_level=log_level,
    )


settings = load_settings()
