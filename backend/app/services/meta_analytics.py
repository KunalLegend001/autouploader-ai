"""
Meta (Instagram + Facebook) Analytics Service
"""
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class MetaAnalyticsService:
    async def get_media_stats(self, media_id: str, access_token: str = None) -> dict:
        """Fetch media insights from Meta Graph API."""
        token = access_token or settings.META_APP_SECRET
        if not token:
            return {}

        metrics = "reach,impressions,likes,comments,shares,saved"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(
                    f"https://graph.facebook.com/{settings.META_GRAPH_API_VERSION}/{media_id}/insights",
                    params={"metric": metrics, "access_token": token},
                )
                res.raise_for_status()
                data = res.json().get("data", [])
                stats: dict = {}
                for item in data:
                    stats[item["name"]] = item.get("values", [{}])[-1].get("value", 0)
                return {
                    "views": stats.get("reach", 0),
                    "likes": stats.get("likes", 0),
                    "comments": stats.get("comments", 0),
                    "shares": stats.get("shares", 0),
                    "watch_time_seconds": 0,
                    "engagement_rate": 0.0,
                }
        except Exception as e:
            logger.error(f"Meta analytics error: {e}")
            return {}
