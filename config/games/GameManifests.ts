// SLA113 // GAME MANIFESTS
// Strict Asset Segregation & Canon Enforcement

export type GameId = 'SOVEREIGN_SLAM' | 'AZTEC_TIDE';

export interface GameManifest {
  id: GameId;
  name: string;
  type: 'SLOT' | 'FISH';
  theme: 'CHICANO_LOWRIDER' | 'AZTEC_MYTHOLOGY';
  assets: {
    alias: string;
    src: string; // Placeholder for Vertex AI assets
    type: 'SPRITE' | 'ATLAS' | 'VIDEO' | 'AUDIO';
  }[];
  config: {
    seats: number;
    orientation: 'LANDSCAPE';
    physics?: 'MATTER_JS' | 'SIMPLE';
  };
}

export const MANIFESTS: Record<GameId, GameManifest> = {
  SOVEREIGN_SLAM: {
    id: 'SOVEREIGN_SLAM',
    name: 'Sovereign Slam',
    type: 'SLOT',
    theme: 'CHICANO_LOWRIDER',
    config: { seats: 1, orientation: 'LANDSCAPE' },
    assets: [
      // CANON: Chrome/Gold/Neon Lowrider Aesthetic
      { alias: 'bg_mural', src: '/assets/titleScreen.jpg', type: 'SPRITE' }, // Placeholder: Mural Lobby
      { alias: 'sym_lowrider', src: '/assets/lowrider_symbol.png', type: 'SPRITE' }, // Placeholder
      { alias: 'sym_s_emblem', src: '/brand/southern-logo.png', type: 'SPRITE' },
      { alias: 'sfx_hydraulic', src: '/audio/hydraulic_pump.mp3', type: 'AUDIO' },
    ]
  },
  AZTEC_TIDE: {
    id: 'AZTEC_TIDE',
    name: 'Aztec Tide',
    type: 'FISH',
    theme: 'AZTEC_MYTHOLOGY',
    config: { seats: 4, orientation: 'LANDSCAPE', physics: 'MATTER_JS' },
    assets: [
      // CANON: Stone/Jade/Crimson Aztec Aesthetic
      { alias: 'bg_ruins', src: '/assets/aztec_ruins_bg.jpg', type: 'SPRITE' }, // Placeholder
      { alias: 'boss_mictlan', src: '/assets/mictlantecuhtli_bone_sovereign.jpg', type: 'SPRITE' },
      { alias: 'fish_jade', src: '/assets/jade_fish.png', type: 'SPRITE' }, // Placeholder
      { alias: 'cannon_turret', src: '/assets/cannon_gold.png', type: 'SPRITE' }, // Placeholder
    ]
  }
};
