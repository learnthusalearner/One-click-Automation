"""
platforms/instagram.py
───────────────────────
Posts a photo + caption to Instagram via the Meta Graph API.

This module is designed to be beginner-friendly. Instagram posting is a 2-step process:
  1. Create a media container (tells Instagram where the image is and the caption)
  2. Publish the container (tells Instagram to post the container live)
  3. Query the live post's URL (permalink) so the user can click it directly.
"""

import time
import requests
from pathlib import Path

from config import InstagramConfig
from platforms.base import BasePlatform, PostPayload, PostResult

# The base URL for Meta Graph API calls
GRAPH_API = "https://graph.facebook.com/v19.0"
CONTAINER_POLL_INTERVAL = 3   # How many seconds to wait between checking if container is ready
CONTAINER_MAX_POLLS = 10      # Maximum number of checks before giving up


class InstagramPlatform(BasePlatform):
    """
    Adapter that connects to the Instagram API.
    Inherits from BasePlatform and implements the publish method.
    """

    def __init__(self, cfg: InstagramConfig) -> None:
        # Save the credentials passed in from config.py
        self._cfg = cfg

    @property
    def name(self) -> str:
        return "Instagram"

    # ── Step 1: Create media container ────────────────────────────────────────

    def _create_container(self, image_url: str, caption: str) -> tuple[str | None, str | None]:
        """
        Creates a media container on Instagram.
        Returns:
            (container_id, None) on success.
            (None, error_message) on failure.
        """
        # We send a POST request to /{instagram_account_id}/media with our token, image URL, and caption.
        resp = requests.post(
            f"{GRAPH_API}/{self._cfg.account_id}/media",
            params={"access_token": self._cfg.access_token},
            data={"image_url": image_url, "caption": caption},
            timeout=30,
        )
        try:
            data = resp.json()
            if "id" in data:
                return data["id"], None # Successfully created container
            error = data.get("error", {})
            return None, f"{error.get('code', '?')}: {error.get('message', str(data))}"
        except Exception as exc:
            return None, f"Response parsing error: {exc} (status {resp.status_code})"

    # ── Step 2: Wait for container to be ready ────────────────────────────────

    def _wait_for_container(self, container_id: str) -> bool:
        """
        Meta processes the image in the background. We must poll the container
        status and wait until status_code becomes "FINISHED" before publishing.
        """
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
            time.sleep(CONTAINER_POLL_INTERVAL) # Sleep briefly before checking again
        return False

    # ── Step 3: Publish the container ─────────────────────────────────────────

    def _publish_container(self, container_id: str) -> dict:
        """
        Publish the processed media container to make the post live.
        """
        resp = requests.post(
            f"{GRAPH_API}/{self._cfg.account_id}/media_publish",
            params={"access_token": self._cfg.access_token},
            data={"creation_id": container_id},
            timeout=30,
        )
        return resp.json()

    # ── Step 4: Upload Local Image (If no public URL is provided) ─────────────

    def _upload_local_image(self, image_path: Path) -> str | None:
        """
        Instagram requires a public URL. If the user uploads a local image file,
        we upload it to a temporary file sharing host to get a public URL.
        """
        # Try uploading to tmpfiles.org
        try:
            url = "https://tmpfiles.org/api/v1/upload"
            with open(image_path, "rb") as fh:
                files = {"file": ("instagram_upload.jpg", fh, "image/jpeg")}
                resp = requests.post(url, files=files, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    raw_url = data["data"]["url"]
                    # Convert tmpfiles URL to direct download URL (adds /dl/)
                    return raw_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
        except Exception:
            pass

        # Try file.io as a fallback
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

    # ── Public Entry Point ────────────────────────────────────────────────────

    def publish(self, payload: PostPayload) -> PostResult:
        """
        Public entry point called to run the Instagram post logic.
        """
        image_url = payload.image_url

        # If we only have a local image file path, we need to upload it to a public URL first
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
            # 1. Create the media container
            container_id, err = self._create_container(image_url, payload.caption)
            if not container_id:
                return PostResult(
                    platform=self.name, success=False, error=f"Failed to create media container: {err}"
                )

            # 2. Wait for Instagram to finish processing the image
            ready = self._wait_for_container(container_id)
            if not ready:
                return PostResult(
                    platform=self.name, success=False, error="Container processing timed out or errored."
                )

            # 3. Publish the container
            result = self._publish_container(container_id)

            if "id" in result:
                media_id = result["id"]
                
                # Fetch the correct live permalink from Instagram Graph API
                # By querying the media ID directly, we get the exact post link.
                live_url = None
                try:
                    resp_permalink = requests.get(
                        f"{GRAPH_API}/{media_id}",
                        params={
                            "fields": "permalink",
                            "access_token": self._cfg.access_token,
                        },
                        timeout=15,
                    )
                    if resp_permalink.status_code == 200:
                        live_url = resp_permalink.json().get("permalink")
                except Exception:
                    pass

                # If retrieving the permalink failed, fallback to a search/generic link
                if not live_url:
                    live_url = f"https://www.instagram.com/"

                return PostResult(
                    platform=self.name,
                    success=True,
                    post_id=media_id,
                    url=live_url,
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
