"""
platforms/facebook.py
──────────────────────
Posts a photo + caption to a Facebook Page via the Graph API.

Docs: https://developers.facebook.com/docs/graph-api/reference/page/photos/
Endpoint: POST /{page-id}/photos
"""

import requests
from pathlib import Path

from config import FacebookConfig
from platforms.base import BasePlatform, PostPayload, PostResult

GRAPH_API = "https://graph.facebook.com/v19.0"


class FacebookPlatform(BasePlatform):

    def __init__(self, cfg: FacebookConfig) -> None:
        self._cfg = cfg

    @property
    def name(self) -> str:
        return "Facebook"

    def publish(self, payload: PostPayload) -> PostResult:
        """
        Uploads photo to the Page's photo album with the caption.
        Supports both local file path and public URL.
        """
        url = f"{GRAPH_API}/{self._cfg.page_id}/photos"
        params = {"access_token": self._cfg.access_token}
        data = {"caption": payload.caption}

        try:
            if payload.image_path and Path(payload.image_path).exists():
                # Upload local file as multipart
                with open(payload.image_path, "rb") as fh:
                    resp = requests.post(
                        url,
                        params=params,
                        data=data,
                        files={"source": (Path(payload.image_path).name, fh, "image/jpeg")},
                        timeout=30,
                    )
            elif payload.image_url:
                # Reference a publicly accessible image URL
                resp = requests.post(
                    url,
                    params=params,
                    data={**data, "url": payload.image_url},
                    timeout=30,
                )
            else:
                # Text-only post via /feed
                resp = requests.post(
                    f"{GRAPH_API}/{self._cfg.page_id}/feed",
                    params=params,
                    data={"message": payload.caption},
                    timeout=30,
                )

            result = resp.json()

            if "id" in result:
                post_id = result["id"]
                return PostResult(
                    platform=self.name,
                    success=True,
                    post_id=post_id,
                    url=f"https://www.facebook.com/{post_id.replace('_', '/posts/')}",
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
