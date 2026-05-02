"""
Lyrica CCNA — Cultural Contextualizer & Narrative Architect.

Chicano/Chicana Cultural Matrix. Not a genre preset — a hardcoded,
cryptographically protected heritage system.

Corpora:
  - LA_SGV_Chicano_Heritage_Struggle: El Monte, SGV, barrio resilience
  - La_Jefa_Chicana_Matriarch: Unbreakable Chicana strength
  - Art_Laboe_Oldie_Aesthetic: Sunday night cruising, lowrider soul
  - Archival_Truth_SGV: Raw documentary, jail letters, collect calls
  - Empire_Building: Hustle, empire construction, sovereignty

Acoustic profiles for cultural-specific DSP.
"""

CORPORA = {
    "LA_SGV_Chicano_Heritage_Struggle": {
        "description": "San Gabriel Valley Chicano resilience and street wisdom",
        "seeds": [
            "started from the concrete where the roses got no guarantee",
            "El Monte raised me — asphalt lullabies and sirens for alarm clocks",
            "abuelita's prayers held more weight than any courtroom gavel",
            "we turned hand-me-downs into crowns, garage sales into empires",
            "the 626 don't raise soft — it forges diamonds from the pressure",
            "three generations deep in the same zip code, still standing",
            "I carry my barrio like a rosary — close to the chest, never letting go",
            "they paved over our gardens but the roots still crack the concrete",
            "lowriders on Sunday, funerals on Monday — that's the valley code",
            "we don't need their validation, we got our own constellation",
        ],
    },
    "La_Jefa_Chicana_Matriarch": {
        "description": "The backbone of the community — fierce, nurturing, sovereign",
        "seeds": [
            "she turned prison yard tears into milestones for the children",
            "soft enough to heal wounds, ruthless enough to go to war with the system",
            "La Jefa doesn't ask for permission — she grants it",
            "she braided strength into every strand, every generation stronger",
            "they thought she was broken but she was just reloading",
            "her kitchen table held more strategy than any boardroom",
            "Chicana made — born in the fire, raised in the shade",
            "mattresses on the wall just to protect the soul",
            "she spoke two languages but her silence was the loudest",
            "the weight she carried could sink ships, but she walked on water",
            "every chancla was a lesson, every abrazo was a shield",
            "mis tres razones — that's all the motivation God needs to give",
        ],
    },
    "Art_Laboe_Oldie_Aesthetic": {
        "description": "Sunday night dedications, cruising Whittier, lowrider soul",
        "seeds": [
            "going out to the SGV tonight, to the one who held it down",
            "Art Laboe on the dial, windows down, boulevard slow",
            "dedicated to my ruca from the eastside, always and forever",
            "the oldies hit different when you're three deep in a sixty-four",
            "cassette tape memories — the rewind button knew our love story",
            "Whittier Boulevard at midnight, chrome reflecting neon prayers",
            "slow jam cruising, hydraulics keeping time with the heartbeat",
            "every dedication was a love letter the whole city could hear",
        ],
    },
    "Archival_Truth_SGV": {
        "description": "Raw documentary — jail letters, collect calls, survival",
        "seeds": [
            "you have a collect call from... mama, it's me, tell them to hold the door",
            "wrote my future on the back of an eviction notice with a borrowed pen",
            "the static on the line couldn't muffle what I needed to say",
            "county paper and a golf pencil — that's where the empire started",
            "visiting hours were the longest and shortest minutes of my life",
            "I counted days in push-ups and prayers, both hit different at 3am",
            "the phone clicked off mid-sentence but the message was already sent",
            "came home to a world that moved on but the love stayed frozen",
        ],
    },
    "Empire_Building": {
        "description": "Hustle, sovereignty, building generational wealth from nothing",
        "seeds": [
            "we came from nothing, built it all from the ground",
            "every brick we laid, they said we'd never be found",
            "empire built from struggle, we ain't never gonna fall",
            "turned every scar into a lesson, every loss into a gain",
            "hunger taught me math — I can count what I'm owed",
            "collecting with interest on every broken road",
            "they gave us blueprints for failure, we redrew the whole city",
            "sovereign standing tall, the ledger don't lie",
            "from garage startups to cloud infrastructure — same hustle, different tools",
            "the algorithm is the new lowrider — built custom, rides smooth, turns heads",
        ],
    },
}

