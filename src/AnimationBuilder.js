/**
 * AnimationBuilder.js
 *
 * Reads the loaded texture atlas for a creature and auto-registers every
 * Phaser animation from the frame-key naming convention
 * `<creature_id>__<state>__<index>` (contract section 4). No code in this
 * file, or anywhere downstream, hardcodes a creature name or a frame count —
 * everything is derived from what the atlas JSON actually contains, so a
 * malformed or incomplete atlas fails loudly here instead of animating wrong
 * silently later.
 */

import { STATES } from './CreatureRegistry.js';

/**
 * @param {Phaser.Scene} scene
 * @param {string} creatureId
 * @param {object} creatureConfig  — one entry from CreatureRegistry.CREATURES
 * @returns {string[]} the state names that were successfully registered
 */
export function buildCreatureAnimations(scene, creatureId, creatureConfig) {
  const textureKey = creatureId;
  if (!scene.textures.exists(textureKey)) {
    throw new Error(
      `[AnimationBuilder] Texture "${textureKey}" not loaded. Did the preload ` +
      `step call scene.load.atlas("${textureKey}", "<id>.png", "<id>.json")?`
    );
  }

  const texture = scene.textures.get(textureKey);
  const allFrameNames = texture.getFrameNames();

  // Group frame names by state, using the frame index embedded in the key so
  // ordering is correct even if the atlas JSON's own key order isn't sorted.
  const framesByState = {};
  const keyPattern = new RegExp(`^${creatureId}__([a-z]+)__(\\d+)$`);

  for (const frameName of allFrameNames) {
    const match = frameName.match(keyPattern);
    if (!match) continue;
    const [, state, indexStr] = match;
    if (!framesByState[state]) framesByState[state] = [];
    framesByState[state].push({ frameName, index: parseInt(indexStr, 10) });
  }

  const registeredStates = [];
  const missingStates = [];

  for (const state of STATES) {
    const frames = framesByState[state];
    if (!frames || frames.length === 0) {
      missingStates.push(state);
      continue;
    }
    frames.sort((a, b) => a.index - b.index);

    const animKey = `${creatureId}__${state}`;
    if (scene.anims.exists(animKey)) {
      // Idempotent: rebuilding animations (e.g. hot-reloading a swapped atlas)
      // shouldn't throw on "animation already exists".
      scene.anims.remove(animKey);
    }

    scene.anims.create({
      key: animKey,
      frames: frames.map(f => ({ key: textureKey, frame: f.frameName })),
      frameRate: (creatureConfig.animFps && creatureConfig.animFps[state]) || 10,
      repeat: shouldLoop(state) ? -1 : 0,
    });

    registeredStates.push(state);
  }

  if (missingStates.length > 0) {
    // Loud, not silent — a creature missing e.g. 'enraged' frames should be
    // visible in the console during development, not discovered at runtime
    // when the state machine tries to play an animation that doesn't exist.
    console.warn(
      `[AnimationBuilder] "${creatureId}" atlas is missing states: ${missingStates.join(', ')}. ` +
      `CombatEntity will fall back to 'idle' for these states until real frames are added.`
    );
  }

  return registeredStates;
}

function shouldLoop(state) {
  return state === 'idle' || state === 'swim' || state === 'enraged';
}

/**
 * Registers shared (non-creature) FX/UI animations. These use a flatter key
 * scheme (`<kind>__<sub>__<index>`) since there's no per-state contract for
 * FX — see docs/ATLAS_CONTRACT.md section 5.
 */
export function buildSharedAnimations(scene, textureKey, kindPrefix, fpsBySub = {}) {
  if (!scene.textures.exists(textureKey)) {
    throw new Error(`[AnimationBuilder] Shared texture "${textureKey}" not loaded.`);
  }
  const texture = scene.textures.get(textureKey);
  const allFrameNames = texture.getFrameNames();
  const keyPattern = new RegExp(`^${kindPrefix}__([a-z_]+)__(\\d+)$`);

  const framesBySub = {};
  for (const frameName of allFrameNames) {
    const match = frameName.match(keyPattern);
    if (!match) continue;
    const [, sub, indexStr] = match;
    if (!framesBySub[sub]) framesBySub[sub] = [];
    framesBySub[sub].push({ frameName, index: parseInt(indexStr, 10) });
  }

  const registered = [];
  for (const [sub, frames] of Object.entries(framesBySub)) {
    frames.sort((a, b) => a.index - b.index);
    const animKey = `${kindPrefix}__${sub}`;
    if (scene.anims.exists(animKey)) scene.anims.remove(animKey);
    scene.anims.create({
      key: animKey,
      frames: frames.map(f => ({ key: textureKey, frame: f.frameName })),
      frameRate: fpsBySub[sub] || 14,
      repeat: 0,
    });
    registered.push(animKey);
  }
  return registered;
}
