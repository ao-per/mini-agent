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

    if not api_key:
        raise RuntimeError("缺少 ZAI_API_KEY，请检查项目根目录下的 .env")

    return Settings(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )


settings = load_settings()
