from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path

# Optional: load a local .env file so the container can read backend/.env directly
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

_DOTENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if load_dotenv and _DOTENV_PATH.exists():
    load_dotenv(dotenv_path=_DOTENV_PATH)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    chroma_host: str = field(default_factory=lambda: os.getenv("CHROMA_HOST", "localhost"))
    chroma_port: int = field(default_factory=lambda: int(os.getenv("CHROMA_PORT", "8000")))
    chroma_collection: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION", "true-home-kb"))
    langfuse_public_key: str | None = field(default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY"))
    langfuse_secret_key: str | None = field(default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY"))
    langfuse_host: str = field(default_factory=lambda: os.getenv("LANGFUSE_HOST", "http://localhost:3000"))


def get_settings() -> Settings:
    return Settings()
