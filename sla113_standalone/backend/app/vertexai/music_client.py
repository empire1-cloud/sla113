"""Vertex AI Music Client — Lyria 3 (lyria-003) integration for SLA113."""
import asyncio
import base64
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Lyria 3 model ID — do NOT downgrade to lyria-002
LYRIA_MODEL = "lyria-003"
LYRIA_ENDPOINT = (
    "https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/"
    "{location}/publishers/google/models/{model}:predict"
)


def _access_token() -> str:
    """Get a short-lived Google access token via ADC."""
    import google.auth
    import google.auth.transport.requests

    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    return creds.token


class VertexMusicClient:
    """Lyria 3 music generation via Vertex AI Generative Media."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
    ):
        self.project_id = project_id or os.environ.get("VERTEX_PROJECT_ID", "")
        self.location = location
        self._endpoint = LYRIA_ENDPOINT.format(
            location=self.location,
            project=self.project_id,
            model=LYRIA_MODEL,
        )
        logger.info("VertexMusicClient ready (project=%s, model=%s)", self.project_id, LYRIA_MODEL)

    async def generate_music(
        self,
        prompt: str,
        duration_seconds: int = 30,
        style: str = "cinematic",
        negative_prompt: str = "",
    ) -> dict:
        """Generate music using Lyria 3.

        Returns dict with keys:
          status: "ok" | "stub" | "error"
          audio_b64: base64-encoded WAV/MP3 bytes (on success)
          prompt, duration, style
          message: human-readable status
        """
        if not self.project_id:
            logger.warning("VERTEX_PROJECT_ID not set — returning stub")
            return {
                "status": "stub",
                "prompt": prompt,
                "duration": duration_seconds,
                "style": style,
                "message": "Set VERTEX_PROJECT_ID env var to activate Lyria 3.",
            }

        payload = {
            "instances": [
                {
                    "prompt": f"{style} — {prompt}",
                    "negative_prompt": negative_prompt,
                    "duration_seconds": duration_seconds,
                }
            ],
            "parameters": {"sampleCount": 1},
        }

        try:
            token = await asyncio.to_thread(_access_token)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(self._endpoint, json=payload, headers=headers)

            if resp.status_code == 403:
                logger.error("Lyria 3 allowlist required. Visit https://cloud.google.com/vertex-ai/generative-ai/docs/music/overview")
                return {
                    "status": "error",
                    "message": "Lyria 3 access not yet approved for this project. Submit allowlist request.",
                    "prompt": prompt,
                    "duration": duration_seconds,
                    "style": style,
                }

            resp.raise_for_status()
            data = resp.json()
            audio_b64 = data["predictions"][0]["bytesBase64Encoded"]
            return {
                "status": "ok",
                "audio_b64": audio_b64,
                "prompt": prompt,
                "duration": duration_seconds,
                "style": style,
                "message": f"Generated {duration_seconds}s via {LYRIA_MODEL}",
            }

        except httpx.HTTPStatusError as e:
            logger.error("Lyria 3 HTTP error: %s — %s", e.response.status_code, e.response.text[:400])
            return {"status": "error", "message": str(e), "prompt": prompt}
        except Exception as e:
            logger.error("Lyria 3 unexpected error: %s", e)
            return {"status": "error", "message": str(e), "prompt": prompt}

    async def generate_sfx(
        self,
        description: str,
        duration_seconds: int = 5,
    ) -> dict:
        """Generate a sound effect via Lyria 3."""
        return await self.generate_music(
            prompt=description,
            duration_seconds=duration_seconds,
            style="sound effect foley",
        )

    async def generate_full_song(
        self,
        sections: list[dict],
        crossfade_ms: int = 2000,
    ) -> dict:
        """Fire parallel Lyria 3 calls for each song section and return combined audio.

        sections: list of {name, prompt, duration_seconds, style}
        Returns: {status, sections: [{name, audio_b64}], crossfade_ms}
        """
        tasks = [
            self.generate_music(
                prompt=s["prompt"],
                duration_seconds=s.get("duration_seconds", 30),
                style=s.get("style", "cinematic"),
            )
            for s in sections
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        section_results = []
        for s, r in zip(sections, results):
            if isinstance(r, Exception):
                section_results.append({"name": s["name"], "status": "error", "message": str(r)})
            else:
                section_results.append({"name": s["name"], **r})

        overall = "ok" if all(r.get("status") == "ok" for r in section_results) else "partial"
        return {
            "status": overall,
            "sections": section_results,
            "crossfade_ms": crossfade_ms,
            "model": LYRIA_MODEL,
        }
