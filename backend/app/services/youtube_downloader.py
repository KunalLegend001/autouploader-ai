"""
YouTube Downloader Service — yt-dlp based
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional
import yt_dlp
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class YouTubeDownloader:

    def __init__(self):
        self.output_dir = settings.TEMP_DIR

    async def download_video(
        self,
        url: str,
        output_path: Optional[str] = None,
        max_height: int = 1080,
    ) -> str:
        """
        Download a YouTube video using yt-dlp.
        Returns local file path.
        """
        if not output_path:
            video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else "video"
            output_path = os.path.join(self.output_dir, f"{video_id}.mp4")

        ydl_opts = {
            "outtmpl": output_path,
            "format": f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={max_height}][ext=mp4]/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }
            ],
        }

        logger.info(f"⬇️ Downloading: {url}")

        # Run in thread pool to avoid blocking async loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._download_sync, url, ydl_opts)

        if not os.path.exists(output_path):
            # yt-dlp may add extension
            for ext in [".mp4", ".mkv", ".webm"]:
                candidate = output_path.replace(".mp4", ext)
                if os.path.exists(candidate):
                    output_path = candidate
                    break

        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Download completed but file not found: {output_path}")

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"✅ Downloaded: {output_path} ({size_mb:.1f} MB)")
        return output_path

    def _download_sync(self, url: str, opts: dict):
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    async def get_video_info(self, url: str) -> dict:
        """Get metadata without downloading."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, self._get_info_sync, url, ydl_opts)
        return {
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),  # seconds
            "thumbnail": info.get("thumbnail"),
            "channel": info.get("uploader"),
            "upload_date": info.get("upload_date"),
            "view_count": info.get("view_count"),
            "url": url,
        }

    def _get_info_sync(self, url: str, opts: dict) -> dict:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def get_channel_videos(
        self,
        channel_id: str,
        access_token: Optional[str] = None,
        max_results: int = 10,
    ) -> list[dict]:
        """
        Fetch latest videos from a YouTube channel using YouTube Data API v3.
        """
        if not settings.YOUTUBE_API_KEY and not access_token:
            logger.warning("⚠️ No YouTube API key configured")
            return []

        params = {
            "part": "snippet,contentDetails",
            "channelId": channel_id,
            "order": "date",
            "maxResults": max_results,
            "type": "video",
            "key": settings.YOUTUBE_API_KEY,
        }

        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        videos = []
        for item in data.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "id": item["id"]["videoId"],
                "title": snippet["title"],
                "description": snippet.get("description"),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                "published_at": snippet.get("publishedAt"),
            })

        return videos