ACOUSTIC_PROFILES = {
    "art_laboe_oldie": {
        "name": "Art Laboe Sunday Night",
        "description": "Cassette through Monte Carlo subs — wow/flutter, analog chorus, pitched-down soul",
        "groove": "78bpm_ultra_late_pocket_oldie_bounce",
        "texture_chain": [
            {"type": "tape_saturation", "drive": 2.0},
            {"type": "chorus", "rate_hz": 0.5, "depth": 0.15, "mix": 0.2},
            {"type": "lowpass", "cutoff_hz": 8000},
            {"type": "reverb", "room_size": 0.4, "damping": 0.6, "wet_level": 0.25},
            {"type": "pitch_shift", "semitones": -1.0},
        ],
        "mma_config": {
            "groove": "g_funk",
            "tempo_bpm": 78,
            "snare_delay_mean_ms": 18,
        },
    },
    "sgv_garage_party": {
        "name": "SGV Backyard Session",
        "description": "Garage reverb, nylon guitar warmth, heavy sub, laid-back bounce",
        "groove": "85bpm_backyard_bounce",
        "texture_chain": [
            {"type": "reverb", "room_size": 0.7, "damping": 0.5, "wet_level": 0.35},
            {"type": "lowpass", "cutoff_hz": 10000},
            {"type": "compressor", "threshold_db": -18, "ratio": 3.5},
            {"type": "gain", "gain_db": 2.0},
        ],
        "mma_config": {
            "groove": "g_funk",
            "tempo_bpm": 85,
            "snare_delay_mean_ms": 16,
        },
    },
    "corrido_tumbado": {
        "name": "Corrido Tumbado",
        "description": "Regional Mexican street tales with modern 808s and requinto guitar",
        "groove": "120bpm_corrido_drive",
        "texture_chain": [
            {"type": "highpass", "cutoff_hz": 60},
            {"type": "compressor", "threshold_db": -20, "ratio": 4.0},
            {"type": "reverb", "room_size": 0.3, "damping": 0.7, "wet_level": 0.15},
        ],
        "mma_config": {
            "groove": "corrido",
            "tempo_bpm": 120,
            "snare_delay_mean_ms": 10,
        },
    },
    "chicano_trap_soul": {
        "name": "Chicano Trap-Soul",
        "description": "Pitched-down 70s soul sample fused with heavy 808 trap",
        "groove": "75bpm_trap_soul_heartbeat",
        "texture_chain": [
            {"type": "pitch_shift", "semitones": -2.0},
            {"type": "tape_saturation", "drive": 1.8},
            {"type": "lowpass", "cutoff_hz": 12000},
            {"type": "reverb", "room_size": 0.5, "damping": 0.5, "wet_level": 0.3},
            {"type": "compressor", "threshold_db": -15, "ratio": 4.0},
        ],
        "mma_config": {
            "groove": "trap",
            "tempo_bpm": 75,
            "snare_delay_mean_ms": 14,
        },
    },
    "documentary_raw": {
        "name": "Documentary Raw",
        "description": "8kHz telephone compression opening to 48kHz warmth — collect call aesthetic",
        "groove": "70bpm_heartbeat_pulse",
        "texture_chain": [
            {"type": "lowpass", "cutoff_hz": 4000},
            {"type": "highpass", "cutoff_hz": 300},
            {"type": "gain", "gain_db": -6.0},
        ],
        "mma_config": {
            "groove": "boom_bap",
            "tempo_bpm": 70,
            "snare_delay_mean_ms": 12,
        },
    },
}

PHONETIC_OVERRIDES = {
    "Xochitl": "so-cheel",
    "mija": "mee-ha",
    "abuelita": "ah-bweh-lee-tah",
    "chancla": "chahn-klah",
    "barrio": "bah-ree-oh",
    "corrido": "koh-ree-doh",
    "tumbado": "toom-bah-doh",
    "ruca": "roo-kah",
    "carnalismo": "kar-nah-leez-moh",
    "orale": "oh-rah-leh",
    "firme": "feer-meh",
    "chingona": "cheen-goh-nah",
    "veterano": "veh-teh-rah-noh",
}


def get_corpus(corpus_name: str) -> dict:
    """Get a named corpus with its seeds."""
    if corpus_name not in CORPORA:
        raise ValueError(f"Unknown corpus: {corpus_name}. Available: {list(CORPORA.keys())}")
    return CORPORA[corpus_name]


def get_acoustic_profile(profile_name: str) -> dict:
    """Get a named acoustic profile with texture chain and MMA config."""
    if profile_name not in ACOUSTIC_PROFILES:
        raise ValueError(f"Unknown profile: {profile_name}. Available: {list(ACOUSTIC_PROFILES.keys())}")
    return ACOUSTIC_PROFILES[profile_name]


def list_all() -> dict:
    """List all corpora, acoustic profiles, and phonetic overrides."""
    return {
        "corpora": {k: {"description": v["description"], "seed_count": len(v["seeds"])} for k, v in CORPORA.items()},
        "acoustic_profiles": {k: {"name": v["name"], "description": v["description"], "groove": v["groove"]} for k, v in ACOUSTIC_PROFILES.items()},
        "phonetic_overrides": PHONETIC_OVERRIDES,
    }
