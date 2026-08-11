"""
LYRICA3 Intent Engine - Prompt Chain Orchestration (AURA → ASE → EFL → ECHO → EFAD)
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Orchestrates the 5-stage LLM prompt chain for Soulfire payload generation.
    Transforms user intent into complete audio production blueprint.

Prompt Chain Flow:
    1. AURA (Intent Extraction)
       ↓ semantic intent, rhetorical devices, bruised subtext, culture/style anchors
    2. ASE (Strategy Evaluation)
       ↓ novelty/cohesion/impact scores, disruption heuristics
    3. EFL (Emotional/Lyric Mapping)
       ↓ emotional mapping, LML vocal tags (<vocal_fry>, <adaptive_inhale>)
    4. ECHO (Technical Translation)
       ↓ Late-pocket timing (MMA), DSP mastering (PDA), stem priorities
    5. EFAD (Payload Assembly)
       ↓ Final Soulfire payload (track_metadata, dope_audio_blueprint, lyrics_payload)

Integration:
    - Called by Lyrica3 Pro main orchestration layer
    - Invokes MMA (rhythm), PDA (mastering), PFA (vocal biometrics) agents
    - Outputs strict JSON compatible with Soulfire engine

Architecture:
    PromptChainOrchestrator
        ├── stage_aura() → Intent extraction
        ├── stage_ase() → Strategy evaluation
        ├── stage_efl() → Emotional/lyric mapping
        ├── stage_echo() → Technical translation (calls MMA + PDA)
        ├── stage_efad() → Payload assembly
        └── execute_full_chain() → Main entry point

LLM Integration:
    - Uses GPT-4 or Claude for AURA/ASE/EFL stages (semantic reasoning)
    - Uses structured agents (MMA, PDA) for ECHO stage (deterministic)
    - Uses GPT-4 for EFAD stage (JSON assembly)

Example user input:
    "Make me a toxic breakup anthem. She's acting all innocent but I know the truth. 
     Late-pocket trap vibe, analog warmth, intimate vocals."

Example output:
    {
        "track_metadata": {
            "title": "Innocent Act",
            "core_genre": "Trap-Soul",
            "s2_mutation_applied": "Juxtaposition (soft vocals vs. harsh 808s)",
            "dna_tag_preview": "toxic-breakup-anthem-late-pocket-analog"
        },
        "dope_audio_blueprint": {
            "vulnerability_level": 0.72,
            "rhythm_groove": {...MMA output...},
            "texture_dsp": {...PDA output...},
            "mastering_sss": "SANCHA_SIREN_V1"
        },
        "lyrics_payload": [
            {"line": "She plays innocent, but I see through", "lml_trigger": "<vocal_fry>"},
            {"line": "All those lies, girl, I know you", "lml_trigger": "<emotional_crack>"}
        ]
    }
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import sub-agents
from LYRICA3.rhythm_engine import MMAGrooveAgent
from LYRICA3.mastering_engine import PDAMasteringAgent


@dataclass
class AURAState:
    """AURA stage output: Intent extraction."""
    semantic_intent: str
    rhetorical_devices: List[str]
    bruised_subtext: str
    culture_anchors: List[str]
    style_anchors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ASEState:
    """ASE stage output: Strategy evaluation."""
    novelty_score: float  # 0.0-1.0
    cohesion_score: float  # 0.0-1.0
    impact_score: float  # 0.0-1.0
    disruption_heuristic: Optional[str]  # juxtaposition, transplantation, metamorphic_blending
    strategy_rationale: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EFLState:
    """EFL stage output: Emotional/lyric mapping."""
    emotional_mapping: Dict[str, float]  # e.g., {"anger": 0.6, "vulnerability": 0.8}
    lml_tags: List[str]  # e.g., ["<vocal_fry>", "<adaptive_inhale>"]
    lyric_strategy: str
    vulnerability_level: float  # 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ECHOState:
    """ECHO stage output: Technical translation."""
    rhythm_groove: Dict[str, Any]  # MMA output
    texture_dsp: Dict[str, Any]  # PDA output
    stem_priorities: Dict[str, float]  # e.g., {"vocal": 1.0, "808": 0.85, "drums": 0.7}
    timing_descriptor: str  # e.g., "85bpm_chicano_soul_cruising"
    texture_descriptor: str  # e.g., "vintage_ssl_console_warmth"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SoulfirePayload:
    """EFAD stage output: Final Soulfire payload."""
    track_metadata: Dict[str, Any]
    dope_audio_blueprint: Dict[str, Any]
    lyrics_payload: List[Dict[str, str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PromptChainOrchestrator:
    """
    Orchestrates the 5-stage LLM prompt chain for Soulfire payload generation.
    
    Mission:
        Transform user intent into complete audio production blueprint.
        Coordinate LLM reasoning stages (AURA/ASE/EFL) with deterministic agents (MMA/PDA).
    
    Usage:
        >>> orchestrator = PromptChainOrchestrator(llm_client=your_llm_client)
        >>> payload = orchestrator.execute_full_chain(user_input="toxic breakup anthem...")
        >>> print(json.dumps(payload.to_dict(), indent=2))
    """
    
    def __init__(self, llm_client=None, seed: int = None):
        """
        Initialize orchestrator.
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.) - optional for testing
            seed: Random seed for reproducible agent outputs
        """
        self.llm_client = llm_client
        self.mma_agent = MMAGrooveAgent(seed=seed)
        self.pda_agent = PDAMasteringAgent()
        
        # Load prompt templates
        self.prompts = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """
        Load prompt templates for each stage.
        
        Returns:
            Dict with prompt templates
        """
        return {
            "AURA": """[AURA CORTEX INIT]
