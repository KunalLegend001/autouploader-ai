"""
YouTube Shorts Auto-Poster
"""

import logging
import httpx
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import asyncio
import tempfile
import os
from app.config import settings

logger = logging.getLogger(__name__)


class YouTubeShortsPoster:

    async def upload(
        self,
        video_url: str,
        title: str,
        description: str,
        tags: list[str] = None,
        access_token: str = None,
    ) -> tuple[str, str]:
        """
        Upload a video as a YouTube Short.
        Returns (video_id, video_url).
        """
        if not access_token and not settings.YOUTUBE_CLIENT_ID:
            raise ValueError("YouTube credentials not configured")

        # Download video to temp file (needed for YouTube API multipart upload)
        local_path = await self._download_temp(video_url)

        try:
            creds = Credentials(token=access_token) if access_token else None
            loop = asyncio.get_event_loop()
            video_id = await loop.run_in_executor(
                None,
                self._upload_sync,
                local_path,
                title,
                description,
                tags or [],
                creds,
            )
            url = f"https://youtube.com/shorts/{video_id}"
            logger.info(f"✅ YouTube Short uploaded: {url}")
            return video_id, url
        finally:
            try:
                os.unlink(local_path)
            except Exception:
                pass

    def _upload_sync(
        self,
        local_path: str,
        title: str,
        description: str,
        tags: list,
        creds,
    ) -> str:
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:500],
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        media = MediaFileUpload(local_path, mimetype="video/mp4", resumable=True, chunksize=1024 * 1024 * 10)
        request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"📤 YouTube upload: {int(status.progress() * 100)}%")
        return response["id"]

    async def _download_temp(self, url: str) -> str:
        if url.startswith("file://"):
            return url[7:]
        tmp = tempfile.mktemp(suffix=".mp4")
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream("GET", url) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    async for chunk in r.aiter_bytes(1024 * 1024):
                        f.write(chunk)
        return tmp
