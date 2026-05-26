from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path


_DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _read_env_file_value(key: str) -> str | None:
    if not _DOTENV_PATH.exists():
        return None

    try:
        lines = _DOTENV_PATH.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None

    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line.startswith(f"{key}="):
            continue

        first_value = line.split("=", 1)[1].strip()
        parts = [first_value]

        for following in lines[index + 1 :]:
            item = following.strip()
            if not item:
                break
            if "=" in item and item.split("=", 1)[0].isidentifier():
                break
            parts.append(item)

        candidate = "".join(parts).replace("\n", "").strip()
        if candidate:
            return candidate

    return None


def _get_env_value(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    if value:
        return value

    file_value = _read_env_file_value(key)
    if file_value:
        return file_value

    return default


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = field(default_factory=lambda: _get_env_value("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: _get_env_value("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini")
    chroma_host: str = field(default_factory=lambda: _get_env_value("CHROMA_HOST", "localhost") or "localhost")
    chroma_port: int = field(default_factory=lambda: int(_get_env_value("CHROMA_PORT", "8000") or "8000"))
    chroma_collection: str = field(default_factory=lambda: _get_env_value("CHROMA_COLLECTION", "true-home-kb") or "true-home-kb")
    langfuse_public_key: str | None = field(default_factory=lambda: _get_env_value("LANGFUSE_PUBLIC_KEY"))
    langfuse_secret_key: str | None = field(default_factory=lambda: _get_env_value("LANGFUSE_SECRET_KEY"))
    langfuse_host: str = field(default_factory=lambda: _get_env_value("LANGFUSE_HOST", "http://localhost:3000") or "http://localhost:3000")


def get_settings() -> Settings:
    return Settings()
