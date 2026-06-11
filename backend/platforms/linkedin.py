"""
platforms/linkedin.py
──────────────────────
Posts a photo + caption to LinkedIn via the UGC Posts API.

LinkedIn image posting is a three-step process:
  1. Register an image upload   →  POST /assets?action=registerUpload
  2. Upload the binary image    →  PUT  {uploadUrl}
  3. Create the UGC post        →  POST /ugcPosts

Docs: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
"""

import requests
from pathlib import Path

from config import LinkedInConfig
from platforms.base import BasePlatform, PostPayload, PostResult

LI_API = "https://api.linkedin.com/v2"


class LinkedInPlatform(BasePlatform):

    def __init__(self, cfg: LinkedInConfig) -> None:
        self._cfg = cfg
        self._headers = {
            "Authorization": f"Bearer {self._cfg.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    @property
    def name(self) -> str:
        return "LinkedIn"

    # ── Step 1: Register image upload ─────────────────────────────────────────

    def _register_upload(self) -> tuple[str, str] | tuple[None, None]:
        """Returns (asset_urn, upload_url) or (None, None) on failure."""
        body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self._cfg.author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }
        resp = requests.post(
            f"{LI_API}/assets?action=registerUpload",
            headers=self._headers,
            json=body,
            timeout=30,
        )
        data = resp.json()
        try:
            value = data["value"]
            asset_urn = value["asset"]
            upload_url = value["uploadMechanism"][
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
            ]["uploadUrl"]
            return asset_urn, upload_url
        except (KeyError, TypeError):
            return None, None

    # ── Step 2: Upload the image binary ───────────────────────────────────────

    def _upload_image(self, upload_url: str, image_path: Path) -> bool:
        with open(image_path, "rb") as fh:
            resp = requests.put(
                upload_url,
                data=fh,
                headers={"Authorization": f"Bearer {self._cfg.access_token}"},
                timeout=60,
            )
        return resp.status_code in (200, 201)

    # ── Step 3: Create the UGC post ───────────────────────────────────────────

    def _create_post(self, asset_urn: str, caption: str) -> dict:
        body = {
            "author": self._cfg.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": caption},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": caption[:200]},
                            "media": asset_urn,
                        }
                    ],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        return requests.post(
            f"{LI_API}/ugcPosts",
            headers=self._headers,
            json=body,
            timeout=30,
        ).json()

    # ── Text-only fallback (no image) ─────────────────────────────────────────

    def _create_text_post(self, caption: str) -> dict:
        body = {
            "author": self._cfg.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": caption},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
        return requests.post(
            f"{LI_API}/ugcPosts",
            headers=self._headers,
            json=body,
            timeout=30,
        ).json()

    # ── Public entry point ────────────────────────────────────────────────────

    def publish(self, payload: PostPayload) -> PostResult:
        try:
            if payload.image_path and Path(payload.image_path).exists():
                # Full image upload flow
                asset_urn, upload_url = self._register_upload()
                if not asset_urn:
                    return PostResult(
                        platform=self.name, success=False, error="Failed to register image upload."
                    )

                uploaded = self._upload_image(upload_url, Path(payload.image_path))
                if not uploaded:
                    return PostResult(
                        platform=self.name, success=False, error="Image upload to LinkedIn CDN failed."
                    )

                result = self._create_post(asset_urn, payload.caption)
            else:
                # Text-only or URL-based (LinkedIn doesn't accept external URLs directly)
                result = self._create_text_post(payload.caption)

            post_id = result.get("id")
            if post_id:
                return PostResult(
                    platform=self.name,
                    success=True,
                    post_id=post_id,
                    url=f"https://www.linkedin.com/feed/update/{post_id}/",
                )
            else:
                error = result.get("message", str(result))
                return PostResult(platform=self.name, success=False, error=error)

        except requests.RequestException as exc:
            return PostResult(platform=self.name, success=False, error=str(exc))
