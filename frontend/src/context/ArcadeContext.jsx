import { createContext, useContext, useState, useEffect } from "react";

// Canon theme configurations
export const CANONS = {
  horror: {
    id: "horror",
    name: "Horror",
    icon: "👻",
    description: "Dark terrors, survival horror, and nightmare fuel",
    colors: {
      primary: "#8b0000",
      secondary: "#2d0a0a",
      accent: "#ff0000",
      bg: "#0a0a0a",
      text: "#e0e0e0",
      neon: "#ff3333"
    },
    machines: [
      { id: "monster_builder", name: "Monster Builder", desc: "Create terrifying creatures", cost: 50, difficulty: "Medium", icon: "👹" },
      { id: "fear_engine", name: "Fear Engine", desc: "Generate psychological horror scenarios", cost: 75, difficulty: "Hard", icon: "😱" },
      { id: "survival_blueprint", name: "Survival Blueprint", desc: "Design survival horror game mechanics", cost: 100, difficulty: "Expert", icon: "🏚️" },
      { id: "curse_generator", name: "Curse Generator", desc: "Craft supernatural curses and hexes", cost: 40, difficulty: "Easy", icon: "🔮" }
    ],
    multiplier: 1.5
  },
  anime: {
    id: "anime",
    name: "Anime",
    icon: "🎌",
    description: "Japanese animation style characters, stories, and worlds",
    colors: {
      primary: "#ff6b9d",
      secondary: "#1a1a2e",
      accent: "#00d4ff",
      bg: "#0f0f1a",
      text: "#ffffff",
      neon: "#ff69b4"
    },
    machines: [
      { id: "character_engine", name: "Character Engine", desc: "Generate original anime characters", cost: 50, difficulty: "Medium", icon: "🎨", endpoint: "/anime/character" },
      { id: "lore_engine", name: "Lore Engine", desc: "Build anime world mythology", cost: 60, difficulty: "Medium", icon: "📚", endpoint: "/anime/lore" },
      { id: "episode_engine", name: "Episode Engine", desc: "Create episode storylines", cost: 80, difficulty: "Hard", icon: "📺", endpoint: "/anime/story" },
      { id: "art_direction", name: "Art Direction", desc: "Define visual style guides", cost: 70, difficulty: "Medium", icon: "🖼️", endpoint: "/art-direction" }
    ],
    multiplier: 1.2
  },
  southern: {
    id: "southern",
    name: "Southern Gothic",
    icon: "🌿",
    description: "Deep south mysteries, swamp legends, and rural horror",
    colors: {
      primary: "#8fbc8f",
      secondary: "#2f4f2f",
      accent: "#daa520",
      bg: "#1a1a0f",
      text: "#f5f5dc",
      neon: "#9acd32"
    },
    machines: [
      { id: "sl_blueprint", name: "SL Blueprint", desc: "Southern gothic story structures", cost: 60, difficulty: "Medium", icon: "🏛️" },
      { id: "sl_persona", name: "SL Persona", desc: "Create southern characters", cost: 50, difficulty: "Easy", icon: "🤠" },
      { id: "chrome_bloom", name: "Chrome Bloom Engine", desc: "Generate atmospheric settings", cost: 70, difficulty: "Hard", icon: "🌸" },
      { id: "bayou_tales", name: "Bayou Tales", desc: "Swamp-based story generator", cost: 55, difficulty: "Medium", icon: "🐊" }
    ],
    multiplier: 1.3
  },
  cyberpunk: {
    id: "cyberpunk",
    name: "Cyberpunk",
    icon: "🤖",
    description: "High tech, low life. Neon-soaked dystopian futures",
    colors: {
      primary: "#00ffff",
      secondary: "#0d0d1a",
      accent: "#ff00ff",
      bg: "#050510",
      text: "#e0e0ff",
      neon: "#00ffff"
    },
    machines: [
      { id: "augment_engine", name: "Augment Engine", desc: "Design cybernetic enhancements", cost: 80, difficulty: "Hard", icon: "🦾" },
      { id: "hack_engine", name: "Hack Engine", desc: "Generate hacking scenarios", cost: 60, difficulty: "Medium", icon: "💻" },
      { id: "neon_blueprint", name: "Neon Blueprint", desc: "Create cyberpunk city designs", cost: 90, difficulty: "Expert", icon: "🌃" },
      { id: "corp_builder", name: "Corp Builder", desc: "Design megacorporations", cost: 70, difficulty: "Hard", icon: "🏢" }
    ],
    multiplier: 1.4
  },
  fantasy: {
    id: "fantasy",
    name: "Fantasy",
    icon: "🐉",
    description: "Epic quests, magical realms, and legendary creatures",
    colors: {
      primary: "#9b59b6",
      secondary: "#1a0a2e",
      accent: "#f1c40f",
      bg: "#0a0a14",
      text: "#f0e6ff",
      neon: "#9b59b6"
    },
    machines: [
      { id: "quest_forge", name: "Quest Forge", desc: "Generate epic quest lines", cost: 70, difficulty: "Hard", icon: "⚔️" },
      { id: "spell_weaver", name: "Spell Weaver", desc: "Create magic systems", cost: 60, difficulty: "Medium", icon: "✨" },
      { id: "realm_builder", name: "Realm Builder", desc: "Design fantasy kingdoms", cost: 85, difficulty: "Expert", icon: "🏰" },
      { id: "creature_codex", name: "Creature Codex", desc: "Generate mythical beasts", cost: 50, difficulty: "Easy", icon: "🦄" }
    ],
    multiplier: 1.25
  },
  romance: {
    id: "romance",
    name: "Romance",
    icon: "💕",
    description: "Love stories, relationship dynamics, and emotional journeys",
    colors: {
      primary: "#e91e63",
      secondary: "#1a0a14",
      accent: "#ffb6c1",
      bg: "#0f0a0c",
      text: "#fff0f5",
      neon: "#ff1493"
    },
    machines: [
      { id: "meet_cute", name: "Meet Cute Generator", desc: "Create romantic first encounters", cost: 40, difficulty: "Easy", icon: "💘" },
      { id: "tension_engine", name: "Tension Engine", desc: "Build romantic tension scenarios", cost: 55, difficulty: "Medium", icon: "🔥" },
      { id: "arc_weaver", name: "Arc Weaver", desc: "Design relationship arcs", cost: 65, difficulty: "Hard", icon: "💫" },
      { id: "dialogue_spark", name: "Dialogue Spark", desc: "Generate romantic dialogue", cost: 45, difficulty: "Easy", icon: "💬" }
    ],
    multiplier: 1.1
  },
  urban: {
    id: "urban",
    name: "Urban",
    icon: "🌆",
    description: "City life, street culture, and modern-day stories",
    colors: {
      primary: "#ff9800",
      secondary: "#1a1410",
      accent: "#4caf50",
      bg: "#0a0908",
      text: "#fff8e1",
      neon: "#ff9800"
    },
    machines: [
      { id: "street_tales", name: "Street Tales", desc: "Generate urban narratives", cost: 50, difficulty: "Medium", icon: "🎤" },
      { id: "hood_builder", name: "Hood Builder", desc: "Create neighborhood settings", cost: 60, difficulty: "Medium", icon: "🏘️" },
      { id: "hustle_engine", name: "Hustle Engine", desc: "Design come-up stories", cost: 70, difficulty: "Hard", icon: "💰" },
      { id: "crew_forge", name: "Crew Forge", desc: "Build character crews", cost: 55, difficulty: "Medium", icon: "👥" }
    ],
    multiplier: 1.2
  },
  mythic: {
    id: "mythic",
    name: "Mythic",
    icon: "⚡",
    description: "Ancient legends, gods, and timeless mythology",
    colors: {
      primary: "#ffd700",
      secondary: "#1a1400",
      accent: "#4169e1",
      bg: "#0a0a05",
      text: "#fffaf0",
      neon: "#ffd700"
    },
    machines: [
      { id: "pantheon_forge", name: "Pantheon Forge", desc: "Create god hierarchies", cost: 80, difficulty: "Expert", icon: "🏛️" },
      { id: "hero_engine", name: "Hero Engine", desc: "Generate legendary heroes", cost: 60, difficulty: "Medium", icon: "🦸" },
      { id: "prophecy_weaver", name: "Prophecy Weaver", desc: "Craft divine prophecies", cost: 70, difficulty: "Hard", icon: "📜" },
      { id: "artifact_smith", name: "Artifact Smith", desc: "Design mythic artifacts", cost: 55, difficulty: "Medium", icon: "🗡️" }
    ],
    multiplier: 1.35
  }
};

