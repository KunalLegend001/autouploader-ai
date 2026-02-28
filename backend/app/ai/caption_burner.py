"""
Caption Burner — Burns animated captions onto video using FFmpeg
Supports: word-level highlighting, animated pop-up style
"""

import asyncio
import logging
import os
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)


class CaptionBurner:

    async def burn_captions(
        self,
        video_path: str,
        output_path: str,
        segments: list[dict],
        style: str = "modern",  # "modern", "bold", "karaoke"
    ):
        """
        Burn captions into video using FFmpeg.
        Generates an ASS (Advanced SubStation Alpha) subtitle file for rich styling.
        """
        logger.info(f"📝 Burning captions: {style} style, {len(segments)} segments")

        # Build ASS subtitle file
        ass_path = output_path.replace(".mp4", ".ass")
        self._write_ass_file(ass_path, segments, style)

        # FFmpeg command to burn in subtitles
        cmd = [
            settings.FFMPEG_PATH,
            "-i", video_path,
            "-vf", f"ass='{ass_path}'",
            "-c:a", "copy",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
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
            raise RuntimeError(f"FFmpeg caption burn failed: {stderr.decode()[-1000:]}")

        # Cleanup ASS file
        try:
            os.unlink(ass_path)
        except Exception:
            pass

        logger.info(f"✅ Captions burned to: {output_path}")

    def _write_ass_file(self, ass_path: str, segments: list[dict], style: str):
        """Generate ASS subtitle file with modern styling."""

        styles = {
            "modern": {
                "Fontname": "Arial",
                "Fontsize": "20",
                "PrimaryColour": "&H00FFFFFF",
                "OutlineColour": "&H00000000",
                "Outline": "2",
                "Bold": "-1",
                "Alignment": "2",  # Bottom center
                "MarginV": "60",
                "BorderStyle": "1",
            },
            "bold": {
                "Fontname": "Impact",
                "Fontsize": "24",
                "PrimaryColour": "&H00FFFF00",  # Yellow
                "OutlineColour": "&H00000000",
                "Outline": "3",
                "Bold": "-1",
                "Alignment": "2",
                "MarginV": "50",
                "BorderStyle": "1",
            },
            "karaoke": {
                "Fontname": "Arial Black",
                "Fontsize": "22",
                "PrimaryColour": "&H00FFFFFF",
                "SecondaryColour": "&H0000FFFF",  # Cyan highlight
                "OutlineColour": "&H00000000",
                "Outline": "2",
                "Bold": "-1",
                "Alignment": "2",
                "MarginV": "55",
                "BorderStyle": "1",
            },
        }

        s = styles.get(style, styles["modern"])

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{s['Fontname']},{s['Fontsize']},{s['PrimaryColour']},&H000000FF,{s['OutlineColour']},&H00000000,{s.get('Bold', '0')},0,0,0,100,100,0,0,{s.get('BorderStyle', '1')},{s.get('Outline', '2')},0,{s.get('Alignment', '2')},10,10,{s.get('MarginV', '60')},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        for seg in segments:
            start = self._seconds_to_ass_time(seg["start"])
            end = self._seconds_to_ass_time(seg["end"])
            text = seg["text"].strip().replace("\n", "\\N")
            # Word wrap: split long lines
            if len(text) > 40:
                words = text.split()
                mid = len(words) // 2
                text = " ".join(words[:mid]) + "\\N" + " ".join(words[mid:])
            events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")

    @staticmethod
    def _seconds_to_ass_time(seconds: float) -> str:
        """Convert seconds to ASS time format H:MM:SS.cc"""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        cs = int((s % 1) * 100)
        return f"{h}:{m:02d}:{int(s):02d}.{cs:02d}"
