"""
AI Agent Pipeline — Core Brain
Orchestrates: download → transcribe → AI select → clip → caption → broll → vertical
"""

import os
import json
import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Optional
from uuid import UUID

from app.config import settings
from app.ai.transcriber import VideoTranscriber
from app.ai.clip_selector import ClipSelector
from app.ai.caption_burner import CaptionBurner
from app.ai.broll_inserter import BRollInserter
from app.ai.video_formatter import VideoFormatter
from app.storage.s3_uploader import S3Uploader
from app.services.youtube_downloader import YouTubeDownloader

logger = logging.getLogger(__name__)


class AIAgentPipeline:
    """
    Full AI pipeline:
    1. Download video (if URL provided)
    2. Transcribe audio → Whisper
    3. AI selects best viral moments → GPT-4
    4. FFmpeg cuts clips
    5. Burn captions → FFmpeg
    6. Insert B-roll → FFmpeg
    7. Convert to vertical 9:16 → FFmpeg
    8. Upload to S3
    """

    def __init__(self):
        self.downloader = YouTubeDownloader()
        self.transcriber = VideoTranscriber()
        self.selector = ClipSelector()
        self.caption_burner = CaptionBurner()
        self.broll_inserter = BRollInserter()
        self.formatter = VideoFormatter()
        self.uploader = S3Uploader()

    async def run(
        self,
        video_path: str,
        num_clips: int = 5,
        min_duration: int = 20,
        max_duration: int = 60,
        add_captions: bool = True,
        add_broll: bool = False,
        vertical_format: bool = True,
        custom_prompt: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Run the full pipeline on a local video file.
        Returns list of clip result dicts with s3_url, metadata, etc.
        """
        logger.info(f"🎬 Starting AI pipeline on: {video_path}")
        results = []

        # Step 1: Transcribe
        logger.info("📝 Step 1: Transcribing video...")
        transcription = await self.transcriber.transcribe(video_path)
        if not transcription:
            raise ValueError("Transcription failed — no speech detected")

        # Step 2: AI selects best moments
        logger.info(f"🤖 Step 2: AI selecting {num_clips} best moments...")
        segments = await self.selector.select_viral_moments(
            transcript=transcription["text"],
            timed_segments=transcription["segments"],
            num_clips=num_clips,
            min_duration=min_duration,
            max_duration=max_duration,
            custom_prompt=custom_prompt,
        )
        logger.info(f"✅ Found {len(segments)} segments")

        # Step 3: Process each segment
        for i, seg in enumerate(segments):
            try:
                logger.info(f"✂️ Processing clip {i+1}/{len(segments)}: {seg['start']:.1f}s → {seg['end']:.1f}s")
                clip_result = await self._process_segment(
                    video_path=video_path,
                    segment=seg,
                    clip_index=i,
                    transcription=transcription,
                    add_captions=add_captions,
                    add_broll=add_broll,
                    vertical_format=vertical_format,
                    user_id=user_id,
                )
                results.append(clip_result)
            except Exception as e:
                logger.error(f"❌ Clip {i+1} failed: {e}")
                results.append({"error": str(e), "segment": seg})
                continue

        logger.info(f"🎉 Pipeline complete! {len([r for r in results if 'error' not in r])} clips ready.")
        return results

    async def _process_segment(
        self,
        video_path: str,
        segment: dict,
        clip_index: int,
        transcription: dict,
        add_captions: bool,
        add_broll: bool,
        vertical_format: bool,
        user_id: Optional[str],
    ) -> dict:
        work_dir = Path(settings.CLIPS_OUTPUT_DIR) / (user_id or "guest")
        work_dir.mkdir(parents=True, exist_ok=True)

        clip_id = f"clip_{clip_index:03d}"
        raw_clip = str(work_dir / f"{clip_id}_raw.mp4")

        # Step A: Cut raw clip
        await self.formatter.cut_clip(
            input_path=video_path,
            output_path=raw_clip,
            start_time=segment["start"],
            end_time=segment["end"],
        )

        current_file = raw_clip

        # Step B: Convert to vertical (do this before captions for better results)
        if vertical_format:
            vertical_path = str(work_dir / f"{clip_id}_vertical.mp4")
            await self.formatter.to_vertical(current_file, vertical_path)
            current_file = vertical_path

        # Step C: Add B-roll if requested
        if add_broll:
            broll_path = str(work_dir / f"{clip_id}_broll.mp4")
            keywords = segment.get("keywords", [])
            await self.broll_inserter.insert_broll(
                video_path=current_file,
                output_path=broll_path,
                keywords=keywords,
            )
            current_file = broll_path

        # Step D: Burn captions
        if add_captions:
            captioned_path = str(work_dir / f"{clip_id}_captioned.mp4")
            # Extract relevant transcript segments for this clip
            relevant_segments = [
                s for s in transcription["segments"]
                if s["end"] >= segment["start"] and s["start"] <= segment["end"]
            ]
            # Offset timestamps to clip start
            offset_segments = [
                {**s, "start": max(0, s["start"] - segment["start"]),
                 "end": min(segment["end"] - segment["start"], s["end"] - segment["start"])}
                for s in relevant_segments
            ]
            await self.caption_burner.burn_captions(
                video_path=current_file,
                output_path=captioned_path,
                segments=offset_segments,
            )
            current_file = captioned_path

        # Step E: Upload to S3
        final_key = f"clips/{user_id or 'guest'}/{clip_id}_final.mp4"
        s3_url = await self.uploader.upload_file(current_file, final_key)

        # Thumbnail
        thumbnail_path = str(work_dir / f"{clip_id}_thumb.jpg")
        await self.formatter.extract_thumbnail(current_file, thumbnail_path, time=1.0)
        thumb_key = f"thumbnails/{user_id or 'guest'}/{clip_id}.jpg"
        thumb_url = await self.uploader.upload_file(thumbnail_path, thumb_key)

        return {
            "title": segment.get("title", f"Clip {clip_index + 1}"),
            "description": segment.get("reason", ""),
            "start_time": segment["start"],
            "end_time": segment["end"],
            "duration": segment["end"] - segment["start"],
            "viral_score": segment.get("viral_score", 75.0),
            "keywords": segment.get("keywords", []),
            "s3_url": s3_url,
            "thumbnail_url": thumb_url,
            "local_path": current_file,
            "has_captions": add_captions,
            "has_broll": add_broll,
            "is_vertical": vertical_format,
        }