// Universal Art Engine - shared across all canons
export const UNIVERSAL_ART_ENGINE = {
  styleRules: {
    narrative: ["three-act structure", "hero's journey", "tragedy", "comedy", "mystery"],
    pacing: ["slow burn", "action-packed", "episodic", "continuous"],
    tone: ["dark", "light", "satirical", "earnest", "ambiguous"]
  },
  archetypes: {
    heroes: ["reluctant hero", "chosen one", "anti-hero", "everyman", "mentor"],
    villains: ["mastermind", "fallen hero", "force of nature", "tragic villain", "trickster"],
    support: ["loyal friend", "love interest", "rival", "comic relief", "mysterious stranger"]
  },
  worldbuilding: {
    scales: ["personal", "local", "regional", "global", "cosmic"],
    conflicts: ["person vs person", "person vs nature", "person vs society", "person vs self", "person vs fate"]
  }
};

// Jackpot configurations
export const JACKPOT_CONFIG = {
  triggers: {
    complete_struct: { chance: 0.15, multiplier: 2, name: "Complete Structure" },
    rare_combo: { chance: 0.08, multiplier: 3, name: "Rare Combination" },
    perfect_output: { chance: 0.05, multiplier: 5, name: "Perfect Output" },
    canon_master: { chance: 0.03, multiplier: 10, name: "Canon Master" }
  },
  basePool: 1000,
  contributionRate: 0.1
};

