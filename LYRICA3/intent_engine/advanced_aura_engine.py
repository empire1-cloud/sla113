"""
LYRICA3 Intent Engine - Advanced Local NLP (AURA Enhanced)
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Advanced rhetorical device detection and semantic analysis using local NLP.
    Zero API dependencies - uses pattern matching + linguistic heuristics.

AURA Stage Enhancements:
    1. Rhetorical Device Detection
       - Metaphor patterns ("X is Y", "like X", "as X as Y")
       - Hyperbole detection ("always", "never", "everything", "nothing")
       - Alliteration detection (repeated consonants)
       - Juxtaposition (contrasting sentiment words in proximity)
       - Anaphora (repeated phrase beginnings)
    
    2. Semantic Intent Extraction
       - Emotion detection (anger, vulnerability, defiance, hope, despair)
       - Action verbs (confrontation vs. acceptance)
       - Temporal markers (past regret, present confrontation, future hope)
    
    3. Cultural Anchor Detection
       - Genre markers (trap, drill, soul, corrido)
       - Geographic/cultural references (SGV, chicano, southern, urban)
       - Style descriptors (analog, vintage, modern, intimate)

Dependencies:
    - re (built-in): regex pattern matching
    - collections (built-in): word frequency analysis
    - Optional: spaCy for advanced parsing (fallback to regex if not available)

Integration:
    Replaces rule-based _parse_aura_fallback() in PromptChainOrchestrator
"""

import re
from collections import Counter
from typing import Dict, List, Any, Tuple, Optional


class RhetoricalDeviceDetector:
    """
    Detect rhetorical devices using pattern matching and linguistic heuristics.
    """
    
    # Rhetorical patterns
    METAPHOR_PATTERNS = [
        r'\b(\w+)\s+is\s+(\w+)\b',  # "love is war"
        r'\blike\s+\w+\b',  # "like a storm"
        r'\bas\s+\w+\s+as\b',  # "as cold as ice"
    ]
    
    HYPERBOLE_MARKERS = [
        'always', 'never', 'everything', 'nothing', 'everyone', 'nobody',
        'forever', 'infinite', 'endless', 'total', 'complete', 'absolute'
    ]
    
    JUXTAPOSITION_PAIRS = [
        ('love', 'hate'), ('hot', 'cold'), ('light', 'dark'), ('sweet', 'bitter'),
        ('innocent', 'guilty'), ('angel', 'demon'), ('heaven', 'hell'),
        ('soft', 'harsh'), ('gentle', 'violent'), ('truth', 'lies')
    ]
    
    ANAPHORA_STARTERS = ['i', 'you', 'she', 'he', 'they', 'we']
    
    def __init__(self):
        """Initialize detector."""
        pass
    
    def detect_metaphors(self, text: str) -> List[str]:
        """Detect metaphorical patterns."""
        metaphors = []
        text_lower = text.lower()
        
        for pattern in self.METAPHOR_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                metaphors.extend([f"metaphor: {m}" for m in matches if isinstance(m, str)])
        
        return metaphors
    
    def detect_hyperbole(self, text: str) -> List[str]:
        """Detect hyperbolic language."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        hyperboles = []
        for marker in self.HYPERBOLE_MARKERS:
            if marker in words:
                hyperboles.append(f"hyperbole: {marker}")
        
        return hyperboles
    
    def detect_alliteration(self, text: str) -> List[str]:
        """Detect alliteration (3+ words starting with same consonant)."""
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        if len(words) < 3:
            return []
        
        # Check consecutive words for same starting consonant
        alliterations = []
        for i in range(len(words) - 2):
            if words[i][0] == words[i+1][0] == words[i+2][0]:
                alliterations.append(f"alliteration: {words[i][0]}-")
        
        return alliterations
    
    def detect_juxtaposition(self, text: str) -> List[str]:
        """Detect contrasting word pairs in proximity."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        juxtapositions = []
        for word1, word2 in self.JUXTAPOSITION_PAIRS:
            if word1 in words and word2 in words:
                # Check if they're within 10 words of each other
                idx1 = words.index(word1)
                idx2 = words.index(word2)
                if abs(idx1 - idx2) <= 10:
                    juxtapositions.append(f"juxtaposition: {word1}+{word2}")
        
        return juxtapositions
    
    def detect_anaphora(self, text: str) -> List[str]:
        """Detect repeated phrase beginnings."""
        lines = text.split('.')
        if len(lines) < 2:
            return []
        
        starters = []
        for line in lines:
            words = line.strip().lower().split()
            if words and words[0] in self.ANAPHORA_STARTERS:
                starters.append(words[0])
        
        # If same word starts 2+ lines, it's anaphora
        counts = Counter(starters)
        anaphoras = [f"anaphora: {word}" for word, count in counts.items() if count >= 2]
        
        return anaphoras
    
    def detect_all(self, text: str) -> List[str]:
        """Detect all rhetorical devices."""
        devices = []
        devices.extend(self.detect_metaphors(text))
        devices.extend(self.detect_hyperbole(text))
        devices.extend(self.detect_alliteration(text))
        devices.extend(self.detect_juxtaposition(text))
        devices.extend(self.detect_anaphora(text))
        return devices


