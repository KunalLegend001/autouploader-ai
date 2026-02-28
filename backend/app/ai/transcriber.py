"""
Video Transcriber — Whisper API
"""

import logging
import asyncio
from pathlib import Path
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class VideoTranscriber:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, video_path: str) -> dict:
        """
        Transcribe video audio using OpenAI Whisper.
        Returns dict with 'text' and 'segments' (with timestamps).
        """
        logger.info(f"🎤 Transcribing: {video_path}")

        # First extract audio for efficiency
        audio_path = video_path.replace(".mp4", "_audio.wav")
        await self._extract_audio(video_path, audio_path)

        try:
            with open(audio_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=settings.WHISPER_MODEL,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment", "word"],
                )

            result = {
                "text": response.text,
                "language": response.language,
                "duration": response.duration,
                "segments": [
                    {
                        "id": seg.id,
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text.strip(),
                    }
                    for seg in (response.segments or [])
                ],
                "words": [
                    {
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                    }
                    for w in (response.words or [])
                ] if hasattr(response, "words") else [],
            }
            logger.info(f"✅ Transcription complete: {len(result['segments'])} segments, {response.duration:.1f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise
        finally:
            # Cleanup audio file
            try:
                Path(audio_path).unlink(missing_ok=True)
            except Exception:
                pass

    async def _extract_audio(self, video_path: str, audio_path: str):
        """Extract audio from video using FFmpeg."""
        cmd = [
            settings.FFMPEG_PATH,
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            audio_path,
        ]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed: {stderr.decode()}")
        logger.info(f"✅ Audio extracted to: {audio_path}")
