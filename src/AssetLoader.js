/**
 * AssetLoader.js
 *
 * Loads creature + shared atlas pairs by the naming convention in
 * docs/ATLAS_CONTRACT.md, then builds every Phaser animation once loading
 * completes. This is the only place that knows the assets/atlases/ path
 * structure — everything downstream just calls buildCreatureAnimations
 * with an already-loaded texture.
 */

import { CREATURES } from './CreatureRegistry.js';
import { buildCreatureAnimations, buildSharedAnimations } from './AnimationBuilder.js';

const ATLAS_BASE_PATH = 'assets/atlases';

const SHARED_SHEETS = [
  { key: 'projectiles', prefix: 'projectile', fps: { bolt: 20, harpoon: 14 } },
  { key: 'impacts', prefix: 'impact', fps: { spark: 18 } },
  { key: 'coins', prefix: 'coin', fps: { spin: 10, burst: 16 } },
  { key: 'cannon', prefix: 'cannon', fps: { fire: 16 } },
];

/**
 * Queue every registered creature + shared sheet for load. Call from a
 * scene's preload().
 * @param {Phaser.Scene} scene
 * @param {string[]} [creatureIds] defaults to every creature in the registry
 */
export function queueAssetLoad(scene, creatureIds = Object.keys(CREATURES)) {
  for (const id of creatureIds) {
    scene.load.atlas(id, `${ATLAS_BASE_PATH}/${id}.png`, `${ATLAS_BASE_PATH}/${id}.json`);
  }
  for (const sheet of SHARED_SHEETS) {
    scene.load.atlas(sheet.key, `${ATLAS_BASE_PATH}/${sheet.key}.png`, `${ATLAS_BASE_PATH}/${sheet.key}.json`);
  }
  scene.load.atlas('ui', `${ATLAS_BASE_PATH}/ui.png`, `${ATLAS_BASE_PATH}/ui.json`);
}

/**
 * Build every animation for the loaded atlases. Call from a scene's create(),
 * after the load has completed.
 * @param {Phaser.Scene} scene
 * @param {string[]} [creatureIds] defaults to every creature in the registry
 */
export function buildAllAnimations(scene, creatureIds = Object.keys(CREATURES)) {
  for (const id of creatureIds) {
    buildCreatureAnimations(scene, id, CREATURES[id]);
  }
  for (const sheet of SHARED_SHEETS) {
    buildSharedAnimations(scene, sheet.key, sheet.prefix, sheet.fps);
  }
}
