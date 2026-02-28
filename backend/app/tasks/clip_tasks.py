"""
Celery Tasks — Clip Generation
"""

import asyncio
import logging
from uuid import UUID
from app.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)


def run_async(coro):
    """Run an async function in sync Celery context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.clip_tasks.generate_clips",
)
def generate_clips(
    self,
    source_video_id: str,
    user_id: str,
    video_path: str,
    num_clips: int = 5,
    min_duration: int = 20,
    max_duration: int = 60,
    add_captions: bool = True,
    add_broll: bool = False,
    vertical_format: bool = True,
    custom_prompt: str = None,
):
    """
    Background task: Run AI pipeline to generate clips from a video.
    Updates clip records in DB when done.
    """
    from app.ai.pipeline import AIAgentPipeline
    from app.database import AsyncSessionLocal
    from app.models import Clip, SourceVideo, ClipStatusEnum, UsageRecord
    from sqlalchemy import select
    from datetime import datetime

    logger.info(f"🎬 Starting clip generation task for video {source_video_id}")

    try:
        pipeline = AIAgentPipeline()
        results = run_async(
            pipeline.run(
                video_path=video_path,
                num_clips=num_clips,
                min_duration=min_duration,
                max_duration=max_duration,
                add_captions=add_captions,
                add_broll=add_broll,
                vertical_format=vertical_format,
                custom_prompt=custom_prompt,
                user_id=user_id,
            )
        )

        # Save clips to database
        async def save_clips():
            async with AsyncSessionLocal() as db:
                for result in results:
                    if "error" in result:
                        continue
                    clip = Clip(
                        user_id=UUID(user_id),
                        source_video_id=UUID(source_video_id),
                        title=result.get("title"),
                        description=result.get("description"),
                        start_time=result.get("start_time"),
                        end_time=result.get("end_time"),
                        duration=result.get("duration"),
                        viral_score=result.get("viral_score", 75.0),
                        status=ClipStatusEnum.READY,
                        local_path=result.get("local_path"),
                        s3_url=result.get("s3_url"),
                        thumbnail_url=result.get("thumbnail_url"),
                        has_captions=result.get("has_captions", False),
                        has_broll=result.get("has_broll", False),
                        is_vertical=result.get("is_vertical", False),
                        ai_tags=result.get("keywords", []),
                    )
                    db.add(clip)

                # Update usage
                month = datetime.utcnow().strftime("%Y-%m")
                usage_result = await db.execute(
                    select(UsageRecord).where(
                        UsageRecord.user_id == UUID(user_id),
                        UsageRecord.month == month,
                    )
                )
                usage = usage_result.scalar_one_or_none()
                if usage:
                    usage.clips_generated += len([r for r in results if "error" not in r])
                else:
                    db.add(UsageRecord(
                        user_id=UUID(user_id),
                        month=month,
                        clips_generated=len([r for r in results if "error" not in r]),
                    ))

                # Mark source video as processed
                sv_result = await db.execute(select(SourceVideo).where(SourceVideo.id == UUID(source_video_id)))
                sv = sv_result.scalar_one_or_none()
                if sv:
                    sv.processed = True

                await db.commit()
                logger.info(f"✅ Saved {len(results)} clips to DB")

        run_async(save_clips())
        return {"status": "success", "clips": len(results)}

    except Exception as exc:
        logger.error(f"❌ Clip generation failed: {exc}")
        self.retry(exc=exc)


@celery_app.task(name="app.tasks.clip_tasks.check_new_videos")
def check_new_videos():
    """
    Scheduled task: Check connected channels for new videos.
    """
    from app.services.youtube_downloader import YouTubeDownloader
    from app.database import AsyncSessionLocal
    from app.models import Channel, SourceVideo, ChannelPlatformEnum
    from sqlalchemy import select

    logger.info("🔍 Checking for new videos...")
    downloader = YouTubeDownloader()

    async def _check():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Channel).where(
                    Channel.is_active == True,
                    Channel.platform == ChannelPlatformEnum.YOUTUBE,
                )
            )
            channels = result.scalars().all()

            for channel in channels:
                try:
                    videos = await downloader.get_channel_videos(
                        channel_id=channel.external_channel_id,
                        access_token=channel.access_token,
                        max_results=5,
                    )
                    for video in videos:
                        existing = await db.execute(
                            select(SourceVideo).where(
                                SourceVideo.external_video_id == video["id"]
                            )
                        )
                        if not existing.scalar_one_or_none():
                            sv = SourceVideo(
                                channel_id=channel.id,
                                external_video_id=video["id"],
                                title=video["title"],
                                description=video.get("description"),
                                thumbnail_url=video.get("thumbnail"),
                                duration_seconds=video.get("duration"),
                            )
                            db.add(sv)
                            logger.info(f"📹 New video found: {video['title']}")
                    await db.commit()
                except Exception as e:
                    logger.error(f"❌ Channel check failed for {channel.channel_name}: {e}")

    run_async(_check())
