"""
Video Formatter — FFmpeg operations: cut, vertical format, thumbnail
"""

import asyncio
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class VideoFormatter:

    async def cut_clip(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float,
    ):
        """Cut a clip from a video using FFmpeg."""
        duration = end_time - start_time
        cmd = [
            settings.FFMPEG_PATH,
            "-ss", str(start_time),
            "-i", input_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-crf", "20",
            "-avoid_negative_ts", "make_zero",
            "-y",
            output_path,
        ]
        await self._run(cmd, f"cut clip {start_time:.1f}s–{end_time:.1f}s")
        logger.info(f"✅ Clip cut: {duration:.1f}s → {output_path}")

    async def to_vertical(self, input_path: str, output_path: str):
        """
        Convert video to 9:16 vertical format (1080x1920) for TikTok/Reels/Shorts.
        Uses smart crop + blur background: maintains content, fills with blurred bg.
        """
        # Advanced: blur pad technique — content stays visible, bg is blurred fill
        filter_complex = (
            "[0:v]split[blur][main];"
            "[blur]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=20:20[blurbg];"
            "[main]scale=-2:1920[scaled];"
            "[blurbg][scaled]overlay=(W-w)/2:(H-h)/2[v]"
        )
        cmd = [
            settings.FFMPEG_PATH,
            "-i", input_path,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-crf", "20",
            "-s", "1080x1920",
            "-y",
            output_path,
        ]
        await self._run(cmd, "vertical conversion")
        logger.info(f"✅ Converted to vertical: {output_path}")

    async def extract_thumbnail(
        self,
        video_path: str,
        output_path: str,
        time: float = 1.0,
    ):
        """Extract a JPEG thumbnail at the given time."""
        cmd = [
            settings.FFMPEG_PATH,
            "-ss", str(time),
            "-i", video_path,
            "-vframes", "1",
            "-f", "image2",
            "-q:v", "2",
            "-y",
            output_path,
        ]
        await self._run(cmd, "thumbnail extraction")

    async def add_watermark(
        self,
        video_path: str,
        output_path: str,
        watermark_path: str,
        position: str = "bottom_right",
    ):
        """Add a logo watermark overlay."""
        positions = {
            "bottom_right": "W-w-10:H-h-10",
            "bottom_left": "10:H-h-10",
            "top_right": "W-w-10:10",
            "top_left": "10:10",
        }
        pos = positions.get(position, "W-w-10:H-h-10")
        cmd = [
            settings.FFMPEG_PATH,
            "-i", video_path,
            "-i", watermark_path,
            "-filter_complex", f"[1:v]scale=80:-1[wm];[0:v][wm]overlay={pos}",
            "-c:a", "copy",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-y",
            output_path,
        ]
        await self._run(cmd, "watermark")

    async def _run(self, cmd: list, operation: str):
        """Run an FFmpeg command asynchronously."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                f"FFmpeg {operation} failed (code {process.returncode}): {stderr.decode()[-1000:]}"
            )
