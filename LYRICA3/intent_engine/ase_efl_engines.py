"""
LYRICA3 Intent Engine - ASE (Strategy Evaluation) & EFL (Lyric Generation)
Part of SLA-113 Toxic Drama Expansion

ASE Purpose:
    Evaluate novelty, cohesion, and impact of creative combinations.
    Apply disruption heuristics (juxtaposition, transplantation, metamorphic blending).
    Zero API dependencies - rule-based scoring with cultural knowledge graph.

EFL Purpose:
    Generate actual lyric lines using template-based system.
    LML tag assignment based on emotional mapping.
    Expandable to local LLM integration (Ollama, llama.cpp).

Integration:
    ASE: Evaluates AURA output → returns strategy recommendation
    EFL: Uses AURA + ASE → generates lyrics with LML tags
"""

import random
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# ASE ENGINE: Strategy Evaluation
# ============================================================================

@dataclass
class GenreCombination:
    """Genre combination for novelty scoring."""
    primary: str
    secondary: Optional[str]
    tertiary: Optional[str]


class CulturalKnowledgeGraph:
    """
    Knowledge graph of genre/style relationships for novelty scoring.
    """
    
    # Genre distance matrix (0.0 = same family, 1.0 = completely different)
    GENRE_DISTANCES = {
        ('trap', 'trap'): 0.0,
        ('trap', 'drill'): 0.2,
        ('trap', 'soul'): 0.6,
        ('trap', 'corrido'): 0.9,
        ('drill', 'soul'): 0.7,
        ('drill', 'corrido'): 0.85,
        ('soul', 'corrido'): 0.5,
        ('chicano', 'trap'): 0.7,
        ('chicano', 'soul'): 0.3,
    }
    
    # Style compatibility matrix (1.0 = highly compatible, 0.0 = conflicting)
    STYLE_COMPATIBILITY = {
        ('analog', 'modern'): 0.4,  # Low compatibility (disruption potential)
        ('analog', 'intimate'): 0.9,  # High compatibility
        ('analog', 'aggressive'): 0.5,
        ('modern', 'aggressive'): 0.9,
        ('modern', 'intimate'): 0.6,
        ('intimate', 'aggressive'): 0.3,  # Low compatibility (disruption potential)
        ('late-pocket', 'aggressive'): 0.7,
        ('late-pocket', 'intimate'): 0.8,
    }
    
    def get_genre_distance(self, genre1: str, genre2: str) -> float:
        """Get distance between two genres (0.0-1.0)."""
        key = tuple(sorted([genre1, genre2]))
        return self.GENRE_DISTANCES.get(key, 0.5)  # Default to medium distance
    
    def get_style_compatibility(self, style1: str, style2: str) -> float:
        """Get compatibility between two styles (0.0-1.0)."""
        key = tuple(sorted([style1, style2]))
        return self.STYLE_COMPATIBILITY.get(key, 0.7)  # Default to medium compatibility


