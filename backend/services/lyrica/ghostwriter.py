"""
Lyrica Ghostwriter Agent — Emotionally Injected Lyrical Generation.

Generates 'Soulfire Injected' lyrics using Lyrical Markup Language (LML)
with embedded emotional and biometric cues. Draws from specialized
'Heartbreak' and 'Struggle' corpora for authenticity.

LML Tag Reference:
  [VERSE]...[/VERSE]       — Verse block
  [CHORUS]...[/CHORUS]     — Chorus block
  [BRIDGE]...[/BRIDGE]     — Bridge block
  [HOOK]...[/HOOK]         — Hook/tagline
  [AD-LIB text]            — Ad-lib insertion
  [BREATH]                 — Breath mark (triggers PFA)
  [VOCAL-FRY]...[/VOCAL-FRY] — Vocal fry zone (triggers PFA)
  [EMOTION:type intensity]  — Emotion cue (heartbreak|struggle|triumph|rage|peace)
  [TEMPO:bpm]              — Tempo marker for MMA sync
  [FLOW:style]             — Flow pattern (trap|boom-bap|melodic|spoken-word|corrido)
  [PAUSE:ms]               — Silence duration
"""

import json
import uuid
import logging
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

HEARTBREAK_CORPUS = [
    "empty rooms echo what your voice used to fill",
    "I kept the receipts but lost the reason",
    "you left footprints on a heart that was still drying",
    "every song on the radio sounds like your goodbye",
    "I water dead flowers hoping something grows back",
    "the hardest part ain't losing you — it's remembering why I stayed",
    "your side of the bed still dips like you're coming home",
    "I learned to sleep alone but I never learned to dream without you",
]

STRUGGLE_CORPUS = [
    "started from the concrete, roses got no guarantee",
    "mama worked two shifts so I could waste one chance",
    "the block don't hand out scholarships",
    "every dollar I made had dirt under its fingernails",
    "they say pull yourself up but never hand you the rope",
    "I wrote my future on the back of an eviction notice",
    "grew up where the streetlights were the only stars we got",
    "hunger taught me math — I can count what I'm owed",
]

SYSTEM_PROMPT = """You are the Lyrica Ghostwriter — an elite AI lyricist for the Lyrica 3 Pro platform.

You generate emotionally authentic lyrics using Lyrical Markup Language (LML).

RULES:
1. ALWAYS output lyrics wrapped in LML tags
2. Embed [EMOTION:type intensity] cues (intensity 0.0-1.0)
3. Insert [BREATH] marks at natural phrase boundaries
4. Mark [VOCAL-FRY] sections for emotional peaks
5. Include [AD-LIB text] for ad-libs
6. Set [TEMPO:bpm] and [FLOW:style] at the top
7. Draw from heartbreak and struggle themes when appropriate
8. Match the requested genre/mood/style
9. Keep it real — no generic filler, no clichés
10. Output ONLY the LML-formatted lyrics, no explanations

AVAILABLE LML TAGS:
[VERSE]...[/VERSE], [CHORUS]...[/CHORUS], [BRIDGE]...[/BRIDGE], [HOOK]...[/HOOK]
[AD-LIB text], [BREATH], [VOCAL-FRY]...[/VOCAL-FRY]
[EMOTION:heartbreak|struggle|triumph|rage|peace 0.0-1.0]
[TEMPO:bpm], [FLOW:trap|boom-bap|melodic|spoken-word|corrido]
[PAUSE:ms]

CULTURAL ANCHORS (Southern Lyfestyle):
- SGV/El Monte heritage
- Chicano resilience
- Lowrider soul aesthetic
- Barrio-premium authenticity
- G-Funk and Corrido Tumbado influences"""

GENRE_PROMPTS = {
    "trap": "Write in a modern trap flow. Short punchy bars. Triple-time hi-hat energy. Hard-hitting hooks.",
    "boom_bap": "Write in classic boom-bap style. Complex wordplay. Multi-syllabic rhymes. Storytelling bars.",
    "melodic": "Write melodic rap/R&B. Sung hooks. Emotional vulnerability. Smooth cadence.",
    "corrido": "Write in corrido tumbado style. Narrative storytelling. Regional Mexican influences. Street tales.",
    "spoken_word": "Write spoken word poetry. Raw emotional delivery. No forced rhymes. Truth over technique.",
    "g_funk": "Write G-Funk style. Laid-back flow. West coast cadence. Smooth player energy.",
}


def parse_lml(raw_lyrics: str) -> dict:
    """Parse LML-tagged lyrics into structured sections."""
    import re

    sections = []
    emotion_cues = []
    breath_marks = []
    adlibs = []
    metadata = {}

    tempo_match = re.search(r'\[TEMPO:(\d+)\]', raw_lyrics)
    if tempo_match:
        metadata["tempo_bpm"] = int(tempo_match.group(1))

    flow_match = re.search(r'\[FLOW:(\w[\w-]*)\]', raw_lyrics)
    if flow_match:
        metadata["flow_style"] = flow_match.group(1)

    for section_type in ["VERSE", "CHORUS", "BRIDGE", "HOOK"]:
        pattern = rf'\[{section_type}\](.*?)\[/{section_type}\]'
        for i, match in enumerate(re.finditer(pattern, raw_lyrics, re.DOTALL)):
            content = match.group(1).strip()
            sections.append({
                "type": section_type.lower(),
                "index": i + 1,
                "content": content,
                "char_offset": match.start(),
            })

    for match in re.finditer(r'\[EMOTION:(\w+)\s+([\d.]+)\]', raw_lyrics):
        emotion_cues.append({
            "type": match.group(1),
            "intensity": float(match.group(2)),
            "position": match.start(),
        })

    for match in re.finditer(r'\[BREATH\]', raw_lyrics):
        breath_marks.append(match.start())

    for match in re.finditer(r'\[AD-LIB\s+(.+?)\]', raw_lyrics):
        adlibs.append({
            "text": match.group(1),
            "position": match.start(),
        })

    vocal_fry_zones = []
    for match in re.finditer(r'\[VOCAL-FRY\](.*?)\[/VOCAL-FRY\]', raw_lyrics, re.DOTALL):
        vocal_fry_zones.append({
            "content": match.group(1).strip(),
            "start": match.start(),
            "end": match.end(),
        })

    sections.sort(key=lambda s: s["char_offset"])

    return {
        "metadata": metadata,
        "sections": sections,
        "emotion_cues": emotion_cues,
        "breath_marks": breath_marks,
        "adlibs": adlibs,
        "vocal_fry_zones": vocal_fry_zones,
        "raw_lml": raw_lyrics,
    }