Analyze this user request and extract:
1) semantic intent
2) rhetorical devices
3) bruised subtext
4) culture/style anchors

User input:
{user_input}

Return concise structured text with explicit bullets.""",
            
            "ASE": """[ASE CORE INIT]
Evaluate the AURA output for:
1) novelty
2) cohesion
3) expressive impact

Apply disruption heuristics when useful:
- juxtaposition
- transplantation
- metamorphic blending

AURA output:
{aura_state}

Return a scored strategy recommendation with clear rationale.""",
            
            "EFL": """[EFL ENGINE INIT]
Using the AURA analysis below, produce:
1) emotional/cultural mapping
2) vocal biometric tags (LML)
3) lyric strategy hints

AURA output:
{aura_state}

Include tags such as <vocal_fry>, <adaptive_inhale>, <emotional_crack>, <proximity_effect> when relevant.""",
            
            "ECHO": """[ECHO WEAVER INIT]
Convert the ASE strategy into:
1) temporal groove physics (late-pocket timing)
2) DSP/mastering profile
3) stem-level mix priorities

ASE output:
{ase_state}

Return precise values where possible (ms offsets, dB targets, filter ranges, drive amounts).""",
            
            "EFAD": """[EFAD ORCHESTRATOR INIT]
Assemble the final Soulfire payload using the following pipeline context.

AURA:
{aura_state}

EFL:
{efl_state}

ASE:
{ase_state}

ECHO:
{echo_state}

Required JSON schema:
{schema}