class ASEEngine:
    """
    ASE (Aesthetic Strategy Evaluator) Engine.
    Evaluates novelty, cohesion, and impact of creative combinations.
    """
    
    def __init__(self):
        """Initialize ASE engine."""
        self.knowledge_graph = CulturalKnowledgeGraph()
    
    def evaluate_novelty(self, culture_anchors: List[str], style_anchors: List[str]) -> float:
        """
        Evaluate novelty score (0.0-1.0).
        
        Higher novelty = more unusual genre/style combinations
        
        Args:
            culture_anchors: List of cultural/genre markers
            style_anchors: List of style descriptors
        
        Returns:
            Novelty score (0.0-1.0)
        """
        if len(culture_anchors) < 2:
            return 0.4  # Single genre = medium novelty
        
        # Calculate genre distance (novelty increases with distance)
        total_distance = 0.0
        comparisons = 0
        
        for i in range(len(culture_anchors)):
            for j in range(i + 1, len(culture_anchors)):
                distance = self.knowledge_graph.get_genre_distance(
                    culture_anchors[i],
                    culture_anchors[j]
                )
                total_distance += distance
                comparisons += 1
        
        avg_distance = total_distance / max(comparisons, 1)
        
        # Bonus for unusual style combinations
        style_novelty = 0.0
        if 'analog' in style_anchors and 'modern' in style_anchors:
            style_novelty += 0.3
        if 'intimate' in style_anchors and 'aggressive' in style_anchors:
            style_novelty += 0.3
        
        return min(avg_distance + style_novelty, 1.0)
    
    def evaluate_cohesion(self, culture_anchors: List[str], style_anchors: List[str]) -> float:
        """
        Evaluate cohesion score (0.0-1.0).
        
        Higher cohesion = elements work well together
        
        Args:
            culture_anchors: List of cultural/genre markers
            style_anchors: List of style descriptors
        
        Returns:
            Cohesion score (0.0-1.0)
        """
        if not style_anchors:
            return 0.6  # Default medium cohesion
        
        # Calculate style compatibility
        total_compatibility = 0.0
        comparisons = 0
        
        for i in range(len(style_anchors)):
            for j in range(i + 1, len(style_anchors)):
                compatibility = self.knowledge_graph.get_style_compatibility(
                    style_anchors[i],
                    style_anchors[j]
                )
                total_compatibility += compatibility
                comparisons += 1
        
        if comparisons == 0:
            return 0.7  # Single style = good cohesion
        
        avg_compatibility = total_compatibility / comparisons
        
        # Penalize too many conflicting genres
        if len(culture_anchors) > 3:
            avg_compatibility *= 0.8
        
        return avg_compatibility
    
    def evaluate_impact(self, emotional_profile: Dict[str, float], rhetorical_devices: List[str]) -> float:
        """
        Evaluate expressive impact score (0.0-1.0).
        
        Higher impact = more emotional intensity + rhetorical sophistication
        
        Args:
            emotional_profile: Dict of emotion scores
            rhetorical_devices: List of detected devices
        
        Returns:
            Impact score (0.0-1.0)
        """
        # Base impact from emotional intensity
        emotional_intensity = sum(emotional_profile.values()) / max(len(emotional_profile), 1)
        
        # Bonus for rhetorical sophistication
        rhetorical_bonus = min(len(rhetorical_devices) * 0.1, 0.3)
        
        # Bonus for high-impact emotions
        impact_emotions = ['anger', 'betrayal', 'despair']
        high_impact_bonus = sum(
            emotional_profile.get(emotion, 0) * 0.2
            for emotion in impact_emotions
        )
        
        return min(emotional_intensity + rhetorical_bonus + high_impact_bonus, 1.0)
    
    def determine_disruption_heuristic(self,
                                       novelty_score: float,
                                       cohesion_score: float,
                                       style_anchors: List[str]) -> Optional[str]:
        """
        Determine disruption heuristic based on scores and style anchors.
        
        Returns:
            "juxtaposition", "transplantation", "metamorphic_blending", or None
        """
        # Juxtaposition: high novelty + contrasting styles
        if novelty_score > 0.7:
            if 'analog' in style_anchors and 'modern' in style_anchors:
                return "juxtaposition"
            if 'intimate' in style_anchors and 'aggressive' in style_anchors:
                return "juxtaposition"
        
        # Transplantation: medium novelty + good cohesion (genre blending)
        if 0.5 < novelty_score < 0.8 and cohesion_score > 0.7:
            return "transplantation"
        
        # Metamorphic blending: high cohesion despite novelty
        if novelty_score > 0.6 and cohesion_score > 0.8:
            return "metamorphic_blending"
        
        return None
    
    def generate_strategy_rationale(self,
                                    novelty_score: float,
                                    cohesion_score: float,
                                    impact_score: float,
                                    disruption_heuristic: Optional[str],
                                    culture_anchors: List[str],
                                    style_anchors: List[str]) -> str:
        """Generate human-readable strategy rationale."""
        rationale_parts = []
        
        # Novelty assessment
        if novelty_score > 0.7:
            rationale_parts.append(f"Highly novel combination ({', '.join(culture_anchors[:2])})")
        elif novelty_score > 0.5:
            rationale_parts.append(f"Moderately novel approach")
        else:
            rationale_parts.append(f"Familiar genre territory")
        
        # Disruption heuristic
        if disruption_heuristic == "juxtaposition":
            rationale_parts.append(f"Juxtapose contrasting elements ({', '.join(style_anchors[:2])})")
        elif disruption_heuristic == "transplantation":
            rationale_parts.append(f"Transplant elements across genre boundaries")
        elif disruption_heuristic == "metamorphic_blending":
            rationale_parts.append(f"Seamlessly blend disparate influences")
        
        # Cohesion assessment
        if cohesion_score > 0.8:
            rationale_parts.append("Elements cohere naturally")
        elif cohesion_score < 0.5:
            rationale_parts.append("Requires careful balance to maintain cohesion")
        
        return ". ".join(rationale_parts) + "."
    
    def evaluate(self, aura_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Evaluate AURA output and generate strategy.
        
        Args:
            aura_output: Output from AdvancedAURAEngine.analyze()
        
        Returns:
            Dict with novelty_score, cohesion_score, impact_score,
            disruption_heuristic, strategy_rationale
        """
        culture_anchors = aura_output.get('culture_anchors', [])
        style_anchors = aura_output.get('style_anchors', [])
        emotional_profile = aura_output.get('emotional_profile', {})
        rhetorical_devices = aura_output.get('rhetorical_devices', [])
        
        # Calculate scores
        novelty_score = self.evaluate_novelty(culture_anchors, style_anchors)
        cohesion_score = self.evaluate_cohesion(culture_anchors, style_anchors)
        impact_score = self.evaluate_impact(emotional_profile, rhetorical_devices)
        
        # Determine disruption heuristic
        disruption_heuristic = self.determine_disruption_heuristic(
            novelty_score, cohesion_score, style_anchors
        )
        
        # Generate rationale
        strategy_rationale = self.generate_strategy_rationale(
            novelty_score, cohesion_score, impact_score,
            disruption_heuristic, culture_anchors, style_anchors
        )
        
        return {
            'novelty_score': round(novelty_score, 2),
            'cohesion_score': round(cohesion_score, 2),
            'impact_score': round(impact_score, 2),
            'disruption_heuristic': disruption_heuristic,
            'strategy_rationale': strategy_rationale
        }


# ============================================================================
# EFL ENGINE: Lyric Generation
# ============================================================================

class LyricTemplateEngine:
    """
    Template-based lyric generation system.
    Generates contextually appropriate lyrics based on emotional state and theme.
    """
    
    # Lyric templates organized by theme and emotional state
    LYRIC_TEMPLATES = {
        'toxic_breakup': {
            'anger': [
                "You played {deception_verb}, but I see {truth_noun}",
                "All those {lies_noun}, I know {knowledge_verb}",
                "You can't {escape_verb} from what you did",
                "Not {adverb_finality}, never {adverb_finality}"
            ],
            'vulnerability': [
                "I gave you {love_noun}, you left me {pain_noun}",
                "My heart's {broken_adj}, can't {healing_verb}",
                "I'm {vulnerable_adj}, still {persisting_verb}",
                "Every {time_noun}, I {remember_verb} you"
            ],
            'betrayal': [
                "She plays {innocent_adj}, but I see through",
                "All those {fake_adj} smiles, I know the {truth_noun}",
                "You {betray_verb}, thought I wouldn't know",
                "But I see {clear_adv}, see you for {real_adj}"
            ]
        },
        'love_expression': {
            'vulnerability': [
                "When I'm with you, I feel {safe_adj}",
                "Your {touch_noun} brings me {peace_noun}",
                "I'm {falling_verb}, can't {stop_verb}",
                "You're my {everything_noun}, my {reason_noun}"
            ],
            'hope': [
                "Together we'll {achieve_verb} our {dreams_noun}",
                "Nothing can {stop_verb} us now",
                "I {believe_verb} in what we have",
                "Our {love_noun} will {prevail_verb}"
            ]
        },
        'defiance': {
            'anger': [
                "I won't {submit_verb} to your {control_noun}",
                "You can't {break_verb} my {spirit_noun}",
                "I'm {standing_verb} tall, won't {fall_verb}",
                "This is my {moment_noun}, my {time_noun}"
            ],
            'confidence': [
                "I know my {worth_noun}, know my {power_noun}",
                "No one can {tell_verb} me what I {deserve_verb}",
                "I'm {rising_verb} up, {breaking_verb} free",
                "This is {my_adj} {destiny_noun}"
            ]
        }
    }
    
    # Word banks for template filling
    WORD_BANKS = {
        'deception_verb': ['innocent', 'perfect', 'victim', 'sweet'],
        'truth_noun': ['truth', 'lies', 'game', 'fake'],
        'lies_noun': ['lies', 'games', 'tricks', 'fronts'],
        'knowledge_verb': ['know you', 'see through', 'understand', 'remember'],
        'escape_verb': ['hide', 'run', 'escape', 'avoid'],
        'adverb_finality': ['anymore', 'again', 'this time', 'now'],
        'love_noun': ['love', 'heart', 'soul', 'everything'],
        'pain_noun': ['broken', 'empty', 'bleeding', 'numb'],
        'broken_adj': ['broken', 'shattered', 'torn', 'damaged'],
        'healing_verb': ['heal', 'mend', 'recover', 'move on'],
        'vulnerable_adj': ['vulnerable', 'exposed', 'raw', 'fragile'],
        'persisting_verb': ['fighting', 'surviving', 'standing', 'breathing'],
        'innocent_adj': ['innocent', 'perfect', 'clean', 'sweet'],
        'fake_adj': ['fake', 'false', 'plastic', 'empty'],
        'betray_verb': ['betrayed', 'lied', 'cheated', 'deceived'],
        'clear_adv': ['clearly', 'finally', 'truly', 'really'],
        'real_adj': ['real', 'who you are', 'what you did', 'the truth'],
        'time_noun': ['night', 'day', 'moment', 'second'],
        'remember_verb': ['remember', 'think of', 'miss', 'see'],
        'safe_adj': ['safe', 'whole', 'complete', 'alive'],
        'touch_noun': ['touch', 'voice', 'presence', 'love'],
        'peace_noun': ['peace', 'comfort', 'calm', 'warmth'],
        'falling_verb': ['falling', 'drowning', 'lost', 'gone'],
        'stop_verb': ['stop', 'fight it', 'deny it', 'hide it'],
        'everything_noun': ['everything', 'world', 'light', 'reason'],
        'reason_noun': ['reason', 'purpose', 'home', 'destiny'],
        'achieve_verb': ['achieve', 'reach', 'build', 'create'],
        'dreams_noun': ['dreams', 'future', 'goals', 'vision'],
        'believe_verb': ['believe', 'trust', 'know', 'feel'],
        'prevail_verb': ['prevail', 'survive', 'win', 'last'],
        'submit_verb': ['submit', 'bow', 'break', 'surrender'],
        'control_noun': ['control', 'rules', 'chains', 'games'],
        'break_verb': ['break', 'crush', 'destroy', 'defeat'],
        'spirit_noun': ['spirit', 'soul', 'fire', 'will'],
        'standing_verb': ['standing', 'rising', 'fighting', 'pushing'],
        'fall_verb': ['fall', 'break', 'give up', 'quit'],
        'moment_noun': ['moment', 'time', 'turn', 'chance'],
        'worth_noun': ['worth', 'value', 'power', 'strength'],
        'power_noun': ['power', 'fire', 'truth', 'light'],
        'tell_verb': ['tell', 'show', 'teach', 'convince'],
        'deserve_verb': ['deserve', 'want', 'need', 'am'],
        'rising_verb': ['rising', 'soaring', 'flying', 'breaking'],
        'breaking_verb': ['breaking', 'tearing', 'bursting', 'shattering'],
        'my_adj': ['my', 'our', 'the', 'this'],
        'destiny_noun': ['destiny', 'story', 'life', 'path']
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize lyric engine."""
        if seed is not None:
            random.seed(seed)
    
    def determine_theme(self, aura_output: Dict[str, Any]) -> str:
        """Determine lyric theme from AURA output."""
        emotional_profile = aura_output.get('emotional_profile', {})
        action_stance = aura_output.get('action_stance', 'neutral')
        
        if 'betrayal' in emotional_profile or 'anger' in emotional_profile:
            return 'toxic_breakup'
        elif action_stance == 'confrontation':
            return 'defiance'
        elif 'love' in emotional_profile or 'hope' in emotional_profile:
            return 'love_expression'
        else:
            return 'toxic_breakup'  # Default
    
    def select_emotion_for_template(self, emotional_profile: Dict[str, float], theme: str) -> str:
        """Select best emotion for template selection."""
        if not emotional_profile:
            return list(self.LYRIC_TEMPLATES.get(theme, {}).keys())[0]
        
        # Find emotion that exists in both emotional_profile and templates
        available_emotions = self.LYRIC_TEMPLATES.get(theme, {}).keys()
        
        for emotion in emotional_profile.keys():
            if emotion in available_emotions:
                return emotion
        
        # Fallback to first available emotion in templates
        return list(available_emotions)[0] if available_emotions else 'vulnerability'
    
    def fill_template(self, template: str) -> str:
        """Fill template with words from word banks."""
        filled = template
        
        # Find all placeholders {word_type}
        placeholders = re.findall(r'\{([a-z_]+)\}', template)
        
        for placeholder in placeholders:
            if placeholder in self.WORD_BANKS:
                word = random.choice(self.WORD_BANKS[placeholder])
                filled = filled.replace(f'{{{placeholder}}}', word, 1)
        
        return filled
    
    def assign_lml_tag(self, line: str, vulnerability_level: float, line_index: int, total_lines: int) -> str:
        """Assign appropriate LML tag based on context."""
        # First line often has vocal_fry (establishing tone)
        if line_index == 0 and vulnerability_level > 0.6:
            return "<vocal_fry>"
        
        # Peak emotional moment (middle lines) gets emotional_crack
        if line_index == total_lines // 2 and vulnerability_level > 0.7:
            return "<emotional_crack>"
        
        # Last line often has adaptive_inhale (finality, breath)
        if line_index == total_lines - 1:
            return "<adaptive_inhale>"
        
        # Proximity effect for intimate moments
        if vulnerability_level > 0.8 and random.random() < 0.3:
            return "<proximity_effect>"
        
        return ""
    
    def generate_lyrics(self,
                       aura_output: Dict[str, Any],
                       ase_output: Dict[str, Any],
                       num_lines: int = 4) -> List[Dict[str, str]]:
        """
        Generate lyrics with LML tags.
        
        Args:
            aura_output: AURA analysis output
            ase_output: ASE evaluation output
            num_lines: Number of lyric lines to generate
        
        Returns:
            List of dicts with 'line' and 'lml_trigger'
        """
        theme = self.determine_theme(aura_output)
        emotional_profile = aura_output.get('emotional_profile', {})
        vulnerability_level = max(emotional_profile.values()) if emotional_profile else 0.7
        
        # Select emotion for templates
        emotion = self.select_emotion_for_template(emotional_profile, theme)
        
        # Get templates
        templates = self.LYRIC_TEMPLATES.get(theme, {}).get(emotion, [])
        
        if not templates:
            # Fallback generic templates
            templates = [
                "I'm feeling {vulnerable_adj}, can't {escape_verb}",
                "You left me {broken_adj}, heart won't {healing_verb}",
                "But I'm {standing_verb}, won't {fall_verb}",
                "This is my {moment_noun}, my {time_noun}"
            ]
        
        # Generate lines
        lyrics = []
        for i in range(min(num_lines, len(templates) * 2)):  # Allow repetition
            template = templates[i % len(templates)]
            line = self.fill_template(template)
            lml_tag = self.assign_lml_tag(line, vulnerability_level, i, num_lines)
            
            lyrics.append({
                'line': line,
                'lml_trigger': lml_tag
            })
        
        return lyrics


class EFLEngine:
    """
    EFL (Emotional/Lyrical Framework) Engine.
    Generates emotional mapping and lyric strategy with actual lyric lines.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize EFL engine."""
        self.lyric_engine = LyricTemplateEngine(seed=seed)
    
    def generate(self,
                 aura_output: Dict[str, Any],
                 ase_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point: Generate EFL output.
        
        Args:
            aura_output: AURA analysis output
            ase_output: ASE evaluation output
        
        Returns:
            Dict with emotional_mapping, lml_tags, lyric_strategy,
            vulnerability_level, generated_lyrics
        """
        emotional_profile = aura_output.get('emotional_profile', {})
        style_anchors = aura_output.get('style_anchors', [])
        disruption_heuristic = ase_output.get('disruption_heuristic')
        
        # Calculate vulnerability level
        vulnerability_level = max(emotional_profile.values()) if emotional_profile else 0.7
        
        # Determine LML tags based on emotional profile
        lml_tags = []
        if vulnerability_level > 0.7:
            lml_tags.extend(['<vocal_fry>', '<emotional_crack>'])
        if 'intimate' in style_anchors:
            lml_tags.append('<proximity_effect>')
        if vulnerability_level > 0.5:
            lml_tags.append('<adaptive_inhale>')
        
        # Generate lyric strategy
        if disruption_heuristic == "juxtaposition":
            lyric_strategy = "Contrast defensive bravado with moments of raw vulnerability"
        elif disruption_heuristic == "metamorphic_blending":
            lyric_strategy = "Seamlessly blend cultural influences with emotional authenticity"
        else:
            lyric_strategy = "Maintain consistent emotional tone with subtle intensity shifts"
        
        # Generate actual lyrics
        generated_lyrics = self.lyric_engine.generate_lyrics(aura_output, ase_output, num_lines=4)
        
        return {
            'emotional_mapping': emotional_profile,
            'lml_tags': lml_tags,
            'lyric_strategy': lyric_strategy,
            'vulnerability_level': vulnerability_level,
            'generated_lyrics': generated_lyrics
        }


# Example usage
if __name__ == "__main__":
    import json
    from advanced_aura_engine import AdvancedAURAEngine
    
    # Test ASE + EFL
    aura_engine = AdvancedAURAEngine()
    ase_engine = ASEEngine()
    efl_engine = EFLEngine(seed=42)
    
    test_input = "Make me a toxic breakup anthem. She's acting all innocent but I know the truth. Late-pocket trap vibe, analog warmth, intimate vocals."
    
    print(f"\n{'='*80}")
    print(f"User Input: {test_input}")
    print(f"{'='*80}\n")
    
    # AURA
    aura_output = aura_engine.analyze(test_input)
    print("AURA Output:")
    print(json.dumps(aura_output, indent=2))
    
    # ASE
    ase_output = ase_engine.evaluate(aura_output)
    print("\nASE Output:")
    print(json.dumps(ase_output, indent=2))
    
    # EFL
    efl_output = efl_engine.generate(aura_output, ase_output)
    print("\nEFL Output:")
    print(json.dumps(efl_output, indent=2))
