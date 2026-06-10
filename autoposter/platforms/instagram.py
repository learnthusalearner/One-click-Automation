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
from pathlib import Path

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

    def _create_container(self, image_url: str, caption: str) -> tuple[str | None, str | None]:
        """Returns (container_id, None) or (None, error_msg) on failure."""
        resp = requests.post(
            f"{GRAPH_API}/{self._cfg.account_id}/media",
            params={"access_token": self._cfg.access_token},
            data={"image_url": image_url, "caption": caption},
            timeout=30,
        )
        try:
            data = resp.json()
            if "id" in data:
                return data["id"], None
            error = data.get("error", {})
            return None, f"{error.get('code', '?')}: {error.get('message', str(data))}"
        except Exception as exc:
            return None, f"Response parsing error: {exc} (status {resp.status_code})"

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

    def _upload_local_image(self, image_path: Path) -> str | None:
        """Uploads a local image to a temporary file host and returns a public URL.
        Tries tmpfiles.org first, then falls back to file.io.
        """
        # Try tmpfiles.org
        try:
            url = "https://tmpfiles.org/api/v1/upload"
            with open(image_path, "rb") as fh:
                files = {"file": ("instagram_upload.jpg", fh, "image/jpeg")}
                resp = requests.post(url, files=files, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    raw_url = data["data"]["url"]
                    # Replace https://tmpfiles.org/ with https://tmpfiles.org/dl/ to get direct link
                    return raw_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
        except Exception:
            pass

        # Try file.io fallback
        try:
            url = "https://file.io"
            with open(image_path, "rb") as fh:
                files = {"file": ("instagram_upload.jpg", fh, "image/jpeg")}
                resp = requests.post(url, files=files, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    return data.get("link")
        except Exception:
            pass

        return None

    # ── Public entry point ────────────────────────────────────────────────────

    def publish(self, payload: PostPayload) -> PostResult:
        image_url = payload.image_url

        if not image_url and payload.image_path:
            image_path = Path(payload.image_path)
            if image_path.exists():
                image_url = self._upload_local_image(image_path)
                if not image_url:
                    return PostResult(
                        platform=self.name,
                        success=False,
                        error="Failed to upload local image to a temporary public URL.",
                    )
                print(f"\n  [Instagram] Uploaded local image to temporary public URL: {image_url}")
            else:
                return PostResult(
                    platform=self.name,
                    success=False,
                    error=f"Local image path does not exist: {image_path}",
                )

        if not image_url:
            return PostResult(
                platform=self.name,
                success=False,
                error="Instagram requires a public image URL or a valid local image path.",
            )

        try:
            # 1. Create container
            container_id, err = self._create_container(image_url, payload.caption)
            if not container_id:
                return PostResult(
                    platform=self.name, success=False, error=f"Failed to create media container: {err}"
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