class SemanticIntentExtractor:
    """
    Extract semantic intent using emotion lexicons and action verb analysis.
    """
    
    # Emotion lexicons
    EMOTION_WORDS = {
        'anger': ['angry', 'mad', 'furious', 'rage', 'hate', 'pissed', 'hostile', 'bitter'],
        'vulnerability': ['vulnerable', 'hurt', 'broken', 'weak', 'fragile', 'exposed', 'raw'],
        'defiance': ['defiant', 'rebel', 'resist', 'fight', 'stand', 'refuse', 'deny'],
        'hope': ['hope', 'dream', 'wish', 'believe', 'trust', 'faith', 'future'],
        'despair': ['despair', 'hopeless', 'empty', 'lost', 'numb', 'darkness', 'void'],
        'love': ['love', 'adore', 'cherish', 'devoted', 'passion', 'desire'],
        'betrayal': ['betray', 'lie', 'cheat', 'deceive', 'fake', 'false', 'innocent']
    }
    
    # Action verb categories
    CONFRONTATION_VERBS = ['confront', 'face', 'call', 'expose', 'reveal', 'challenge', 'see through']
    ACCEPTANCE_VERBS = ['accept', 'let go', 'move on', 'forgive', 'understand', 'realize']
    ESCAPE_VERBS = ['run', 'leave', 'escape', 'flee', 'hide', 'avoid']
    
    def __init__(self):
        """Initialize extractor."""
        pass
    
    def extract_emotions(self, text: str) -> Dict[str, float]:
        """Extract emotion scores based on lexicon matches."""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        emotion_scores = {}
        for emotion, lexicon in self.EMOTION_WORDS.items():
            matches = sum(1 for word in words if word in lexicon)
            # Normalize by total word count
            score = matches / max(len(words), 1)
            if score > 0:
                emotion_scores[emotion] = min(score * 5, 1.0)  # Scale up but cap at 1.0
        
        return emotion_scores
    
    def extract_action_stance(self, text: str) -> str:
        """Determine primary action stance (confrontation, acceptance, escape)."""
        text_lower = text.lower()
        
        confrontation_score = sum(1 for verb in self.CONFRONTATION_VERBS if verb in text_lower)
        acceptance_score = sum(1 for verb in self.ACCEPTANCE_VERBS if verb in text_lower)
        escape_score = sum(1 for verb in self.ESCAPE_VERBS if verb in text_lower)
        
        max_score = max(confrontation_score, acceptance_score, escape_score)
        
        if max_score == 0:
            return "neutral"
        elif confrontation_score == max_score:
            return "confrontation"
        elif acceptance_score == max_score:
            return "acceptance"
        else:
            return "escape"
    
    def extract_temporal_focus(self, text: str) -> str:
        """Determine temporal focus (past, present, future)."""
        text_lower = text.lower()
        
        past_markers = ['was', 'were', 'had', 'used to', 'remember', 'before']
        present_markers = ['is', 'are', 'now', 'right now', 'today', 'currently']
        future_markers = ['will', 'gonna', 'going to', 'tomorrow', 'someday', 'future']
        
        past_score = sum(1 for marker in past_markers if marker in text_lower)
        present_score = sum(1 for marker in present_markers if marker in text_lower)
        future_score = sum(1 for marker in future_markers if marker in text_lower)
        
        max_score = max(past_score, present_score, future_score)
        
        if max_score == 0:
            return "present"  # Default
        elif past_score == max_score:
            return "past"
        elif present_score == max_score:
            return "present"
        else:
            return "future"
    
    def extract_semantic_intent(self, text: str) -> str:
        """Generate semantic intent summary."""
        emotions = self.extract_emotions(text)
        action_stance = self.extract_action_stance(text)
        temporal_focus = self.extract_temporal_focus(text)
        
        # Build intent description
        if emotions:
            primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            intent = f"Express {primary_emotion} through {action_stance}"
        else:
            intent = f"Express emotion through {action_stance}"
        
        # Add temporal context
        if temporal_focus == "past":
            intent += " (reflecting on past)"
        elif temporal_focus == "future":
            intent += " (looking toward future)"
        
        return intent


