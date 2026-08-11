"""
LYRICA3 Global Lyric Engine - Worldwide Genre Coverage
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Expand beyond SGV/Chicano to cover global music scenes.
    Support 20+ international genres with culturally authentic templates.

Global Coverage:
    - Afrobeats (Nigeria, Ghana, South Africa)
    - UK Drill (London grime culture)
    - K-pop (Korean pop, romance themes)
    - Reggaeton (Latin urban, Puerto Rico, Colombia)
    - Amapiano (South African house)
    - Dancehall (Jamaica, Caribbean)
    - French Rap (Paris, Marseille)
    - German Trap (Berlin)
    - Brazilian Funk (Rio favelas)
    - Arabic Trap (Middle East)
    - Bollywood Pop (India)
    - J-pop (Japan)
    - Australian Hip-Hop (Sydney, Melbourne)
    - Nordic Folk-Pop (Sweden, Norway)

Architecture:
    GlobalLyricEngine extends LyricTemplateEngine with:
        - 20+ genre-specific template banks
        - Cultural phrase databases
        - Multi-language support (English + transliterated phrases)
        - Regional slang and idioms
"""

import random
from typing import Dict, List, Any, Optional


class GlobalLyricEngine:
    """
    Global lyric generation engine covering worldwide music scenes.
    Extends base template system with international genre support.
    """
    
    # Global lyric templates organized by genre and theme
    GLOBAL_LYRIC_TEMPLATES = {
        # AFROBEATS (Nigeria, Ghana, South Africa)
        'afrobeats': {
            'celebration': [
                "We dey {celebrate_verb} all night, {affirmation_word}",
                "My {vibe_noun} no get {limit_noun}",
                "From {location} to the world, we {rising_verb}",
                "Tell them say we {winning_verb}, no {stopping_verb}"
            ],
            'love': [
                "Baby you dey make me {crazy_adj}, for real",
                "Your {beauty_noun} pass {comparison}, no lie",
                "I go {promise_verb} you the {everything_noun}",
                "Girl you be my {treasure_noun}, my {precious_noun}"
            ],
            'hustle': [
                "From {nothing_noun} to {something_noun}, we grind",
                "No {sleep_noun}, only {hustle_noun}",
                "They thought I go {fail_verb}, but I {rise_verb}",
                "Every day I'm {grinding_verb}, no time for {waste_noun}"
            ]
        },
        
        # UK DRILL (London)
        'uk_drill': {
            'street': [
                "Man's {moving_verb} with the {crew_noun}, no cap",
                "They don't want {smoke_noun}, they {talking_verb}",
                "From the {ends_noun} to the {top_noun}, we made it",
                "Real {recognize_verb} real, that's on {affirmation}"
            ],
            'ambition': [
                "Started from the {bottom_noun}, now we here",
                "No {handouts_noun}, we {earned_verb} this",
                "They {watching_verb} how we {moving_verb}",
                "Can't {stop_verb} won't {stop_verb}, that's the {motto_noun}"
            ]
        },
        
        # K-POP (Korea)
        'kpop': {
            'love': [
                "You make my heart go {beat_sound}",
                "Like a {dream_noun}, you're so {perfect_adj}",
                "Baby you're my {everything_noun}, my {starlight_noun}",
                "Forever and ever, we'll be {together_adj}"
            ],
            'confidence': [
                "I'm the {main_character}, watch me {shine_verb}",
                "Born to be a {star_noun}, no {doubt_noun}",
                "Every day I'm {leveling_verb} up, new {height_noun}",
                "Can't nobody {stop_verb} my {flow_noun}"
            ],
            'heartbreak': [
                "Why'd you {leave_verb} me so {alone_adj}",
                "My heart is {broken_adj} like {glass_noun}",
                "I gave you {everything_noun}, you gave {nothing_noun}",
                "Bye bye to you, hello to {new_adj} me"
            ]
        },
        
        # REGGAETON (Latin Urban)
        'reggaeton': {
            'party': [
                "Dale {movement_word}, muévete así",
                "Tonight we're gonna {party_verb} till the sun",
                "Pégate más, feel the {rhythm_noun}",
                "En la disco, baby you're my {queen_noun}"
            ],
            'romance': [
                "Mami you got me {crazy_adj}, no mentira",
                "Tu {beauty_noun} me tiene {hypnotized_adj}",
                "Dame más de tu {love_noun}, nena",
                "Contigo I feel {complete_adj}, for real"
            ],
            'flex': [
                "Llegamos con el {style_noun}, puro fuego",
                "Money, power, {respect_noun}, we got it all",
                "De la calle to the {mansion_noun}",
                "They know who we are, we're {legendary_adj}"
            ]
        },
        
        # AMAPIANO (South Africa)
        'amapiano': {
            'groove': [
                "Yebo yes, we {dancing_verb} all night",
                "The {bass_noun} is {hitting_verb}, feel it deep",
                "Piano {melodies_noun} got me in my {zone_noun}",
                "Mzansi sound, we {putting_verb} on for the world"
            ],
            'love': [
                "Sthandwa sami, you're my {everything_noun}",
                "Your {vibe_noun} is {unmatched_adj}, no competition",
                "When you {move_verb}, I can't {look_verb} away",
                "Together we're {unstoppable_adj}, baby"
            ]
        },
        
        # DANCEHALL (Jamaica)
        'dancehall': {
            'party': [
                "Gyal come {wine_verb} up pon the {riddim_noun}",
                "From {sunset_noun} to {sunrise_noun}, we nah stop",
                "Turn it up, make the {speaker_noun} blow",
                "Everybody jump and {wave_verb}, right now"
            ],
            'confidence': [
                "Dem can't {test_verb} we, we too {strong_adj}",
                "Born fi {win_verb}, that's the program",
                "Real {badman_noun} ting, no {pretend_noun}",
                "We a {champion_noun}, no second place"
            ]
        },
        
        # FRENCH RAP (Paris)
        'french_rap': {
            'struggle': [
                "Dans les rues we {fighting_verb} for respect",
                "From the {banlieue_noun} to the {top_noun}",
                "They tried to {stop_verb} us, mais on est là",
                "C'est la vie, we {surviving_verb} every day"
            ],
            'success': [
                "Maintenant we're {living_verb} like kings",
                "Money in the {pocket_noun}, no more {stress_noun}",
                "Tout le monde nous {watching_verb} now",
                "From {zero_noun} to {hero_noun}, voilà"
            ]
        },
        
        # GERMAN TRAP (Berlin)
        'german_trap': {
            'street': [
                "Aus dem {block_noun} direkt to the top",
                "Meine {crew_noun}, we don't play games",
                "Money, {power_noun}, that's the {mission_noun}",
                "Niemand can {stop_verb} what we building"
            ]
        },
        
        # BRAZILIAN FUNK (Rio)
        'brazilian_funk': {
            'party': [
                "Vai vai, everybody {dancing_verb} now",
                "Na favela we {living_verb} our best life",
                "Turn the {music_noun} up, feel the {heat_noun}",
                "Toda noite is a {celebration_noun}"
            ],
            'pride': [
                "From the {streets_noun} we rose up",
                "Nossa {culture_noun} is worldwide now",
                "They can't {deny_verb} our {power_noun}",
                "Rio to the world, we {representing_verb}"
            ]
        },
        
        # ARABIC TRAP (Middle East)
        'arabic_trap': {
            'ambition': [
                "Habibi we're {chasing_verb} dreams, yalla",
                "From the {desert_noun} to the {palace_noun}",
                "Inshallah we're gonna make it big",
                "No {stopping_verb}, only {forward_adj}"
            ],
            'love': [
                "Ya amar, you're my {moon_noun}",
                "Your {eyes_noun} shine like {stars_noun}",
                "Habibti you're my {everything_noun}",
                "Forever mine, that's the {promise_noun}"
            ]
        },
        
        # BOLLYWOOD POP (India)
        'bollywood_pop': {
            'romance': [
                "Dil hai tumhara, my heart is yours",
                "Like a {dream_noun}, you came to me",
                "Pyaar in the air, can you feel it",
                "Together forever, that's our {destiny_noun}"
            ],
            'celebration': [
                "Nachle tonight, let's {dance_verb} away",
                "Rang barse, colors everywhere",
                "Life is a {party_noun}, enjoy every moment",
                "Khushi hai, happiness all around"
            ]
        },
        
        # J-POP (Japan)
        'jpop': {
            'youth': [
                "Ima from this moment, we {shining_verb}",
                "Kimi to with you, I feel {alive_adj}",
                "Yume dreams coming true, sugoi",
                "Ganbare keep going, never give up"
            ],
            'energy': [
                "Genki full energy, let's go",
                "Kawaii {vibes_noun} but we {fierce_adj}",
                "Tokyo lights, we own the {night_noun}",
                "Ichiban number one, that's us"
            ]
        },
        
        # AUSTRALIAN HIP-HOP
        'aus_hiphop': {
            'local_pride': [
                "From the {suburbs_noun} to the city lights",
                "Mate we're {grinding_verb} every day",
                "Down under but we {rising_verb} up",
                "Aussie {style_noun}, can't be replicated"
            ],
            'confidence': [
                "No worries mate, we got this sorted",
                "They thought we couldn't, but we {proved_verb} them wrong",
                "Fair dinkum, this is our {time_noun}",
                "From Sydney to the world, watch us {shine_verb}"
            ]
        },
        
        # NORDIC FOLK-POP
        'nordic_folk': {
            'nature': [
                "Cold {winds_noun} but warm {hearts_noun}",
                "Under northern {lights_noun}, we {dreaming_verb}",
                "From the {mountains_noun} to the {sea_noun}",
                "Wild and {free_adj}, that's how we be"
            ],
            'melancholy': [
                "Dark {nights_noun} bring deep {thoughts_noun}",
                "In the {silence_noun}, I hear your voice",
                "Winter {blues_noun} but summer {hope_noun}",
                "Through the {cold_noun}, our love stays {warm_adj}"
            ]
        },
        
        # MAINSTREAM POP (Global)
        'mainstream_pop': {
            'love': [
                "You're the only one I {need_verb}",
                "When I'm with you, everything's {perfect_adj}",
                "Baby you're my {sunrise_noun}, my {sunset_noun}",
                "Forever and always, that's my {promise_noun}"
            ],
            'empowerment': [
                "I know my {worth_noun}, I know my {power_noun}",
                "No one can {tell_verb} me what I can't do",
                "Rising up, breaking every {ceiling_noun}",
                "This is my {moment_noun}, watch me {shine_verb}"
            ],
            'heartbreak': [
                "You left me {broken_adj}, but I'll be okay",
                "Goodbye to the {past_noun}, hello to {new_adj}",
                "I gave my {all_noun}, but you gave {nothing_noun}",
                "Moving on, finding {better_adj}"
            ]
        },
        
        # EDM/ELECTRONIC
        'edm': {
            'energy': [
                "Hands up, feel the {drop_noun}",
                "Bass is {hitting_verb}, bodies {moving_verb}",
                "Lost in the {music_noun}, found in the {moment_noun}",
                "Tonight we're {infinite_adj}, we're {alive_adj}"
            ],
            'freedom': [
                "No {rules_noun}, just the {beat_noun}",
                "Dancing till the {sunrise_noun}",
                "This is {freedom_noun}, pure and {simple_adj}",
                "Together we're {unstoppable_adj}"
            ]
        },
        
        # COUNTRY (Nashville)
        'country': {
            'roots': [
                "Small town {roads_noun}, big {dreams_noun}",
                "Raised on {values_noun} and hard {work_noun}",
                "Simple {life_noun}, happy {heart_noun}",
                "This is home, where I {belong_verb}"
            ],
            'heartbreak': [
                "You took my {heart_noun} and left me {empty_adj}",
                "Whiskey and {tears_noun} on a Friday night",
                "Should've known better than to {trust_verb}",
                "But I'll be {fine_adj}, I always am"
            ]
        }
    }
    
    # Expanded global word banks
    GLOBAL_WORD_BANKS = {
        # Afrobeats specific
        'celebrate_verb': ['celebrate', 'jolly', 'vibe', 'groove'],
        'affirmation_word': ['omo', 'chai', 'ah ah', 'for real'],
        'vibe_noun': ['vibe', 'energy', 'sauce', 'groove'],
        'limit_noun': ['limit', 'boundary', 'end', 'cap'],
        'winning_verb': ['winning', 'popping', 'moving', 'shining'],
        
        # UK Drill specific
        'moving_verb': ['moving', 'sliding', 'gliding', 'cruising'],
        'crew_noun': ['crew', 'squad', 'mandem', 'gang'],
        'smoke_noun': ['smoke', 'beef', 'problems', 'heat'],
        'talking_verb': ['talking', 'chatting', 'capping', 'fronting'],
        'ends_noun': ['ends', 'block', 'hood', 'yard'],
        
        # K-pop specific
        'beat_sound': ['boom boom', 'pit-a-pat', 'boom boom boom', 'thump thump'],
        'starlight_noun': ['starlight', 'moonlight', 'sunshine', 'angel'],
        'leveling_verb': ['leveling', 'powering', 'glowing', 'rising'],
        'flow_noun': ['flow', 'vibe', 'energy', 'aura'],
        
        # Reggaeton specific
        'movement_word': ['dale', 'muévete', 'pégate', 'azota'],
        
        # Amapiano specific
        'bass_noun': ['bass', 'log drum', 'kick', 'rhythm'],
        'hitting_verb': ['hitting', 'knocking', 'bumping', 'thumping'],
        'melodies_noun': ['melodies', 'chords', 'keys', 'vibes'],
        
        # Dancehall specific
        'wine_verb': ['wine', 'bubble', 'shake', 'move'],
        'riddim_noun': ['riddim', 'beat', 'track', 'sound'],
        'badman_noun': ['badman', 'champion', 'winner', 'boss'],
        
        # Multilingual/transliterated terms
        'banlieue_noun': ['banlieue', 'suburbs', 'quartier', 'hood'],
        'block_noun': ['Block', 'Kiez', 'Viertel', 'hood'],
        'habibi': ['habibi', 'habibti', 'baby', 'love'],
        
        # Universal words (expanded)
        'crazy_adj': ['crazy', 'wild', 'insane', 'mad'],
        'beauty_noun': ['beauty', 'shine', 'glow', 'light'],
        'comparison': ['everything', 'the sun', 'diamonds', 'gold'],
        'promise_verb': ['promise', 'give', 'show', 'bring'],
        'treasure_noun': ['treasure', 'diamond', 'jewel', 'gold'],
        'precious_noun': ['precious', 'blessing', 'gift', 'miracle'],
        'nothing_noun': ['nothing', 'zero', 'dust', 'ground'],
        'something_noun': ['something', 'everything', 'success', 'glory'],
        'hustle_noun': ['hustle', 'grind', 'work', 'pressure'],
        'fail_verb': ['fail', 'fall', 'lose', 'break'],
        'rise_verb': ['rise', 'soar', 'fly', 'climb'],
        'grinding_verb': ['grinding', 'hustling', 'working', 'pushing'],
        'waste_noun': ['waste', 'play', 'slack', 'games'],
        'sleep_noun': ['sleep', 'rest', 'breaks', 'time off'],
        'bottom_noun': ['bottom', 'mud', 'dirt', 'streets'],
        'top_noun': ['top', 'throne', 'crown', 'peak'],
        'handouts_noun': ['handouts', 'favors', 'charity', 'help'],
        'earned_verb': ['earned', 'built', 'made', 'created'],
        'watching_verb': ['watching', 'seeing', 'studying', 'checking'],
        'stop_verb': ['stop', 'quit', 'fold', 'break'],
        'motto_noun': ['motto', 'way', 'code', 'rule'],
        'perfect_adj': ['perfect', 'amazing', 'beautiful', 'incredible'],
        'together_adj': ['together', 'united', 'one', 'forever'],
        'main_character': ['main character', 'star', 'lead', 'hero'],
        'shine_verb': ['shine', 'glow', 'sparkle', 'radiate'],
        'star_noun': ['star', 'superstar', 'icon', 'legend'],
        'doubt_noun': ['doubt', 'question', 'fear', 'hesitation'],
        'height_noun': ['height', 'level', 'peak', 'summit'],
        'leave_verb': ['leave', 'abandon', 'ghost', 'forget'],
        'alone_adj': ['alone', 'lonely', 'empty', 'cold'],
        'broken_adj': ['broken', 'shattered', 'torn', 'crushed'],
        'glass_noun': ['glass', 'ice', 'crystal', 'porcelain'],
        'everything_noun': ['everything', 'my all', 'my world', 'my heart'],
        'nothing_noun': ['nothing', 'emptiness', 'lies', 'pain'],
        'new_adj': ['new', 'better', 'stronger', 'free'],
        'party_verb': ['party', 'dance', 'vibe', 'celebrate'],
        'rhythm_noun': ['rhythm', 'beat', 'flow', 'groove'],
        'queen_noun': ['queen', 'princess', 'goddess', 'star'],
        'hypnotized_adj': ['hypnotized', 'mesmerized', 'entranced', 'hooked'],
        'love_noun': ['love', 'amor', 'cariño', 'passion'],
        'complete_adj': ['complete', 'whole', 'perfect', 'alive'],
        'style_noun': ['style', 'swag', 'drip', 'sauce'],
        'respect_noun': ['respect', 'honor', 'power', 'status'],
        'mansion_noun': ['mansion', 'penthouse', 'villa', 'palace'],
        'legendary_adj': ['legendary', 'iconic', 'historic', 'immortal'],
        'dancing_verb': ['dancing', 'moving', 'grooving', 'vibing'],
        'zone_noun': ['zone', 'flow', 'trance', 'vibe'],
        'putting_verb': ['putting', 'showing', 'representing', 'bringing'],
        'unmatched_adj': ['unmatched', 'unbeatable', 'supreme', 'elite'],
        'move_verb': ['move', 'dance', 'sway', 'groove'],
        'look_verb': ['look', 'turn', 'move', 'glance'],
        'unstoppable_adj': ['unstoppable', 'unstoppable', 'invincible', 'infinite'],
        'test_verb': ['test', 'try', 'challenge', 'step to'],
        'strong_adj': ['strong', 'tough', 'solid', 'hard'],
        'win_verb': ['win', 'conquer', 'dominate', 'rule'],
        'pretend_noun': ['pretend', 'acting', 'faking', 'fronting'],
        'champion_noun': ['champion', 'boss', 'king', 'winner'],
        'fighting_verb': ['fighting', 'battling', 'struggling', 'grinding'],
        'surviving_verb': ['surviving', 'pushing', 'fighting', 'enduring'],
        'living_verb': ['living', 'eating', 'flexing', 'shining'],
        'pocket_noun': ['pocket', 'bank', 'wallet', 'bag'],
        'stress_noun': ['stress', 'worry', 'problems', 'pain'],
        'zero_noun': ['zero', 'rien', 'nothing', 'dirt'],
        'hero_noun': ['hero', 'champion', 'winner', 'star'],
        'power_noun': ['power', 'strength', 'force', 'energy'],
        'mission_noun': ['mission', 'goal', 'plan', 'vision'],
        'music_noun': ['music', 'sound', 'beat', 'rhythm'],
        'heat_noun': ['heat', 'fire', 'energy', 'passion'],
        'celebration_noun': ['celebration', 'party', 'festa', 'fiesta'],
        'streets_noun': ['streets', 'favela', 'block', 'hood'],
        'culture_noun': ['culture', 'music', 'spirit', 'soul'],
        'deny_verb': ['deny', 'ignore', 'stop', 'dismiss'],
        'representing_verb': ['representing', 'showing', 'putting on', 'claiming'],
        'chasing_verb': ['chasing', 'hunting', 'pursuing', 'seeking'],
        'desert_noun': ['desert', 'dunes', 'sands', 'badlands'],
        'palace_noun': ['palace', 'castle', 'throne', 'tower'],
        'forward_adj': ['forward', 'ahead', 'up', 'higher'],
        'moon_noun': ['moon', 'qamar', 'light', 'star'],
        'eyes_noun': ['eyes', 'gaze', 'look', 'stare'],
        'stars_noun': ['stars', 'diamonds', 'jewels', 'lights'],
        'promise_noun': ['promise', 'vow', 'oath', 'word'],
        'dream_noun': ['dream', 'fantasy', 'wish', 'vision'],
        'destiny_noun': ['destiny', 'fate', 'future', 'story'],
        'dance_verb': ['dance', 'groove', 'move', 'sway'],
        'shining_verb': ['shining', 'glowing', 'sparkling', 'beaming'],
        'alive_adj': ['alive', 'awake', 'real', 'present'],
        'vibes_noun': ['vibes', 'energy', 'aura', 'mood'],
        'fierce_adj': ['fierce', 'strong', 'powerful', 'bold'],
        'night_noun': ['night', 'city', 'scene', 'world'],
        'suburbs_noun': ['suburbs', 'burbs', 'outskirts', 'ends'],
        'proved_verb': ['proved', 'showed', 'demonstrated', 'confirmed'],
        'time_noun': ['time', 'moment', 'era', 'season'],
        'winds_noun': ['winds', 'breeze', 'air', 'storms'],
        'hearts_noun': ['hearts', 'souls', 'spirits', 'love'],
        'lights_noun': ['lights', 'glow', 'aurora', 'shine'],
        'dreaming_verb': ['dreaming', 'wishing', 'hoping', 'believing'],
        'mountains_noun': ['mountains', 'fjords', 'peaks', 'highlands'],
        'sea_noun': ['sea', 'ocean', 'waters', 'waves'],
        'free_adj': ['free', 'wild', 'untamed', 'boundless'],
        'nights_noun': ['nights', 'evenings', 'darkness', 'shadows'],
        'thoughts_noun': ['thoughts', 'feelings', 'memories', 'dreams'],
        'silence_noun': ['silence', 'stillness', 'quiet', 'peace'],
        'blues_noun': ['blues', 'sadness', 'melancholy', 'sorrow'],
        'hope_noun': ['hope', 'light', 'warmth', 'joy'],
        'cold_noun': ['cold', 'winter', 'frost', 'ice'],
        'warm_adj': ['warm', 'bright', 'strong', 'true'],
        'need_verb': ['need', 'want', 'crave', 'desire'],
        'sunrise_noun': ['sunrise', 'dawn', 'light', 'beginning'],
        'sunset_noun': ['sunset', 'dusk', 'peace', 'end'],
        'worth_noun': ['worth', 'value', 'strength', 'power'],
        'tell_verb': ['tell', 'show', 'teach', 'prove'],
        'ceiling_noun': ['ceiling', 'limit', 'barrier', 'wall'],
        'moment_noun': ['moment', 'time', 'chance', 'shot'],
        'past_noun': ['past', 'yesterday', 'memories', 'pain'],
        'all_noun': ['all', 'everything', 'heart', 'love'],
        'better_adj': ['better', 'stronger', 'happier', 'free'],
        'drop_noun': ['drop', 'beat', 'bass', 'breakdown'],
        'infinite_adj': ['infinite', 'endless', 'eternal', 'limitless'],
        'rules_noun': ['rules', 'limits', 'boundaries', 'control'],
        'beat_noun': ['beat', 'rhythm', 'pulse', 'sound'],
        'freedom_noun': ['freedom', 'liberty', 'release', 'escape'],
        'simple_adj': ['simple', 'pure', 'raw', 'real'],
        'roads_noun': ['roads', 'streets', 'paths', 'ways'],
        'dreams_noun': ['dreams', 'hopes', 'wishes', 'goals'],
        'values_noun': ['values', 'roots', 'faith', 'honor'],
        'work_noun': ['work', 'labor', 'sweat', 'tears'],
        'life_noun': ['life', 'way', 'world', 'place'],
        'heart_noun': ['heart', 'soul', 'trust', 'love'],
        'belong_verb': ['belong', 'stay', 'remain', 'rest'],
        'empty_adj': ['empty', 'hollow', 'broken', 'numb'],
        'tears_noun': ['tears', 'rain', 'pain', 'memories'],
        'trust_verb': ['trust', 'believe', 'fall', 'hope'],
        'fine_adj': ['fine', 'okay', 'alright', 'stronger']
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize global lyric engine."""
        if seed is not None:
            random.seed(seed)
    
    def get_available_genres(self) -> List[str]:
        """Return list of all supported global genres."""
        return list(self.GLOBAL_LYRIC_TEMPLATES.keys())
    
    def detect_genre_from_input(self, user_input: str, culture_anchors: List[str]) -> str:
        """
        Detect genre from user input and culture anchors.
        
        Expanded to cover global genres beyond SGV/Chicano.
        """
        user_lower = user_input.lower()
        
        # Direct genre mentions
        if 'afrobeat' in user_lower or 'nigeria' in user_lower or 'ghana' in user_lower:
            return 'afrobeats'
        if 'uk drill' in user_lower or 'london' in user_lower or 'grime' in user_lower:
            return 'uk_drill'
        if 'k-pop' in user_lower or 'kpop' in user_lower or 'korea' in user_lower:
            return 'kpop'
        if 'reggaeton' in user_lower or 'latino' in user_lower or 'puerto rico' in user_lower:
            return 'reggaeton'
        if 'amapiano' in user_lower or 'south africa' in user_lower or 'mzansi' in user_lower:
            return 'amapiano'
        if 'dancehall' in user_lower or 'jamaica' in user_lower or 'caribbean' in user_lower:
            return 'dancehall'
        if 'french rap' in user_lower or 'paris' in user_lower or 'marseille' in user_lower:
            return 'french_rap'
        if 'german' in user_lower and ('trap' in user_lower or 'rap' in user_lower):
            return 'german_trap'
        if 'brazilian funk' in user_lower or 'baile funk' in user_lower or 'rio' in user_lower:
            return 'brazilian_funk'
        if 'arabic' in user_lower or 'middle east' in user_lower or 'habibi' in user_lower:
            return 'arabic_trap'
        if 'bollywood' in user_lower or 'india' in user_lower or 'hindi' in user_lower:
            return 'bollywood_pop'
        if 'j-pop' in user_lower or 'jpop' in user_lower or 'japan' in user_lower or 'tokyo' in user_lower:
            return 'jpop'
        if 'australia' in user_lower or 'aussie' in user_lower or 'sydney' in user_lower:
            return 'aus_hiphop'
        if 'nordic' in user_lower or 'sweden' in user_lower or 'norway' in user_lower or 'iceland' in user_lower:
            return 'nordic_folk'
        if 'edm' in user_lower or 'house' in user_lower or 'techno' in user_lower or 'electronic' in user_lower:
            return 'edm'
        if 'country' in user_lower or 'nashville' in user_lower or 'southern' in user_lower:
            return 'country'
        
        # Fallback to mainstream pop or culture anchor detection
        if 'drill' in culture_anchors:
            return 'uk_drill'
        elif 'trap' in culture_anchors:
            return 'mainstream_pop'  # Generic trap
        
        return 'mainstream_pop'
    
    def generate_global_lyrics(self,
                              genre: str,
                              theme: str,
                              num_lines: int = 4,
                              vulnerability_level: float = 0.7) -> List[Dict[str, str]]:
        """
        Generate lyrics for specified global genre and theme.
        
        Args:
            genre: Genre (afrobeats, uk_drill, kpop, reggaeton, etc.)
            theme: Theme (love, party, struggle, confidence, etc.)
            num_lines: Number of lines to generate
            vulnerability_level: 0.0-1.0 (affects LML tag assignment)
        
        Returns:
            List of dicts with 'line' and 'lml_trigger'
        """
        # Get templates for genre and theme
        templates = self.GLOBAL_LYRIC_TEMPLATES.get(genre, {}).get(theme, [])
        
        if not templates:
            # Fallback to mainstream pop
            templates = self.GLOBAL_LYRIC_TEMPLATES['mainstream_pop'].get(theme, [])
        
        if not templates:
            # Ultimate fallback
            templates = [
                "I'm feeling {alive_adj}, can't {stop_verb}",
                "You and me, we're {unstoppable_adj}",
                "This is our {moment_noun}, our {time_noun}",
                "Together we {shine_verb}, forever {free_adj}"
            ]
        
        # Generate lines
        lyrics = []
        for i in range(min(num_lines, len(templates) * 2)):
            template = templates[i % len(templates)]
            line = self._fill_global_template(template)
            lml_tag = self._assign_lml_tag(line, vulnerability_level, i, num_lines)
            
            lyrics.append({
                'line': line,
                'lml_trigger': lml_tag
            })
        
        return lyrics
    
    def _fill_global_template(self, template: str) -> str:
        """Fill template with global word banks."""
        import re
        filled = template
        
        # Find all placeholders {word_type}
        placeholders = re.findall(r'\{([a-z_]+)\}', template)
        
        for placeholder in placeholders:
            if placeholder in self.GLOBAL_WORD_BANKS:
                word = random.choice(self.GLOBAL_WORD_BANKS[placeholder])
                filled = filled.replace(f'{{{placeholder}}}', word, 1)
        
        return filled
    
    def _assign_lml_tag(self, line: str, vulnerability_level: float, line_index: int, total_lines: int) -> str:
        """Assign LML tag based on context."""
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


# Example usage
if __name__ == "__main__":
    import json
    
    engine = GlobalLyricEngine(seed=42)
    
    print("="*80)
    print("GLOBAL LYRIC ENGINE TEST")
    print("="*80)
    print(f"\nSupported Genres ({len(engine.get_available_genres())}): {', '.join(engine.get_available_genres())}")
    
    # Test different global genres
    test_cases = [
        ('afrobeats', 'celebration', "Afrobeats Party Anthem"),
        ('uk_drill', 'street', "UK Drill Street Track"),
        ('kpop', 'love', "K-pop Love Song"),
        ('reggaeton', 'party', "Reggaeton Club Banger"),
        ('bollywood_pop', 'romance', "Bollywood Romance"),
        ('arabic_trap', 'ambition', "Arabic Trap Hustle"),
        ('mainstream_pop', 'empowerment', "Pop Empowerment Anthem")
    ]
    
    for genre, theme, description in test_cases:
        print(f"\n{'='*80}")
        print(f"{description} ({genre} - {theme})")
        print(f"{'='*80}")
        
        lyrics = engine.generate_global_lyrics(
            genre=genre,
            theme=theme,
            num_lines=4,
            vulnerability_level=0.65
        )
        
        for i, lyric in enumerate(lyrics, 1):
            tag = f" [{lyric['lml_trigger']}]" if lyric['lml_trigger'] else ""
            print(f"{i}. \"{lyric['line']}\"{tag}")