class GhostwriterAgent:
    """
    AI Ghostwriter — Soulfire Injected lyric generation.
    Uses LLM (GPT/Claude via Emergent API or direct) with emotion corpus injection.
    """

    async def generate(
        self,
        concept: str,
        genre: str = "trap",
        mood: str = "struggle",
        num_verses: int = 2,
        include_chorus: bool = True,
        include_bridge: bool = False,
        tempo_bpm: int = 140,
        custom_instructions: Optional[str] = None,
    ) -> dict:
        session_id = str(uuid.uuid4())

        corpus_injection = ""
        if mood in ("heartbreak", "love", "pain"):
            corpus_injection = "HEARTBREAK CORPUS SEEDS:\n" + "\n".join(
                f"- {line}" for line in HEARTBREAK_CORPUS[:4]
            )
        elif mood in ("struggle", "hustle", "grind"):
            corpus_injection = "STRUGGLE CORPUS SEEDS:\n" + "\n".join(
                f"- {line}" for line in STRUGGLE_CORPUS[:4]
            )

        genre_guidance = GENRE_PROMPTS.get(genre, GENRE_PROMPTS["trap"])

        structure_request = f"Write {num_verses} verses"
        if include_chorus:
            structure_request += " and a chorus"
        if include_bridge:
            structure_request += " and a bridge"

        user_prompt = f"""CONCEPT: {concept}
GENRE: {genre}
MOOD: {mood}
TEMPO: {tempo_bpm} BPM
STRUCTURE: {structure_request}

{genre_guidance}

{corpus_injection}

{f"ADDITIONAL INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

Generate the full song in LML format. Start with [TEMPO:{tempo_bpm}] and [FLOW:{genre}].
Include [EMOTION] cues, [BREATH] marks, [AD-LIB] tags, and at least one [VOCAL-FRY] section."""

        raw_lml = await self._call_llm(user_prompt)

        parsed = parse_lml(raw_lml)

        return {
            "session_id": session_id,
            "concept": concept,
            "genre": genre,
            "mood": mood,
            "tempo_bpm": tempo_bpm,
            "parsed": parsed,
            "section_count": len(parsed["sections"]),
            "emotion_cue_count": len(parsed["emotion_cues"]),
            "breath_mark_count": len(parsed["breath_marks"]),
            "adlib_count": len(parsed["adlibs"]),
            "vocal_fry_zones": len(parsed["vocal_fry_zones"]),
            "provider": "ghostwriter",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _call_llm(self, user_prompt: str) -> str:
        """Call LLM for lyric generation. Tries Emergent, then OpenAI, then falls back to template."""
        import os

        emergent_key = os.getenv("EMERGENT_LLM_KEY", "")
        openai_key = os.getenv("OPENAI_API_KEY", "")

        if emergent_key:
            try:
                return await self._call_emergent(user_prompt, emergent_key)
            except Exception:
                logger.warning("Emergent LLM call failed, trying OpenAI")

        if openai_key:
            try:
                return await self._call_openai(user_prompt, openai_key)
            except Exception:
                logger.warning("OpenAI call failed, falling back to template")

        return self._template_fallback(user_prompt)

    async def _call_emergent(self, prompt: str, api_key: str) -> str:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.emergentintegrations.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.85,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _call_openai(self, prompt: str, api_key: str) -> str:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.85,
        )
        return response.choices[0].message.content

    def _template_fallback(self, prompt: str) -> str:
        """Structured template when no LLM API key is available."""
        return """[TEMPO:140]
[FLOW:trap]

[EMOTION:struggle 0.8]
[VERSE]
[BREATH]
Started from the concrete, roses got no guarantee
Every dollar I made had dirt under its fingernails
[VOCAL-FRY]The block don't hand out scholarships[/VOCAL-FRY]
Mama worked two shifts so I could waste one chance
[BREATH]
But I ain't waste it — I invested in the pain
Turned every scar into a lesson, every loss into a gain
[AD-LIB yeah]
[/VERSE]

[EMOTION:triumph 0.7]
[CHORUS]
[BREATH]
We came from nothing, built it all from the ground
[VOCAL-FRY]Every brick we laid, they said we'd never be found[/VOCAL-FRY]
But look at us now — sovereign, standing tall
[AD-LIB let's go]
Empire built from struggle, we ain't never gonna fall
[BREATH]
[/CHORUS]

[EMOTION:struggle 0.6]
[VERSE]
[BREATH]
I wrote my future on the back of an eviction notice
Grew up where the streetlights were the only stars we got
[AD-LIB facts]
They say pull yourself up but never hand you the rope
[VOCAL-FRY]So I braided my own from the threads they forgot[/VOCAL-FRY]
[BREATH]
Hunger taught me math — I can count what I'm owed
And I'm collecting with interest on every broken road
[/VERSE]"""