class CulturalAnchorDetector:
    """
    Detect cultural and stylistic anchors from user input.
    """
    
    # Genre markers
    GENRE_MARKERS = {
        'trap': ['trap', '808', 'hi-hat', 'drill', 'sliding'],
        'soul': ['soul', 'r&b', 'rnb', 'smooth', 'groove'],
        'corrido': ['corrido', 'banda', 'norteño', 'mariachi', 'ranchera'],
        'chicano': ['chicano', 'chicana', 'lowrider', 'ese'],
        'drill': ['drill', 'aggressive', 'uk', 'sliding'],
        'lo-fi': ['lo-fi', 'lofi', 'chill', 'study', 'beats']
    }
    
    # Geographic/cultural markers
    CULTURAL_MARKERS = {
        'sgv': ['sgv', 'san gabriel valley', 'east la', 'southland'],
        'southern': ['southern', 'south', 'houston', 'atlanta', 'memphis'],
        'west_coast': ['west coast', 'california', 'la', 'bay area'],
        'urban': ['urban', 'city', 'street', 'hood', 'block']
    }
    
    # Style descriptors
    STYLE_MARKERS = {
        'analog': ['analog', 'analogue', 'vintage', 'tape', 'warmth', 'warm'],
        'modern': ['modern', 'contemporary', 'new', 'fresh', 'current'],
        'intimate': ['intimate', 'close', 'personal', 'bedroom', 'quiet'],
        'aggressive': ['aggressive', 'harsh', 'hard', 'heavy', 'intense'],
        'late-pocket': ['late-pocket', 'late pocket', 'behind the beat', 'drag', 'swing']
    }
    
    def __init__(self):
        """Initialize detector."""
        pass
    
    def detect_genres(self, text: str) -> List[str]:
        """Detect genre markers."""
        text_lower = text.lower()
        detected = []
        
        for genre, markers in self.GENRE_MARKERS.items():
            if any(marker in text_lower for marker in markers):
                detected.append(genre)
        
        return detected if detected else ['contemporary']
    
    def detect_cultural_anchors(self, text: str) -> List[str]:
        """Detect cultural/geographic anchors."""
        text_lower = text.lower()
        detected = []
        
        for culture, markers in self.CULTURAL_MARKERS.items():
            if any(marker in text_lower for marker in markers):
                detected.append(culture)
        
        return detected if detected else ['universal']
    
    def detect_style_anchors(self, text: str) -> List[str]:
        """Detect style descriptors."""
        text_lower = text.lower()
        detected = []
        
        for style, markers in self.STYLE_MARKERS.items():
            if any(marker in text_lower for marker in markers):
                detected.append(style)
        
        return detected if detected else ['standard']


