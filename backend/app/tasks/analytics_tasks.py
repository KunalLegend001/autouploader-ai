"""
Analytics Sync Tasks — Fetch performance data from all platforms
"""

import asyncio
import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.analytics_tasks.sync_all_analytics")
def sync_all_analytics():
    """Hourly task: Fetch analytics for all published posts."""
    from app.database import AsyncSessionLocal
    from app.models import Post, PostAnalytics, PostStatusEnum, PlatformEnum
    from app.services.youtube_analytics import YouTubeAnalyticsService
    from app.services.meta_analytics import MetaAnalyticsService
    from app.services.tiktok_analytics import TikTokAnalyticsService
    from sqlalchemy import select
    from datetime import datetime

    async def _sync():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Post).where(Post.status == PostStatusEnum.PUBLISHED)
            )
            posts = result.scalars().all()

            for post in posts:
                try:
                    if post.platform == PlatformEnum.YOUTUBE_SHORTS:
                        svc = YouTubeAnalyticsService()
                        stats = await svc.get_video_stats(post.external_post_id)
                    elif post.platform in (PlatformEnum.INSTAGRAM_REELS, PlatformEnum.FACEBOOK_REELS):
                        svc = MetaAnalyticsService()
                        stats = await svc.get_media_stats(post.external_post_id)
                    elif post.platform == PlatformEnum.TIKTOK:
                        svc = TikTokAnalyticsService()
                        stats = await svc.get_video_stats(post.external_post_id)
                    else:
                        continue

                    record = PostAnalytics(
                        post_id=post.id,
                        platform=post.platform,
                        views=stats.get("views", 0),
                        likes=stats.get("likes", 0),
                        comments=stats.get("comments", 0),
                        shares=stats.get("shares", 0),
                        watch_time_seconds=stats.get("watch_time_seconds", 0),
                        followers_gained=stats.get("followers_gained", 0),
                        engagement_rate=stats.get("engagement_rate", 0.0),
                        recorded_at=datetime.utcnow(),
                    )
                    db.add(record)

                except Exception as e:
                    logger.error(f"❌ Analytics sync failed for post {post.id}: {e}")

            await db.commit()
            logger.info(f"✅ Analytics synced for {len(posts)} posts")

    run_async(_sync())
