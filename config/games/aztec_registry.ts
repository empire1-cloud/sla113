/**
 * SLA113 // AZTEC_MYTH_REGISTRY
 * 6 Variations of the Sovereign Fish Hunter Engine
 */

export const AZTEC_GAMES = [
  {
    id: 'luna_xolotl_duo',
    name: "Luna & Xolotl",
    god: "Bonded Pair",
    element: "Moon/Fire",
    color: "#D4AF37",
    description: "Sovereign bonded hunt: Luna marks, Xolotl executes. Twin Sigil Resonance active.",
    config: {
      bulletSpeed: 1450,
      spawnRate: 1400,
      bossHp: 900,
      multiplier: 4.2
    }
  },
  {
    id: 'tlaloc_tide',
    name: "Tlaloc's Tide",
    god: "Tlaloc",
    element: "Water",
    color: "#00FFFF",
    description: "The Rain God's aquatic realm. Hunt the sacred Jades and Blue Fins.",
    config: {
      bulletSpeed: 900,
      spawnRate: 1500,
      bossHp: 500,
      multiplier: 1.2
    }
  },
  {
    id: 'quetzalcoatl_quest',
    name: "Quetzalcoatl's Quest",
    god: "Quetzalcoatl",
    element: "Air/Spirit",
    color: "#00FF7F",
    description: "The Feathered Serpent commands the skies. Aim for the Emerald Serpents.",
    config: {
      bulletSpeed: 1200,
      spawnRate: 2000,
      bossHp: 400,
      multiplier: 1.5
    }
  },
  {
    id: 'mictlantecuhtli_maw',
    name: "Mictlantecuhtli's Maw",
    god: "Mictlantecuhtli",
    element: "Underworld",
    color: "#FF4500",
    description: "Descent into the dead. Target the Obsidian Skulls and Bone Eels.",
    config: {
      bulletSpeed: 800,
      spawnRate: 1000,
      bossHp: 800,
      multiplier: 2.0
    }
  },
  {
    id: 'huitzil_hunt',
    name: "Huitzilopochtli's Hunt",
    god: "Huitzilopochtli",
    element: "Fire/Sun",
    color: "#FFD700",
    description: "The Sun God's war. Crimson Piranhas and Solaris Rays.",
    config: {
      bulletSpeed: 1500,
      spawnRate: 2500,
      bossHp: 300,
      multiplier: 1.8
    }
  },
  {
    id: 'tezcat_trap',
    name: "Tezcatlipoca's Trap",
    god: "Tezcatlipoca",
    element: "Shadow",
    color: "#8A2BE2",
    description: "The Smoking Mirror reveals shadow prey. Hunt the Void Jaguars.",
    config: {
      bulletSpeed: 1000,
      spawnRate: 1800,
      bossHp: 600,
      multiplier: 2.5
    }
  },
  {
    id: 'xochi_reef',
    name: "Xochiquetzal's Reef",
    god: "Xochiquetzal",
    element: "Flower/Beauty",
    color: "#FF69B4",
    description: "Luxury and beauty. Radiant Corals and Petal Fins.",
    config: {
      bulletSpeed: 1100,
      spawnRate: 1200,
      bossHp: 450,
      multiplier: 1.3
    }
  },
  {
    id: 'coyol_moon',
    name: "Coyolxauhqui's Moon",
    god: "Coyolxauhqui",
    element: "Moon",
    color: "#B0C4DE",
    description: "The dismembered moon goddess. Silver rays and Lunar Eels.",
    config: {
      bulletSpeed: 1300,
      spawnRate: 2200,
      bossHp: 350,
      multiplier: 1.6
    }
  },
  {
    id: 'xiuh_hearth',
    name: "Xiuhtecuhtli's Hearth",
    god: "Xiuhtecuhtli",
    element: "Fire/Time",
    color: "#FF0000",
    description: "The Lord of Fire and Year. Volcanic Sharks and Magma Mantas.",
    config: {
      bulletSpeed: 1400,
      spawnRate: 2000,
      bossHp: 550,
      multiplier: 1.9
    }
  },
  {
    id: 'ehecatl_wind',
    name: "Ehēcatl's Gale",
    god: "Ehēcatl",
    element: "Wind",
    color: "#F5F5F5",
    description: "The Breath of Life. Whirlwind Darts and Hurricane Hawks.",
    config: {
      bulletSpeed: 1800,
      spawnRate: 3000,
      bossHp: 250,
      multiplier: 2.2
    }
  },
  {
    id: 'rabbit_chaos',
    name: "Centzon Tōtōchtin",
    god: "Centzon Tōtōchtin",
    element: "Chaos/Rabbit",
    color: "#D2B48C",
    description: "The 400 Drunken Rabbits. High-speed swarm chaos mechanics.",
    config: {
      bulletSpeed: 1000,
      spawnRate: 500,
      bossHp: 150,
      multiplier: 3.0
    }
  },
  {
    id: 'coatlicue_earth',
    name: "Coatlicue's Stone",
    god: "Coatlicue",
    element: "Earth",
    color: "#556B2F",
    description: "The Mother of Gods. Granite Turtles and Serpent Skirts.",
    config: {
      bulletSpeed: 700,
      spawnRate: 1500,
      bossHp: 1200,
      multiplier: 2.8
    }
  },
  {
    id: 'tonatiuh_realm',
    name: "Tonatiuh's Realm",
    god: "Tonatiuh",
    element: "Sun",
    color: "#FFFF00",
    description: "The Lord of the Fifth Sun. Pure Gold Leviathans.",
    config: {
      bulletSpeed: 1600,
      spawnRate: 3500,
      bossHp: 500,
      multiplier: 5.0
    }
  },
  {
    id: 'xochi_prince',
    name: "Xōchipilli's Grace",
    god: "Xōchipilli",
    element: "Art/Games",
    color: "#FFDAB9",
    description: "The Prince of Flowers. Golden Petals and Artistic Souls.",
    config: {
      bulletSpeed: 1100,
      spawnRate: 1500,
      bossHp: 400,
      multiplier: 2.2
    }
  },
  {
    id: 'xolotl_shock',
    name: "Xolotl's Descent",
    god: "Xolotl",
    element: "Lightning/Fire",
    color: "#FF8C00",
    description: "The Twin of Quetzalcoatl. Lightning Souls and Skeletal Guides.",
    config: {
      bulletSpeed: 2000,
      spawnRate: 1800,
      bossHp: 650,
      multiplier: 3.5
    }
  }
];
