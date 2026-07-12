/**
 * CreatureRegistry.js
 *
 * Single source of truth for which creatures exist and their per-creature
 * atlas parameters. Adding a creature means adding one entry here + dropping
 * the matching <id>.png/<id>.json pair into assets/atlases/ — no other file
 * in this codebase should ever hardcode a creature name. That's what makes
 * the system "character-agnostic": CombatEntity, AnimationBuilder, and the
 * boss/minion spawners all read from this table, never from a switch statement
 * on creature identity.
 *
 * See docs/ATLAS_CONTRACT.md for the frame/state rules this config assumes.
 */

export const STATES = ['idle', 'swim', 'attack', 'hit', 'enraged', 'death'];

export const CREATURES = {
  gold_wolf: {
    id: 'gold_wolf',
    displayName: 'Sovereign Slam Wolf',
    role: 'minion',              // 'minion' | 'boss' | 'treasure'
    frameWidth: 128,
    frameHeight: 128,
    scale: 1.0,
    baseHealth: 20,
    baseSpeed: 60,
    enrageThreshold: 0.3,        // fraction of health remaining that triggers 'enraged'
    baseCoinValue: 5,
    movement: 'drift',           // 'drift' | 'weave' | 'flee' — ignored for role: 'boss'
    animFps: {
      idle: 6, swim: 10, attack: 14, hit: 12, enraged: 8, death: 8,
    },
  },
  fire_jaguar: {
    id: 'fire_jaguar',
    displayName: 'Fire Jaguar Warrior',
    role: 'minion',
    frameWidth: 128,
    frameHeight: 128,
    scale: 1.1,
    baseHealth: 35,
    baseSpeed: 50,
    enrageThreshold: 0.3,
    baseCoinValue: 5,
    movement: 'drift',
    animFps: {
      idle: 6, swim: 9, attack: 15, hit: 12, enraged: 8, death: 8,
    },
  },
  obsidian_serpent: {
    id: 'obsidian_serpent',
    displayName: 'Obsidian Coil Serpent',
    role: 'minion',
    frameWidth: 128,
    frameHeight: 128,
    scale: 0.85,
    baseHealth: 12,
    baseSpeed: 95,
    enrageThreshold: 0.3,
    baseCoinValue: 4,
    movement: 'drift',
    animFps: {
      idle: 7, swim: 13, attack: 16, hit: 13, enraged: 9, death: 8,
    },
  },
  stone_turtle: {
    id: 'stone_turtle',
    displayName: 'Stone-Shell Guardian',
    role: 'minion',
    frameWidth: 128,
    frameHeight: 128,
    scale: 1.3,
    baseHealth: 65,
    baseSpeed: 22,
    enrageThreshold: 0.25,
    baseCoinValue: 9,
    movement: 'drift',
    animFps: {
      idle: 4, swim: 6, attack: 10, hit: 9, enraged: 6, death: 7,
    },
  },
  eagle_warrior: {
    id: 'eagle_warrior',
    displayName: 'Sky Eagle Warrior',
    role: 'minion',
    frameWidth: 128,
    frameHeight: 128,
    scale: 1.0,
    baseHealth: 18,
    baseSpeed: 75,
    enrageThreshold: 0.3,
    baseCoinValue: 6,
    movement: 'weave',           // vertical swooping flight path, see DemoScene._patrolWeave
    animFps: {
      idle: 6, swim: 11, attack: 15, hit: 12, enraged: 8, death: 8,
    },
  },
  aztec_wolf_boss: {
    id: 'aztec_wolf_boss',
    displayName: 'Mictlantecuhtli, Bone Sovereign',
    role: 'boss',
    frameWidth: 128,
    frameHeight: 128,
    scale: 2.4,
    baseHealth: 2000,
    baseSpeed: 25,
    enrageThreshold: 0.35,
    baseCoinValue: 500,
    animFps: {
      idle: 5, swim: 7, attack: 12, hit: 10, enraged: 7, death: 6,
    },
  },
  tlaltecuhtli_boss: {
    id: 'tlaltecuhtli_boss',
    displayName: 'Tlaltecuhtli, Earth Devourer',
    role: 'boss',
    frameWidth: 128,
    frameHeight: 128,
    scale: 2.6,
    baseHealth: 2600,
    baseSpeed: 20,
    enrageThreshold: 0.3,
    baseCoinValue: 600,
    animFps: {
      idle: 5, swim: 7, attack: 11, hit: 9, enraged: 7, death: 6,
    },
  },
  jade_treasure_fish: {
    id: 'jade_treasure_fish',
    displayName: 'Jade Treasure Koi',
    role: 'treasure',            // flees the cannon instead of fighting; big coin payout
    frameWidth: 128,
    frameHeight: 128,
    scale: 0.75,
    baseHealth: 8,
    baseSpeed: 115,
    enrageThreshold: 0.3,
    baseCoinValue: 40,
    movement: 'flee',
    animFps: {
      idle: 7, swim: 15, attack: 14, hit: 12, enraged: 9, death: 8,
    },
  },
};

export function getCreature(id) {
  const c = CREATURES[id];
  if (!c) {
    throw new Error(
      `[CreatureRegistry] Unknown creature_id "${id}". ` +
      `Register it in CREATURES before referencing it — nothing should ` +
      `hardcode a fallback creature.`
    );
  }
  return c;
}

export function listCreatureIds() {
  return Object.keys(CREATURES);
}

export function listBossIds() {
  return Object.values(CREATURES).filter(c => c.role === 'boss').map(c => c.id);
}

export function listMinionIds() {
  return Object.values(CREATURES).filter(c => c.role === 'minion').map(c => c.id);
}

export function listTreasureIds() {
  return Object.values(CREATURES).filter(c => c.role === 'treasure').map(c => c.id);
}
