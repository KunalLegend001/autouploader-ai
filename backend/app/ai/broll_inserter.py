"""
B-Roll Inserter — Fetches and inserts stock footage at keyword moments
"""

import asyncio
import logging
import httpx
import os
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)


class BRollInserter:

    async def insert_broll(
        self,
        video_path: str,
        output_path: str,
        keywords: list[str],
        max_broll_clips: int = 2,
    ):
        """
        Fetch B-roll from Pexels and insert at strategic moments.
        """
        if not keywords:
            logger.warning("⚠️ No keywords for B-roll, copying as-is")
            await self._copy_file(video_path, output_path)
            return

        logger.info(f"🎬 Fetching B-roll for keywords: {keywords}")

        # Get video duration
        duration = await self._get_video_duration(video_path)

        # Fetch stock clips
        broll_paths = []
        for kw in keywords[:max_broll_clips]:
            clip_path = await self._fetch_pexels_clip(kw)
            if clip_path:
                broll_paths.append(clip_path)

        if not broll_paths:
            logger.warning("⚠️ No B-roll clips found, copying original")
            await self._copy_file(video_path, output_path)
            return

        # Build ffmpeg concat list
        concat_list = []
        broll_duration = 3.0  # seconds per B-roll clip
        insert_times = self._calculate_insert_times(duration, len(broll_paths))

        # We'll use a simple overlapping strategy: picture-in-picture or full replace
        # For simplicity, use PiP (picture-in-picture) in corner
        await self._apply_pip_broll(
            main_video=video_path,
            broll_clips=broll_paths,
            insert_times=insert_times,
            output_path=output_path,
            broll_duration=broll_duration,
        )

        # Cleanup temp B-roll files
        for p in broll_paths:
            try:
                os.unlink(p)
            except Exception:
                pass

        logger.info(f"✅ B-roll inserted: {output_path}")

    async def _fetch_pexels_clip(self, keyword: str) -> str | None:
        """Fetch a stock video from Pexels API."""
        if not settings.PEXELS_API_KEY:
            logger.warning("⚠️ No PEXELS_API_KEY configured")
            return None

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.pexels.com/videos/search",
                    headers={"Authorization": settings.PEXELS_API_KEY},
                    params={
                        "query": keyword,
                        "per_page": 5,
                        "size": "medium",
                        "orientation": "portrait",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("videos"):
                    return None

                # Pick first video with a suitable file
                for video in data["videos"]:
                    for vf in video.get("video_files", []):
                        if vf.get("quality") in ("hd", "sd") and "mp4" in vf.get("file_type", ""):
                            url = vf["link"]
                            # Download clip
                            dl = await client.get(url, follow_redirects=True)
                            tmp_path = f"{settings.TEMP_DIR}/broll_{keyword.replace(' ', '_')}.mp4"
                            with open(tmp_path, "wb") as f:
                                f.write(dl.content)
                            logger.info(f"✅ Downloaded B-roll for '{keyword}'")
                            return tmp_path

        except Exception as e:
            logger.error(f"❌ Pexels fetch failed for '{keyword}': {e}")
            return None

    async def _apply_pip_broll(
        self,
        main_video: str,
        broll_clips: list[str],
        insert_times: list[float],
        output_path: str,
        broll_duration: float = 3.0,
    ):
        """Apply picture-in-picture B-roll overlay using FFmpeg."""
        # Build complex filtergraph for PiP
        inputs = ["-i", main_video]
        filter_parts = []

        for i, (broll, ts) in enumerate(zip(broll_clips, insert_times)):
            inputs += ["-i", broll]
            filter_parts.append(
                f"[{i+1}:v]scale=320:568,setpts=PTS-STARTPTS+{ts}/TB[pip{i}];"
            )

        # Overlay each PiP
        current = "[0:v]"
        for i in range(len(broll_clips)):
            ts = insert_times[i]
            end_ts = ts + broll_duration
            next_label = f"[ovl{i}]"
            filter_parts.append(
                f"{current}[pip{i}]overlay=W-w-20:H-h-20:enable='between(t,{ts},{end_ts})'{next_label};"
            )
            current = next_label

        filter_complex = "".join(filter_parts).rstrip(";")
        last_label = f"[ovl{len(broll_clips)-1}]" if broll_clips else "[0:v]"

        cmd = [
            settings.FFMPEG_PATH,
            *inputs,
            "-filter_complex", filter_complex,
            "-map", last_label,
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-y",
            output_path,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"FFmpeg PiP failed: {stderr.decode()[-500:]}")
            # Fallback: just copy original
            await self._copy_file(main_video, output_path)

    def _calculate_insert_times(self, total_duration: float, num_clips: int) -> list[float]:
        """Calculate evenly spaced insert times, avoiding start/end."""
        if num_clips == 0:
            return []
        step = total_duration / (num_clips + 1)
        return [step * (i + 1) for i in range(num_clips)]

    async def _get_video_duration(self, video_path: str) -> float:
        """Get video duration via ffprobe."""
        cmd = [
            settings.FFPROBE_PATH,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        import json
        data = json.loads(stdout)
        return float(data["format"]["duration"])

    async def _copy_file(self, src: str, dst: str):
        """Simple file copy."""
        import shutil
        shutil.copy2(src, dst)