const ArcadeContext = createContext();

export const ArcadeProvider = ({ children }) => {
  const [currentCanon, setCurrentCanon] = useState("anime");
  const [tokens, setTokens] = useState(() => {
    const saved = localStorage.getItem("arcadeTokens");
    return saved ? parseInt(saved) : 500;
  });
  const [jackpotPool, setJackpotPool] = useState(() => {
    const saved = localStorage.getItem("jackpotPool");
    return saved ? parseInt(saved) : JACKPOT_CONFIG.basePool;
  });
  const [recentJackpots, setRecentJackpots] = useState(() => {
    const saved = localStorage.getItem("recentJackpots");
    return saved ? JSON.parse(saved) : [];
  });
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem("arcadeSessions");
    return saved ? JSON.parse(saved) : [];
  });

  // Persist state
  useEffect(() => {
    localStorage.setItem("arcadeTokens", tokens);
  }, [tokens]);

  useEffect(() => {
    localStorage.setItem("jackpotPool", jackpotPool);
  }, [jackpotPool]);

  useEffect(() => {
    localStorage.setItem("recentJackpots", JSON.stringify(recentJackpots));
  }, [recentJackpots]);

  useEffect(() => {
    localStorage.setItem("arcadeSessions", JSON.stringify(sessions));
  }, [sessions]);

  const spendTokens = (amount) => {
    if (tokens >= amount) {
      setTokens(prev => prev - amount);
      // Contribute to jackpot pool
      setJackpotPool(prev => prev + Math.floor(amount * JACKPOT_CONFIG.contributionRate));
      return true;
    }
    return false;
  };

  const addTokens = (amount) => {
    setTokens(prev => prev + amount);
  };

  const checkJackpot = (output) => {
    const canon = CANONS[currentCanon];
    const triggers = JACKPOT_CONFIG.triggers;
    
    // Check for jackpot triggers based on output quality
    const outputStr = JSON.stringify(output);
    const hasCompleteStruct = outputStr.length > 2000;
    const hasRareCombo = outputStr.includes("unique") || outputStr.includes("rare");
    
    let jackpotResult = null;
    
    if (hasCompleteStruct && Math.random() < triggers.complete_struct.chance * canon.multiplier) {
      jackpotResult = {
        type: "complete_struct",
        amount: Math.floor(jackpotPool * 0.1 * triggers.complete_struct.multiplier),
        name: triggers.complete_struct.name
      };
    } else if (hasRareCombo && Math.random() < triggers.rare_combo.chance * canon.multiplier) {
      jackpotResult = {
        type: "rare_combo",
        amount: Math.floor(jackpotPool * 0.05 * triggers.rare_combo.multiplier),
        name: triggers.rare_combo.name
      };
    }
    
    if (jackpotResult) {
      addTokens(jackpotResult.amount);
      setJackpotPool(prev => Math.max(JACKPOT_CONFIG.basePool, prev - jackpotResult.amount));
      setRecentJackpots(prev => [{
        ...jackpotResult,
        canon: currentCanon,
        timestamp: new Date().toISOString()
      }, ...prev.slice(0, 9)]);
    }
    
    return jackpotResult;
  };

  const saveSession = (session) => {
    setSessions(prev => [session, ...prev.slice(0, 49)]);
  };

  const value = {
    currentCanon,
    setCurrentCanon,
    canonData: CANONS[currentCanon],
    allCanons: CANONS,
    tokens,
    spendTokens,
    addTokens,
    jackpotPool,
    recentJackpots,
    checkJackpot,
    sessions,
    saveSession,
    universalEngine: UNIVERSAL_ART_ENGINE
  };

  return (
    <ArcadeContext.Provider value={value}>
      {children}
    </ArcadeContext.Provider>
  );
};

export const useArcade = () => {
  const context = useContext(ArcadeContext);
  if (!context) {
    throw new Error("useArcade must be used within ArcadeProvider");
  }
  return context;
};
