"""
TikTok Analytics Service
"""
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class TikTokAnalyticsService:
    async def get_video_stats(self, video_id: str, access_token: str = None) -> dict:
        """Fetch video stats from TikTok Research API v2."""
        token = access_token
        if not token:
            return {}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    "https://open.tiktokapis.com/v2/video/query/",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "filters": {"video_ids": [video_id]},
                        "fields": ["view_count", "like_count", "comment_count", "share_count"],
                    },
                )
                res.raise_for_status()
                videos = res.json().get("data", {}).get("videos", [])
                if not videos:
                    return {}
                v = videos[0]
                views = v.get("view_count", 0)
                likes = v.get("like_count", 0)
                comments = v.get("comment_count", 0)
                shares = v.get("share_count", 0)
                engagement = round((likes + comments + shares) / max(views, 1), 4)
                return {
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "watch_time_seconds": 0,
                    "engagement_rate": engagement,
                }
        except Exception as e:
            logger.error(f"TikTok analytics error: {e}")
            return {}
