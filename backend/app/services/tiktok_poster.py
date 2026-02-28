"""
TikTok Video Uploader
"""

import logging
import httpx
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)


class TikTokPoster:

    def __init__(self, access_token: str = None):
        self.access_token = access_token
        self.api_base = "https://open.tiktokapis.com/v2"

    async def upload(
        self,
        video_url: str,
        title: str,
        hashtags: list[str] = None,
        privacy: str = "PUBLIC_TO_EVERYONE",
    ) -> tuple[str, str]:
        """
        Upload a video to TikTok via URL upload (Content Posting API v2).
        Returns (video_id, video_url).
        """
        if not self.access_token:
            raise ValueError("TikTok access token not configured")

        caption = title
        if hashtags:
            caption += " " + " ".join(hashtags[:20])

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Initialize upload
            init_resp = await client.post(
                f"{self.api_base}/post/publish/video/init/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                json={
                    "post_info": {
                        "title": caption[:2200],
                        "privacy_level": privacy,
                        "disable_duet": False,
                        "disable_comment": False,
                        "disable_stitch": False,
                    },
                    "source_info": {
                        "source": "PULL_FROM_URL",
                        "video_url": video_url,
                    },
                },
            )
            init_resp.raise_for_status()
            data = init_resp.json()["data"]
            publish_id = data["publish_id"]

            logger.info(f"📤 TikTok publish_id: {publish_id}, polling for result...")

            # Poll for completion
            for _ in range(20):
                await asyncio.sleep(5)
                status_resp = await client.post(
                    f"{self.api_base}/post/publish/status/fetch/",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={"publish_id": publish_id},
                )
                status_resp.raise_for_status()
                status_data = status_resp.json()["data"]
                status = status_data.get("status")
                logger.info(f"TikTok status: {status}")
                if status == "PUBLISH_COMPLETE":
                    video_id = status_data.get("video_id", publish_id)
                    url = f"https://www.tiktok.com/@me/video/{video_id}"
                    logger.info(f"✅ TikTok posted: {url}")
                    return video_id, url
                elif status in ("FAILED", "CANCELLED"):
                    raise RuntimeError(f"TikTok upload failed: {status_data}")

            raise TimeoutError("TikTok upload timed out after 100 seconds")
