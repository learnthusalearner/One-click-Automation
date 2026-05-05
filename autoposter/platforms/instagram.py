"""
platforms/instagram.py
───────────────────────
Posts a photo + caption to Instagram via the Meta Graph API.

Instagram publishing is a two-step process:
  1. Create a media container  →  POST /{ig-user-id}/media
  2. Publish the container     →  POST /{ig-user-id}/media_publish

Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user/media
Note: Instagram requires a PUBLIC image URL — local files are not accepted.
"""

import time
import requests

from config import InstagramConfig
from platforms.base import BasePlatform, PostPayload, PostResult

GRAPH_API = "https://graph.facebook.com/v19.0"
CONTAINER_POLL_INTERVAL = 3   # seconds between status checks
CONTAINER_MAX_POLLS = 10      # max retries before giving up


class InstagramPlatform(BasePlatform):

    def __init__(self, cfg: InstagramConfig) -> None:
        self._cfg = cfg

    @property
    def name(self) -> str:
        return "Instagram"

    # ── Step 1: Create media container ────────────────────────────────────────

    def _create_container(self, image_url: str, caption: str) -> str | None:
        """Returns the container ID, or None on failure."""
        resp = requests.post(
            f"{GRAPH_API}/{self._cfg.account_id}/media",
            params={"access_token": self._cfg.access_token},
            data={"image_url": image_url, "caption": caption},
            timeout=30,
        )
        data = resp.json()
        return data.get("id")

    # ── Step 2: Wait for container to be ready ────────────────────────────────

    def _wait_for_container(self, container_id: str) -> bool:
        """Poll until status_code == FINISHED (or timeout)."""
        for _ in range(CONTAINER_MAX_POLLS):
            resp = requests.get(
                f"{GRAPH_API}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": self._cfg.access_token,
                },
                timeout=15,
            )
            status = resp.json().get("status_code", "")
            if status == "FINISHED":
                return True
            if status == "ERROR":
                return False
            time.sleep(CONTAINER_POLL_INTERVAL)
        return False

    # ── Step 3: Publish the container ─────────────────────────────────────────

    def _publish_container(self, container_id: str) -> dict:
        resp = requests.post(
            f"{GRAPH_API}/{self._cfg.account_id}/media_publish",
            params={"access_token": self._cfg.access_token},
            data={"creation_id": container_id},
            timeout=30,
        )
        return resp.json()

    # ── Public entry point ────────────────────────────────────────────────────

    def publish(self, payload: PostPayload) -> PostResult:
        if not payload.image_url:
            return PostResult(
                platform=self.name,
                success=False,
                error="Instagram requires a public image URL (image_url not set in payload).",
            )

        try:
            # 1. Create container
            container_id = self._create_container(payload.image_url, payload.caption)
            if not container_id:
                return PostResult(
                    platform=self.name, success=False, error="Failed to create media container."
                )

            # 2. Wait for processing
            ready = self._wait_for_container(container_id)
            if not ready:
                return PostResult(
                    platform=self.name, success=False, error="Container processing timed out or errored."
                )

            # 3. Publish
            result = self._publish_container(container_id)

            if "id" in result:
                media_id = result["id"]
                return PostResult(
                    platform=self.name,
                    success=True,
                    post_id=media_id,
                    url=f"https://www.instagram.com/p/{media_id}/",
                )
            else:
                error = result.get("error", {})
                return PostResult(
                    platform=self.name,
                    success=False,
                    error=f"{error.get('code', '?')}: {error.get('message', str(result))}",
                )

        except requests.RequestException as exc:
            return PostResult(platform=self.name, success=False, error=str(exc))
