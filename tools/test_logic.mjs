/**
 * test_logic.mjs
 *
 * Since a headless browser isn't reachable from this sandbox (Puppeteer's
 * Chromium download is blocked by network policy — storage.googleapis.com
 * isn't in the allowlist), this exercises the real AnimationBuilder and
 * CombatEntity modules against a minimal mock of the Phaser APIs they call.
 * This is NOT a substitute for an in-browser render test — it verifies the
 * logic (frame-key parsing, state transition rules) actually behaves as
 * specified, not that pixels draw correctly. Both matter; this covers one.
 */

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildCreatureAnimations } from '../src/AnimationBuilder.js';
import { CombatEntity, CombatState } from '../src/CombatEntity.js';
import { getCreature, CREATURES, listBossIds, listTreasureIds } from '../src/CreatureRegistry.js';

let passCount = 0;
let failCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  [pass] ${name}`);
    passCount++;
  } catch (err) {
    console.log(`  [FAIL] ${name}`);
    console.log(`         ${err.message}`);
    failCount++;
  }
}

// ---- Mock Phaser primitives -----------------------------------------------

class MockTexture {
  constructor(frameNames) {
    this._frameNames = frameNames;
  }
  getFrameNames() {
    return this._frameNames;
  }
}

class MockAnims {
  constructor() {
    this.registry = new Map();
  }
  exists(key) {
    return this.registry.has(key);
  }
  create(config) {
    this.registry.set(config.key, config);
  }
  remove(key) {
    this.registry.delete(key);
  }
  get(key) {
    return this.registry.get(key);
  }
}

class MockSprite {
  constructor() {
    this._listeners = {};
    this.currentAnim = null;
    this.body = { setVelocity: () => {} };
  }
  setScale() { return this; }
  setOrigin() { return this; }
  play(key) {
    this.currentAnim = key;
    return this;
  }
  on(event, cb) {
    this._listeners[event] = this._listeners[event] || [];
    this._listeners[event].push(cb);
  }
  emit(event, ...args) {
    (this._listeners[event] || []).forEach(cb => cb(...args));
  }
  destroy() {}
}

class MockScene {
  constructor(frameNamesByTexture) {
    this.anims = new MockAnims();
    this._textures = new Map(
      Object.entries(frameNamesByTexture).map(([k, v]) => [k, new MockTexture(v)])
    );
    this.textures = {
      exists: (key) => this._textures.has(key),
      get: (key) => this._textures.get(key),
    };
    this.physics = {
      add: {
        sprite: () => new MockSprite(),
      },
    };
  }
}

// ---- Build a realistic frame-name set matching the real atlas JSON --------

function loadRealFrameNames(creatureId) {
  const jsonPath = new URL(`../assets/atlases/${creatureId}.json`, import.meta.url);
  const atlas = JSON.parse(readFileSync(jsonPath, 'utf-8'));
  return Object.keys(atlas.frames);
}

console.log('\n=== AnimationBuilder: frame-key parsing against REAL generated atlas JSON ===');

test('gold_wolf atlas JSON parses into all 6 states with correct frame counts', () => {
  const frameNames = loadRealFrameNames('gold_wolf');
  const scene = new MockScene({ gold_wolf: frameNames });
  const registered = buildCreatureAnimations(scene, 'gold_wolf', getCreature('gold_wolf'));

  assert.deepEqual(
    registered.sort(),
    ['attack', 'death', 'enraged', 'hit', 'idle', 'swim'].sort(),
    'expected all 6 contract states to register'
  );

  const idleAnim = scene.anims.get('gold_wolf__idle');
  assert.ok(idleAnim, 'idle animation should be registered');
  assert.equal(idleAnim.repeat, -1, 'idle should loop (repeat: -1)');

  const attackAnim = scene.anims.get('gold_wolf__attack');
  assert.equal(attackAnim.repeat, 0, 'attack should NOT loop');

  const deathAnim = scene.anims.get('gold_wolf__death');
  assert.equal(deathAnim.repeat, 0, 'death should NOT loop');
});

test('every registered creature\'s real atlas JSON parses into all 6 contract states', () => {
  for (const id of Object.keys(CREATURES)) {
    const frameNames = loadRealFrameNames(id);
    const scene = new MockScene({ [id]: frameNames });
    const registered = buildCreatureAnimations(scene, id, getCreature(id));
    assert.deepEqual(
      registered.sort(),
      ['attack', 'death', 'enraged', 'hit', 'idle', 'swim'].sort(),
      `${id}: expected all 6 contract states to register`
    );
  }
});

test('frames within a state are correctly ordered by embedded index, not JSON key order', () => {
  const frameNames = loadRealFrameNames('gold_wolf');
  const scene = new MockScene({ gold_wolf: frameNames });
  buildCreatureAnimations(scene, 'gold_wolf', getCreature('gold_wolf'));

  const swimAnim = scene.anims.get('gold_wolf__swim');
  const indices = swimAnim.frames.map(f => {
    const m = f.frame.match(/__(\d+)$/);
    return parseInt(m[1], 10);
  });
  const sorted = [...indices].sort((a, b) => a - b);
  assert.deepEqual(indices, sorted, 'frame order must be ascending by index');
});

test('missing-state atlas warns but does not throw', () => {
  // Simulate a partial atlas (e.g. real art delivered idle+swim only so far)
  const partialFrames = [
    'partial_creature__idle__0',
    'partial_creature__idle__1',
    'partial_creature__swim__0',
    'partial_creature__swim__1',
  ];
  const scene = new MockScene({ partial_creature: partialFrames });
  const fakeConfig = { animFps: { idle: 6, swim: 8 } };

  let registered;
  assert.doesNotThrow(() => {
    registered = buildCreatureAnimations(scene, 'partial_creature', fakeConfig);
  });
  assert.deepEqual(registered.sort(), ['idle', 'swim'].sort());
});

test('unknown texture throws a clear, actionable error', () => {
  const scene = new MockScene({});
  assert.throws(
    () => buildCreatureAnimations(scene, 'never_loaded', {}),
    /Texture "never_loaded" not loaded/
  );
});

console.log('\n=== CreatureRegistry: contract lookups ===');

test('getCreature throws on unknown id instead of silently returning undefined', () => {
  assert.throws(() => getCreature('nonexistent_creature'), /Unknown creature_id/);
});

test('every registered creature declares all 6 animFps entries', () => {
  for (const [id, cfg] of Object.entries(CREATURES)) {
    const states = ['idle', 'swim', 'attack', 'hit', 'enraged', 'death'];
    for (const s of states) {
      assert.ok(
        typeof cfg.animFps[s] === 'number',
        `${id} is missing animFps.${s}`
      );
    }
  }
});

test('listTreasureIds returns only treasure-role creatures', () => {
  const ids = listTreasureIds();
  assert.ok(ids.length >= 1, 'expected at least one treasure creature');
  for (const id of ids) assert.equal(getCreature(id).role, 'treasure');
});

test('listBossIds returns at least 2 bosses so rotation has something to rotate through', () => {
  const ids = listBossIds();
  assert.ok(ids.length >= 2, `expected at least 2 bosses, got ${ids.length}`);
});

console.log('\n=== CombatEntity: state machine transition rules ===');

function makeMockEntityScene(creatureId) {
  const frameNames = loadRealFrameNames(creatureId);
  const scene = new MockScene({ [creatureId]: frameNames });
  buildCreatureAnimations(scene, creatureId, getCreature(creatureId));
  return scene;
}

test('death is terminal — no state can override it once entered', () => {
  const scene = makeMockEntityScene('gold_wolf');
  const entity = new CombatEntity(scene, 'gold_wolf', 0, 0);

  entity.takeDamage(entity.maxHealth); // lethal
  assert.equal(entity.isDead, true);
  assert.equal(entity.state, CombatState.DEATH);

  entity.playState(CombatState.IDLE);
  assert.equal(entity.state, CombatState.DEATH, 'state must remain DEATH after death');

  entity.takeDamage(999);
  assert.equal(entity.health, 0, 'health should not go negative or change post-death');
});

test('hit does not cancel an in-progress attack — it queues', () => {
  const scene = makeMockEntityScene('gold_wolf');
  const entity = new CombatEntity(scene, 'gold_wolf', 0, 0);

  entity.attack();
  assert.equal(entity.state, CombatState.ATTACK);

  entity.takeDamage(1); // sub-lethal hit while attacking
  assert.equal(
    entity.state, CombatState.ATTACK,
    'state should still show ATTACK immediately after a hit during attack windup'
  );
  assert.equal(entity._queuedHitAfterAttack, true, 'hit should be queued, not dropped or immediate');

  // Simulate the attack animation completing
  entity.sprite.emit('animationcomplete', { key: 'gold_wolf__attack' });
  assert.equal(entity.state, CombatState.HIT, 'queued hit should play once attack completes');
});

test('enrage is sticky — idle/swim requests resolve to enraged loop after threshold', () => {
  const scene = makeMockEntityScene('gold_wolf');
  const entity = new CombatEntity(scene, 'gold_wolf', 0, 0);
  const cfg = getCreature('gold_wolf');

  const dmgToTriggerEnrage = entity.maxHealth - Math.floor(entity.maxHealth * cfg.enrageThreshold) + 1;
  entity.takeDamage(dmgToTriggerEnrage);
  assert.equal(entity.isEnrageLocked, true, 'enrage should lock once health crosses threshold');

  // hit animation completes -> should return to ENRAGED, not IDLE
  entity.sprite.emit('animationcomplete', { key: 'gold_wolf__hit' });
  assert.equal(entity.state, CombatState.ENRAGED);

  // explicit idle/swim requests should also resolve to enraged
  entity.playState(CombatState.IDLE);
  assert.equal(entity.state, CombatState.ENRAGED, 'idle request should resolve to enraged once locked');

  entity.playState(CombatState.SWIM);
  assert.equal(entity.state, CombatState.ENRAGED, 'swim request should resolve to enraged once locked');
});

test('onHealthChange and onDeath callbacks fire with correct values', () => {
  const scene = makeMockEntityScene('gold_wolf');
  const entity = new CombatEntity(scene, 'gold_wolf', 0, 0);

  let lastHealth = null, lastMax = null;
  entity.onHealthChange = (h, m) => { lastHealth = h; lastMax = m; };

  entity.takeDamage(5);
  assert.equal(lastHealth, entity.maxHealth - 5);
  assert.equal(lastMax, entity.maxHealth);

  let deathFired = false;
  entity.onDeath = () => { deathFired = true; };
  entity.takeDamage(9999);
  entity.sprite.emit('animationcomplete', { key: 'gold_wolf__death' });
  assert.equal(deathFired, true, 'onDeath should fire after death animation completes');
});

test('missing-animation fallback plays idle instead of throwing', () => {
  // CombatEntity's constructor calls getCreature(), which correctly refuses
  // unregistered creature ids (verified in the "getCreature throws" test
  // above) — so to test the fallback behavior we register a temporary
  // creature in CREATURES first, matching how a real partial-art creature
  // would actually be onboarded (registry entry now, remaining frames later).
  const partialFrames = ['fallback_test__idle__0', 'fallback_test__idle__1'];
  const scene = new MockScene({ fallback_test: partialFrames });
  const fakeConfig = {
    id: 'fallback_test', displayName: 'Fallback Test Creature', role: 'minion',
    frameWidth: 128, frameHeight: 128,
    animFps: { idle: 6 }, scale: 1, baseHealth: 10, baseSpeed: 10, enrageThreshold: 0.3,
  };
  CREATURES.fallback_test = fakeConfig; // temporary registration, cleaned up below
  buildCreatureAnimations(scene, 'fallback_test', fakeConfig);

  try {
    const entity = new CombatEntity(scene, 'fallback_test', 0, 0);
    assert.doesNotThrow(() => entity.attack());
    assert.equal(entity.sprite.currentAnim, 'fallback_test__idle', 'should fall back to idle animation key');
  } finally {
    delete CREATURES.fallback_test; // don't leak test fixtures into the real registry
  }
});

// ---- Summary ---------------------------------------------------------------

console.log(`\n${passCount} passed, ${failCount} failed\n`);
if (failCount > 0) process.exit(1);
