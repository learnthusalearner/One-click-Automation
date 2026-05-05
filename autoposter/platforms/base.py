"""
platforms/base.py
─────────────────
Abstract base class that every platform module must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PostPayload:
    """Everything a platform needs to publish a post."""
    caption: str                      # Platform-optimised caption
    image_path: Path | None = None    # Local file path (used by Facebook)
    image_url: str | None = None      # Public URL (used by Instagram, LinkedIn)


@dataclass
class PostResult:
    """Unified result returned by every platform after posting."""
    platform: str
    success: bool
    post_id: str | None = None        # Platform's returned post/media ID
    url: str | None = None            # Direct link to the live post (if available)
    error: str | None = None          # Error message on failure

    def __str__(self) -> str:
        if self.success:
            tail = f" → {self.url}" if self.url else f" (id: {self.post_id})"
            return f"[✓] {self.platform}{tail}"
        return f"[✗] {self.platform}: {self.error}"


class BasePlatform(ABC):
    """
    All platform adapters inherit from this class.
    They must implement `name` and `publish()`.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable platform name, e.g. 'Facebook'."""
        ...

    @abstractmethod
    def publish(self, payload: PostPayload) -> PostResult:
        """
        Upload the image and caption to the platform.
        Must return a PostResult — never raise.
        """
        ...

    def _safe_publish(self, payload: PostPayload) -> PostResult:
        """Wraps publish() to catch any unexpected exceptions."""
        try:
            return self.publish(payload)
        except Exception as exc:
            return PostResult(
                platform=self.name,
                success=False,
                error=f"Unexpected error: {exc}",
            )
