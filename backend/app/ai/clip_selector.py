"""
Clip Selector — GPT-4 finds the most viral moments
"""

import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

VIRAL_MOMENT_PROMPT = """You are an expert viral content strategist who has studied thousands of viral TikTok, Instagram Reels, and YouTube Shorts.

Analyze the following video transcript and identify the {num_clips} most engaging, viral-worthy moments.

For each clip, you must find moments that have:
- A strong hook in the first 3 seconds (controversial, surprising, or curiosity-inducing)
- High emotional resonance (inspiring, funny, surprising, shocking, relatable)
- A clear narrative arc even when extracted from the full video
- Standalone value without needing to watch the full video

Constraints:
- Each clip must be between {min_duration} and {max_duration} seconds
- Clips should NOT overlap
- Select from different parts of the video for variety

{custom_instruction}

TRANSCRIPT:
{transcript}

Return a JSON array of exactly {num_clips} clips with this exact format:
[
  {{
    "title": "Catchy title for this clip (max 60 chars)",
    "start": 0.0,
    "end": 45.5,
    "viral_score": 87.5,
    "reason": "Why this moment is viral: it reveals a shocking statistic about...",
    "hook": "The hook in the first 3 seconds",
    "keywords": ["success", "money", "motivation"],
    "emotion": "surprising"
  }}
]

Return ONLY the JSON array, no other text."""


class ClipSelector:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def select_viral_moments(
        self,
        transcript: str,
        timed_segments: list[dict],
        num_clips: int = 5,
        min_duration: int = 20,
        max_duration: int = 60,
        custom_prompt: Optional[str] = None,
    ) -> list[dict]:
        """
        Use GPT-4 to identify the most viral-worthy segments.
        Returns list of segment dicts with start/end timestamps.
        """
        if not transcript.strip():
            raise ValueError("Empty transcript — nothing to analyze")

        # Build a timed transcript for context
        timed_text = "\n".join([
            f"[{seg['start']:.1f}s - {seg['end']:.1f}s]: {seg['text']}"
            for seg in timed_segments
        ])

        custom_instruction = f"\nAdditional instructions: {custom_prompt}" if custom_prompt else ""

        prompt = VIRAL_MOMENT_PROMPT.format(
            num_clips=num_clips,
            min_duration=min_duration,
            max_duration=max_duration,
            transcript=timed_text[:12000],  # Limit context
            custom_instruction=custom_instruction,
        )

        logger.info(f"🤖 Sending transcript to GPT-4 ({len(timed_text)} chars)...")

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a viral content strategist. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            logger.info(f"📝 GPT-4 raw response: {content[:200]}...")

            # Parse JSON response
            data = json.loads(content)

            # Handle both {"clips": [...]} and [...] formats
            if isinstance(data, dict):
                segments = data.get("clips") or data.get("moments") or list(data.values())[0]
            else:
                segments = data

            # Validate and clamp durations
            valid = []
            for seg in segments:
                dur = seg["end"] - seg["start"]
                if dur < min_duration or dur > max_duration:
                    logger.warning(f"⚠️ Clip duration {dur:.1f}s out of bounds, adjusting...")
                    seg["end"] = min(seg["start"] + max_duration, seg["end"])
                    seg["end"] = max(seg["start"] + min_duration, seg["end"])
                valid.append(seg)

            logger.info(f"✅ Parsed {len(valid)} viral moments from GPT-4")
            return valid[:num_clips]

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parse error from GPT-4: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ GPT-4 clip selection failed: {e}")
            raise

    async def generate_hashtags(self, title: str, transcript_snippet: str, platform: str) -> list[str]:
        """Generate viral hashtags for a given platform."""
        prompt = f"""Generate 10-15 viral hashtags for a {platform} post.
Title: {title}
Content snippet: {transcript_snippet[:500]}

Return ONLY a JSON array of hashtag strings (with # symbol).
Example: ["#motivation", "#success", "#mindset"]"""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return list(data.values())[0] if data else []

    async def generate_caption(self, title: str, transcript: str, platform: str) -> str:
        """Generate an engaging caption/description for posting."""
        prompt = f"""Write an engaging {platform} caption for this clip.
Title: {title}
Transcript: {transcript[:800]}

Requirements:
- Hook in first line (no emojis at start for TikTok)
- 2-3 sentences max
- Call to action at end
- Feel authentic, not corporate

Return only the caption text."""

        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