Rules:
- Output strict JSON only.
- Include track_metadata, dope_audio_blueprint, lyrics_payload.
- Embed dna_tag_preview."""
        }
    
    def stage_aura(self, user_input: str) -> AURAState:
        """
        AURA stage: Extract semantic intent and cultural anchors.
        
        Args:
            user_input: User's request string
        
        Returns:
            AURAState with extracted intent
        
        Example:
            Input: "toxic breakup anthem, late-pocket trap, analog warmth"
            Output: AURAState(
                semantic_intent="Create emotionally charged breakup song",
                rhetorical_devices=["toxic", "anthem"],
                bruised_subtext="Pain masked by confidence",
                culture_anchors=["SGV", "trap-soul"],
                style_anchors=["late-pocket", "analog"]
            )
        """
        # If LLM client is available, use it
        if self.llm_client:
            prompt = self.prompts["AURA"].format(user_input=user_input)
            response = self.llm_client.complete(prompt)
            # Parse LLM response (simplified - real implementation would use structured parsing)
            return self._parse_aura_response(response)
        
        # Fallback: Rule-based extraction for testing
        return self._parse_aura_fallback(user_input)
    
    def _parse_aura_fallback(self, user_input: str) -> AURAState:
        """Fallback rule-based AURA parsing for testing."""
        user_lower = user_input.lower()
        
        # Extract semantic intent
        if "breakup" in user_lower or "toxic" in user_lower:
            semantic_intent = "Create emotionally charged breakup anthem"
        elif "love" in user_lower or "romance" in user_lower:
            semantic_intent = "Create intimate love song"
        else:
            semantic_intent = "Create expressive song"
        
        # Extract rhetorical devices
        rhetorical_devices = []
        if "toxic" in user_lower:
            rhetorical_devices.append("toxic")
        if "anthem" in user_lower:
            rhetorical_devices.append("anthem")
        if "vibe" in user_lower:
            rhetorical_devices.append("vibe")
        
        # Extract bruised subtext
        if "toxic" in user_lower or "truth" in user_lower:
            bruised_subtext = "Pain masked by defensive confidence"
        else:
            bruised_subtext = "Emotional vulnerability"
        
        # Extract culture/style anchors
        culture_anchors = []
        style_anchors = []
        
        if any(kw in user_lower for kw in ["trap", "drill", "808"]):
            culture_anchors.append("trap")
        if any(kw in user_lower for kw in ["soul", "chicano", "sgv"]):
            culture_anchors.append("SGV/soul")
        if any(kw in user_lower for kw in ["corrido", "waltz"]):
            culture_anchors.append("corrido")
        
        if "late-pocket" in user_lower or "late pocket" in user_lower:
            style_anchors.append("late-pocket")
        if any(kw in user_lower for kw in ["analog", "warmth", "vintage"]):
            style_anchors.append("analog-warmth")
        if any(kw in user_lower for kw in ["intimate", "close", "proximity"]):
            style_anchors.append("intimate-proximity")
        
        return AURAState(
            semantic_intent=semantic_intent,
            rhetorical_devices=rhetorical_devices,
            bruised_subtext=bruised_subtext,
            culture_anchors=culture_anchors if culture_anchors else ["contemporary"],
            style_anchors=style_anchors if style_anchors else ["standard"]
        )
    
    def stage_ase(self, aura_state: AURAState) -> ASEState:
        """
        ASE stage: Evaluate strategy and apply disruption heuristics.
        
        Args:
            aura_state: Output from AURA stage
        
        Returns:
            ASEState with strategy evaluation
        """
        # Rule-based strategy evaluation (simplified)
        novelty_score = 0.7 if len(aura_state.rhetorical_devices) > 2 else 0.5
        cohesion_score = 0.8 if len(aura_state.culture_anchors) > 0 else 0.6
        impact_score = 0.85 if "toxic" in aura_state.rhetorical_devices else 0.7
        
        # Determine disruption heuristic
        disruption_heuristic = None
        strategy_rationale = "Standard production approach"
        
        if len(aura_state.style_anchors) >= 2:
            disruption_heuristic = "juxtaposition"
            strategy_rationale = "Juxtapose contrasting elements (e.g., soft vocals vs. harsh production)"
        elif "analog-warmth" in aura_state.style_anchors and "trap" in aura_state.culture_anchors:
            disruption_heuristic = "metamorphic_blending"
            strategy_rationale = "Blend vintage analog warmth with modern trap aesthetics"
        
        return ASEState(
            novelty_score=novelty_score,
            cohesion_score=cohesion_score,
            impact_score=impact_score,
            disruption_heuristic=disruption_heuristic,
            strategy_rationale=strategy_rationale
        )
    
    def stage_efl(self, aura_state: AURAState, ase_state: ASEState) -> EFLState:
        """
        EFL stage: Generate emotional mapping and LML vocal tags.
        
        Args:
            aura_state: Output from AURA stage
            ase_state: Output from ASE stage
        
        Returns:
            EFLState with emotional mapping
        """
        # Generate emotional mapping
        emotional_mapping = {}
        
        if "toxic" in aura_state.rhetorical_devices:
            emotional_mapping["anger"] = 0.6
            emotional_mapping["vulnerability"] = 0.8
            emotional_mapping["confidence"] = 0.7
        else:
            emotional_mapping["vulnerability"] = 0.5
            emotional_mapping["intimacy"] = 0.7
        
        # Determine LML tags based on emotional mapping
        lml_tags = []
        if emotional_mapping.get("vulnerability", 0) > 0.7:
            lml_tags.append("<vocal_fry>")
            lml_tags.append("<emotional_crack>")
        if "intimate-proximity" in aura_state.style_anchors:
            lml_tags.append("<adaptive_inhale>")
            lml_tags.append("<proximity_effect>")
        
        # Calculate vulnerability level
        vulnerability_level = emotional_mapping.get("vulnerability", 0.5)
        
        # Generate lyric strategy
        if ase_state.disruption_heuristic == "juxtaposition":
            lyric_strategy = "Contrast defensive bravado with moments of raw vulnerability"
        else:
            lyric_strategy = "Maintain consistent emotional tone with subtle intensity shifts"
        
        return EFLState(
            emotional_mapping=emotional_mapping,
            lml_tags=lml_tags,
            lyric_strategy=lyric_strategy,
            vulnerability_level=vulnerability_level
        )
    
    def stage_echo(self, aura_state: AURAState, ase_state: ASEState, efl_state: EFLState) -> ECHOState:
        """
        ECHO stage: Translate strategy into technical parameters (MMA + PDA).
        
        Args:
            aura_state: Output from AURA stage
            ase_state: Output from ASE stage
            efl_state: Output from EFL stage
        
        Returns:
            ECHOState with rhythm groove and texture DSP
        """
        # Build timing descriptor for MMA
        timing_descriptor = self._build_timing_descriptor(aura_state, ase_state)
        
        # Generate rhythm groove using MMA
        rhythm_groove = self.mma_agent.generate_midi_sequence(timing_descriptor)
        
        # Build texture descriptor for PDA
        texture_descriptor = self._build_texture_descriptor(aura_state, ase_state)
        
        # Generate texture DSP using PDA
        texture_dsp = self.pda_agent.generate_master_bus_dsp(texture_descriptor)
        
        # Determine stem priorities
        stem_priorities = {
            "vocal": 1.0,  # Always highest priority
            "808": 0.85 if "trap" in aura_state.culture_anchors else 0.7,
            "drums": 0.75,
            "melody": 0.65
        }
        
        return ECHOState(
            rhythm_groove=rhythm_groove,
            texture_dsp=texture_dsp,
            stem_priorities=stem_priorities,
            timing_descriptor=timing_descriptor,
            texture_descriptor=texture_descriptor
        )
    
    def _build_timing_descriptor(self, aura_state: AURAState, ase_state: ASEState) -> str:
        """Build MMA timing descriptor from AURA/ASE state."""
        # Extract BPM (default to 85 for soul, 120 for trap)
        if "soul" in str(aura_state.culture_anchors).lower():
            bpm = 85
        elif "trap" in str(aura_state.culture_anchors).lower():
            bpm = 120
        elif "drill" in str(aura_state.culture_anchors).lower():
            bpm = 140
        else:
            bpm = 95
        
        # Extract style
        style_parts = []
        if "trap" in str(aura_state.culture_anchors).lower():
            style_parts.append("trap")
        if "soul" in str(aura_state.culture_anchors).lower():
            style_parts.append("soul")
        if "drill" in str(aura_state.culture_anchors).lower():
            style_parts.append("drill")
        
        # Add intensity
        if ase_state.impact_score > 0.8:
            style_parts.append("aggressive")
        elif "intimate" in str(aura_state.style_anchors).lower():
            style_parts.append("cruising")
        
        # Always include late-pocket if in style anchors
        if "late-pocket" in aura_state.style_anchors:
            style_parts.append("late_snare")
        
        return f"{bpm}bpm_{'_'.join(style_parts)}"
    
    def _build_texture_descriptor(self, aura_state: AURAState, ase_state: ASEState) -> str:
        """Build PDA texture descriptor from AURA/ASE state."""
        texture_parts = []
        
        # Check for analog/warmth
        if "analog-warmth" in aura_state.style_anchors:
            texture_parts.append("vintage_ssl")
        if any("analog" in s.lower() or "warmth" in s.lower() for s in aura_state.style_anchors):
            texture_parts.append("analog_warmth")
        
        # Check for lo-fi
        if any("lo" in s.lower() and "fi" in s.lower() for s in aura_state.style_anchors):
            texture_parts.append("lo_fi")
        
        # Check for modern/drill
        if "trap" in str(aura_state.culture_anchors).lower() or "drill" in str(aura_state.culture_anchors).lower():
            texture_parts.append("modern_sub_heavy")
        
        # Check for proximity
        if "intimate-proximity" in aura_state.style_anchors:
            texture_parts.append("intimate_proximity")
        
        return "_".join(texture_parts) if texture_parts else "standard_production"
    
    def stage_efad(self, aura_state: AURAState, ase_state: ASEState, efl_state: EFLState, echo_state: ECHOState) -> SoulfirePayload:
        """
        EFAD stage: Assemble final Soulfire payload.
        
        Args:
            aura_state: Output from AURA stage
            ase_state: Output from ASE stage
            efl_state: Output from EFL stage
            echo_state: Output from ECHO stage
        
        Returns:
            SoulfirePayload with complete production blueprint
        """
        # Build track metadata
        track_metadata = {
            "title": self._generate_title(aura_state),
            "core_genre": self._determine_genre(aura_state),
            "s2_mutation_applied": ase_state.disruption_heuristic or "None",
            "dna_tag_preview": self._generate_dna_tag(aura_state, efl_state)
        }
        
        # Build audio blueprint
        dope_audio_blueprint = {
            "vulnerability_level": efl_state.vulnerability_level,
            "rhythm_groove": echo_state.rhythm_groove,
            "texture_dsp": echo_state.texture_dsp,
            "mastering_sss": self._select_sss_preset(efl_state),
            "stem_priorities": echo_state.stem_priorities
        }
        
        # Build lyrics payload (placeholder - real implementation would generate actual lyrics)
        lyrics_payload = self._generate_lyrics_placeholder(aura_state, efl_state)
        
        return SoulfirePayload(
            track_metadata=track_metadata,
            dope_audio_blueprint=dope_audio_blueprint,
            lyrics_payload=lyrics_payload
        )
    
    def _generate_title(self, aura_state: AURAState) -> str:
        """Generate track title from AURA state."""
        if "toxic" in aura_state.rhetorical_devices:
            return "Innocent Act"
        elif "anthem" in aura_state.rhetorical_devices:
            return "Rise Above"
        else:
            return "Untitled Track"
    
    def _determine_genre(self, aura_state: AURAState) -> str:
        """Determine core genre from culture anchors."""
        if "trap" in str(aura_state.culture_anchors).lower() and "soul" in str(aura_state.culture_anchors).lower():
            return "Trap-Soul"
        elif "trap" in str(aura_state.culture_anchors).lower():
            return "Trap"
        elif "soul" in str(aura_state.culture_anchors).lower():
            return "Soul"
        elif "drill" in str(aura_state.culture_anchors).lower():
            return "Drill"
        else:
            return "Contemporary"
    
    def _generate_dna_tag(self, aura_state: AURAState, efl_state: EFLState) -> str:
        """Generate DNA tag preview."""
        parts = []
        if "toxic" in aura_state.rhetorical_devices:
            parts.append("toxic-breakup")
        if "late-pocket" in aura_state.style_anchors:
            parts.append("late-pocket")
        if "analog-warmth" in aura_state.style_anchors:
            parts.append("analog")
        if efl_state.vulnerability_level > 0.7:
            parts.append("vulnerable")
        
        return "-".join(parts) if parts else "standard"
    
    def _select_sss_preset(self, efl_state: EFLState) -> str:
        """Select SSS preset based on vulnerability level."""
        if efl_state.vulnerability_level > 0.7:
            return "SANCHA_SIREN_V1"
        else:
            return "TOXICO_HARSH_V1"
    
    def _generate_lyrics_placeholder(self, aura_state: AURAState, efl_state: EFLState) -> List[Dict[str, str]]:
        """Generate placeholder lyrics with LML tags."""
        if "toxic" in aura_state.rhetorical_devices:
            return [
                {"line": "She plays innocent, but I see through", "lml_trigger": efl_state.lml_tags[0] if efl_state.lml_tags else ""},
                {"line": "All those lies, girl, I know you", "lml_trigger": efl_state.lml_tags[1] if len(efl_state.lml_tags) > 1 else ""}
            ]
        else:
            return [
                {"line": "Placeholder lyric line 1", "lml_trigger": ""},
                {"line": "Placeholder lyric line 2", "lml_trigger": ""}
            ]
    
    def execute_full_chain(self, user_input: str) -> SoulfirePayload:
        """
        Execute full 5-stage prompt chain: AURA → ASE → EFL → ECHO → EFAD.
        
        Args:
            user_input: User's request string
        
        Returns:
            SoulfirePayload with complete production blueprint
        
        Example:
            >>> orchestrator = PromptChainOrchestrator()
            >>> payload = orchestrator.execute_full_chain(
            ...     "Make me a toxic breakup anthem. Late-pocket trap vibe, analog warmth, intimate vocals."
            ... )
            >>> print(json.dumps(payload.to_dict(), indent=2))
        """
        # Stage 1: AURA - Intent extraction
        aura_state = self.stage_aura(user_input)
        
        # Stage 2: ASE - Strategy evaluation
        ase_state = self.stage_ase(aura_state)
        
        # Stage 3: EFL - Emotional/lyric mapping
        efl_state = self.stage_efl(aura_state, ase_state)
        
        # Stage 4: ECHO - Technical translation (MMA + PDA)
        echo_state = self.stage_echo(aura_state, ase_state, efl_state)
        
        # Stage 5: EFAD - Payload assembly
        payload = self.stage_efad(aura_state, ase_state, efl_state, echo_state)
        
        return payload


# Convenience function for direct invocation
def generate_soulfire_payload(user_input: str, llm_client=None, seed: int = None) -> Dict[str, Any]:
    """
    Convenience function to generate Soulfire payload from user input.
    
    Args:
        user_input: User's request string
        llm_client: Optional LLM client for AURA/ASE/EFL stages
        seed: Random seed for reproducible outputs
    
    Returns:
        Dict with complete Soulfire payload
    
    Example:
        >>> payload = generate_soulfire_payload(
        ...     "toxic breakup anthem, late-pocket trap, analog warmth"
        ... )
        >>> print(json.dumps(payload, indent=2))
    """
    orchestrator = PromptChainOrchestrator(llm_client=llm_client, seed=seed)
    soulfire_payload = orchestrator.execute_full_chain(user_input)
    return soulfire_payload.to_dict()


# Example usage
if __name__ == "__main__":
    # Test with example user input
    test_inputs = [
        "Make me a toxic breakup anthem. She's acting all innocent but I know the truth. Late-pocket trap vibe, analog warmth, intimate vocals.",
        "Create a drill track with aggressive 808s and modern production.",
        "I want a soul song with chicano influence, intimate vocals, vintage warmth."
    ]
    
    orchestrator = PromptChainOrchestrator(seed=42)
    
    for user_input in test_inputs:
        print(f"\n{'='*80}")
        print(f"User Input: {user_input}")
        print(f"{'='*80}\n")
        
        payload = orchestrator.execute_full_chain(user_input)
        print(json.dumps(payload.to_dict(), indent=2))