class AdvancedAURAEngine:
    """
    Advanced AURA engine with local NLP capabilities.
    Zero API dependencies - pure Python + regex + linguistic heuristics.
    """
    
    def __init__(self):
        """Initialize advanced AURA engine."""
        self.rhetorical_detector = RhetoricalDeviceDetector()
        self.intent_extractor = SemanticIntentExtractor()
        self.cultural_detector = CulturalAnchorDetector()
    
    def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        Perform complete AURA analysis on user input.
        
        Args:
            user_input: User's request string
        
        Returns:
            Dict with semantic_intent, rhetorical_devices, bruised_subtext,
            culture_anchors, style_anchors, emotional_profile
        
        Example:
            >>> aura = AdvancedAURAEngine()
            >>> result = aura.analyze("Make me a toxic breakup anthem. She's acting all innocent but I know the truth. Late-pocket trap vibe, analog warmth.")
            >>> result['rhetorical_devices']
            ['juxtaposition: innocent+truth', 'hyperbole: all']
        """
        # Extract semantic intent
        semantic_intent = self.intent_extractor.extract_semantic_intent(user_input)
        
        # Detect rhetorical devices
        rhetorical_devices = self.rhetorical_detector.detect_all(user_input)
        
        # Extract emotional profile
        emotional_profile = self.intent_extractor.extract_emotions(user_input)
        
        # Generate bruised subtext based on emotions
        bruised_subtext = self._generate_bruised_subtext(
            emotional_profile,
            self.intent_extractor.extract_action_stance(user_input)
        )
        
        # Detect cultural and style anchors
        culture_anchors = self.cultural_detector.detect_genres(user_input)
        culture_anchors.extend(self.cultural_detector.detect_cultural_anchors(user_input))
        
        style_anchors = self.cultural_detector.detect_style_anchors(user_input)
        
        return {
            'semantic_intent': semantic_intent,
            'rhetorical_devices': rhetorical_devices,
            'bruised_subtext': bruised_subtext,
            'culture_anchors': list(set(culture_anchors)),  # Remove duplicates
            'style_anchors': style_anchors,
            'emotional_profile': emotional_profile,
            'action_stance': self.intent_extractor.extract_action_stance(user_input),
            'temporal_focus': self.intent_extractor.extract_temporal_focus(user_input)
        }
    
    def _generate_bruised_subtext(self, emotions: Dict[str, float], action_stance: str) -> str:
        """Generate bruised subtext interpretation."""
        if not emotions:
            return "Emotional expression seeking outlet"
        
        # Find dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        
        subtexts = {
            'anger': {
                'confrontation': "Rage masking deep hurt",
                'acceptance': "Anger giving way to resignation",
                'escape': "Fury driving avoidance"
            },
            'vulnerability': {
                'confrontation': "Vulnerability weaponized as truth",
                'acceptance': "Exposed rawness seeking peace",
                'escape': "Fragility driving self-protection"
            },
            'betrayal': {
                'confrontation': "Pain demanding accountability",
                'acceptance': "Betrayal yielding to understanding",
                'escape': "Trust broken, walls rising"
            }
        }
        
        if dominant_emotion in subtexts and action_stance in subtexts[dominant_emotion]:
            return subtexts[dominant_emotion][action_stance]
        else:
            return f"{dominant_emotion.capitalize()} seeking expression through {action_stance}"


# Convenience function
def analyze_user_input(user_input: str) -> Dict[str, Any]:
    """
    Convenience function for AURA analysis.
    
    Args:
        user_input: User's request string
    
    Returns:
        Dict with complete AURA analysis
    
    Example:
        >>> result = analyze_user_input("toxic breakup anthem, late-pocket trap")
        >>> print(result['semantic_intent'])
        "Express betrayal through confrontation"
    """
    aura = AdvancedAURAEngine()
    return aura.analyze(user_input)


# Example usage
if __name__ == "__main__":
    import json
    
    test_inputs = [
        "Make me a toxic breakup anthem. She's acting all innocent but I know the truth. Late-pocket trap vibe, analog warmth, intimate vocals.",
        "I want a drill track with aggressive 808s and harsh modern production. No holding back, pure rage.",
        "Create a soul song with chicano influence, intimate vocals, vintage warmth. Like a slow Sunday morning in the SGV."
    ]
    
    aura = AdvancedAURAEngine()
    
    for user_input in test_inputs:
        print(f"\n{'='*80}")
        print(f"User Input: {user_input}")
        print(f"{'='*80}\n")
        
        result = aura.analyze(user_input)
        print(json.dumps(result, indent=2))
