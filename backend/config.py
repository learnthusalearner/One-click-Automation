"""
config.py
─────────
Loads credentials from .env and exposes typed config objects.
Raises clear errors if required keys are missing.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one directory up from this file, or cwd)
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


def is_placeholder(val: str) -> bool:
    val_lower = val.lower()
    return not val or "your_" in val_lower or "placeholder" in val_lower


def _require(key: str) -> str:
    """Return env var or raise a descriptive error."""
    val = os.getenv(key, "").strip()
    if is_placeholder(val):
        raise EnvironmentError(
            f"Missing required environment variable: {key}\n"
            f"  → Copy .env.example to .env and fill in {key}"
        )
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


# ─── Credential dataclasses ───────────────────────────────────────────────────

@dataclass(frozen=True)
class FacebookConfig:
    page_id: str
    access_token: str

    @classmethod
    def from_env(cls) -> "FacebookConfig":
        return cls(
            page_id=_require("FACEBOOK_PAGE_ID"),
            access_token=_require("FACEBOOK_ACCESS_TOKEN"),
        )


@dataclass(frozen=True)
class InstagramConfig:
    account_id: str
    access_token: str

    @classmethod
    def from_env(cls) -> "InstagramConfig":
        return cls(
            account_id=_require("INSTAGRAM_ACCOUNT_ID"),
            access_token=_require("INSTAGRAM_ACCESS_TOKEN"),
        )


@dataclass(frozen=True)
class LinkedInConfig:
    access_token: str
    author_urn: str

    @classmethod
    def from_env(cls) -> "LinkedInConfig":
        return cls(
            access_token=_require("LINKEDIN_ACCESS_TOKEN"),
            author_urn=_require("LINKEDIN_AUTHOR_URN"),
        )


@dataclass(frozen=True)
class AppConfig:
    facebook: FacebookConfig | None
    instagram: InstagramConfig | None
    linkedin: LinkedInConfig | None

    @classmethod
    def from_env(cls, platforms: list[str] | None = None) -> "AppConfig":
        """
        Load config. If `platforms` is given, only load credentials for those.
        Skips missing credentials for unselected platforms gracefully.
        """
        all_platforms = platforms or ["facebook", "instagram", "linkedin"]

        def _load(name: str, loader):
            if name not in all_platforms:
                return None
            try:
                return loader()
            except EnvironmentError as e:
                # Non-fatal: surface as warning later
                return e

        return cls(
            facebook=_load("facebook", FacebookConfig.from_env),
            instagram=_load("instagram", InstagramConfig.from_env),
            linkedin=_load("linkedin", LinkedInConfig.from_env),
        )