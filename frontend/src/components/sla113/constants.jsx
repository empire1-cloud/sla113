import {
  GameController, Crosshair, Coin, Rocket, PersonSimpleRun,
  PuzzlePiece, Cards, CastleTurret, Scroll, Sword,
} from "@phosphor-icons/react";

export const API = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

export const GAME_ICONS = {
  fish_shooter: Crosshair,
  slot_machine: Coin,
  crash_game: Rocket,
  platformer: PersonSimpleRun,
  puzzle: PuzzlePiece,
  card_game: Cards,
  tower_defense: CastleTurret,
  runner: PersonSimpleRun,
  rpg: Scroll,
  battle_royale: Sword,
};

export const GAME_COLORS = {
  fish_shooter: "#22d3ee",
  slot_machine: "#facc15",
  crash_game: "#ef4444",
  platformer: "#22c55e",
  puzzle: "#a855f7",
  card_game: "#f97316",
  tower_defense: "#3b82f6",
  runner: "#06b6d4",
  rpg: "#ec4899",
  battle_royale: "#f43f5e",
};

export const ASSET_TYPES = ["sprites", "backgrounds", "ui", "animations", "effects"];
export const LOGIC_TYPES = ["mechanics", "rtp", "paytable", "rng", "scoring", "levels", "economy"];
export const STYLES = ["pixel_art", "vector", "3d_render", "hand_drawn", "anime", "neon", "retro"];

export const NoProjectSelected = () => (
  <div className="sla-empty" data-testid="no-project-selected">
    <GameController size={48} weight="thin" />
    <p>Select a project from the Dashboard first</p>
  </div>
);
