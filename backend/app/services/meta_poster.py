"""
Meta (Instagram + Facebook Reels) Auto-Poster
"""

import logging
import httpx
import asyncio
import os
import tempfile
from app.config import settings
from app.models import PlatformEnum

logger = logging.getLogger(__name__)


class MetaPoster:

    def __init__(self, platform: PlatformEnum, access_token: str = None):
        self.platform = platform
        self.access_token = access_token
        self.api_base = f"https://graph.facebook.com/{settings.META_GRAPH_API_VERSION}"

    async def upload(
        self,
        video_url: str,
        caption: str,
        ig_user_id: str = None,
        page_id: str = None,
    ) -> tuple[str, str]:
        """
        Upload to Instagram Reels or Facebook Reels.
        Returns (media_id, post_url).
        """
        if self.platform == PlatformEnum.INSTAGRAM_REELS:
            return await self._upload_instagram_reel(video_url, caption, ig_user_id)
        else:
            return await self._upload_facebook_reel(video_url, caption, page_id)

    async def _upload_instagram_reel(
        self, video_url: str, caption: str, ig_user_id: str
    ) -> tuple[str, str]:
        """
        Instagram Reels upload via Meta Graph API (2-step: create container → publish).
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Create media container
            container_resp = await client.post(
                f"{self.api_base}/{ig_user_id}/media",
                params={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption[:2200],
                    "access_token": self.access_token,
                },
            )
            container_resp.raise_for_status()
            container_id = container_resp.json()["id"]
            logger.info(f"📦 Instagram container created: {container_id}")

            # Step 2: Wait for processing
            await asyncio.sleep(30)

            # Step 3: Publish
            pub_resp = await client.post(
                f"{self.api_base}/{ig_user_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
            )
            pub_resp.raise_for_status()
            media_id = pub_resp.json()["id"]
            url = f"https://www.instagram.com/reel/{media_id}/"
            logger.info(f"✅ Instagram Reel published: {url}")
            return media_id, url

    async def _upload_facebook_reel(
        self, video_url: str, caption: str, page_id: str
    ) -> tuple[str, str]:
        """Facebook Reels upload."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Initialize upload session
            init_resp = await client.post(
                f"{self.api_base}/{page_id}/video_reels",
                params={
                    "upload_phase": "start",
                    "access_token": self.access_token,
                },
            )
            init_resp.raise_for_status()
            video_id = init_resp.json()["video_id"]

            # Finish with video URL
            finish_resp = await client.post(
                f"{self.api_base}/{page_id}/video_reels",
                params={
                    "upload_phase": "finish",
                    "video_id": video_id,
                    "video_state": "PUBLISHED",
                    "description": caption[:63206],
                    "access_token": self.access_token,
                },
                json={"file_url": video_url},
            )
            finish_resp.raise_for_status()
            url = f"https://www.facebook.com/reel/{video_id}"
            logger.info(f"✅ Facebook Reel published: {url}")
            return video_id, url
