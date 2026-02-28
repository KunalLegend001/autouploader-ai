"""
Auto-Posting Tasks — Upload clips to all platforms
"""

import asyncio
import logging
from uuid import UUID
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    name="app.tasks.posting_tasks.upload_to_platform",
)
def upload_to_platform(self, post_id: str):
    """Upload a clip to a social media platform."""
    from app.database import AsyncSessionLocal
    from app.models import Post, Clip, PostStatusEnum, PlatformEnum
    from app.services.youtube_poster import YouTubeShortsPoster
    from app.services.meta_poster import MetaPoster
    from app.services.tiktok_poster import TikTokPoster
    from sqlalchemy import select
    from datetime import datetime

    async def _upload():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Post).where(Post.id == UUID(post_id)))
            post = result.scalar_one_or_none()
            if not post:
                logger.error(f"Post {post_id} not found")
                return

            clip_result = await db.execute(select(Clip).where(Clip.id == post.clip_id))
            clip = clip_result.scalar_one_or_none()
            if not clip or not clip.s3_url:
                logger.error(f"Clip not ready for post {post_id}")
                return

            post.status = PostStatusEnum.UPLOADING
            await db.commit()

            try:
                platform = post.platform
                video_url = clip.s3_url
                title = post.title or clip.title or "Check this out!"
                description = post.description or clip.description or ""
                hashtags = post.hashtags or []

                if platform == PlatformEnum.YOUTUBE_SHORTS:
                    poster = YouTubeShortsPoster()
                    ext_id, url = await poster.upload(
                        video_url=video_url,
                        title=title,
                        description=description,
                        tags=hashtags,
                    )
                elif platform in (PlatformEnum.INSTAGRAM_REELS, PlatformEnum.FACEBOOK_REELS):
                    poster = MetaPoster(platform=platform)
                    ext_id, url = await poster.upload(
                        video_url=video_url,
                        caption=f"{description}\n\n{' '.join(hashtags)}",
                    )
                elif platform == PlatformEnum.TIKTOK:
                    poster = TikTokPoster()
                    ext_id, url = await poster.upload(
                        video_url=video_url,
                        title=title,
                        hashtags=hashtags,
                    )
                else:
                    raise ValueError(f"Unknown platform: {platform}")

                post.status = PostStatusEnum.PUBLISHED
                post.external_post_id = ext_id
                post.post_url = url
                post.published_at = datetime.utcnow()
                await db.commit()
                logger.info(f"✅ Posted to {platform}: {url}")

            except Exception as e:
                post.status = PostStatusEnum.FAILED
                post.error_message = str(e)
                await db.commit()
                raise

    run_async(_upload())
