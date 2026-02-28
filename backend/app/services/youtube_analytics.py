"""
YouTube Analytics Service
"""
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class YouTubeAnalyticsService:
    async def get_video_stats(self, video_id: str, access_token: str = None) -> dict:
        """Fetch video stats from YouTube Data API v3."""
        if not settings.YOUTUBE_API_KEY and not access_token:
            return {}

        params = {
            "part": "statistics",
            "id": video_id,
            "key": settings.YOUTUBE_API_KEY,
        }
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(
                    "https://www.googleapis.com/youtube/v3/videos",
                    params=params, headers=headers,
                )
                res.raise_for_status()
                items = res.json().get("items", [])
                if not items:
                    return {}
                stats = items[0].get("statistics", {})
                return {
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "shares": 0,
                    "watch_time_seconds": 0,
                    "engagement_rate": 0.0,
                }
        except Exception as e:
            logger.error(f"YouTube analytics error: {e}")
            return {}
