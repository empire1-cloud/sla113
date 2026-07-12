/**
 * CombatEntity.js
 *
 * Wraps a Phaser sprite with the idle/swim/attack/hit/enraged/death state
 * machine. One class, used for every minion AND every boss — role-specific
 * behavior (boss health-bar wiring, bigger scale) is composition via
 * CreatureRegistry config, not subclassing per creature.
 *
 * State transition rules (this is the actual logic, not just animation
 * swapping):
 *   - death is terminal: once entered, no other transition is accepted.
 *   - hit does not cancel an in-progress attack windup; it queues after.
 *   - enraged is sticky: once health crosses enrageThreshold, every future
 *     idle/swim call resolves to the enraged variant instead, until death.
 *   - attack and hit are non-looping; on animationcomplete they fall back
 *     to enraged-idle or idle depending on current health fraction.
 */

import { getCreature } from './CreatureRegistry.js';

export const CombatState = Object.freeze({
  IDLE: 'idle',
  SWIM: 'swim',
  ATTACK: 'attack',
  HIT: 'hit',
  ENRAGED: 'enraged',
  DEATH: 'death',
});

export class CombatEntity {
  /**
   * @param {Phaser.Scene} scene
   * @param {string} creatureId
   * @param {number} x
   * @param {number} y
   * @param {object} [overrides] — optional per-instance stat overrides (e.g. difficulty scaling)
   */
  constructor(scene, creatureId, x, y, overrides = {}) {
    this.scene = scene;
    this.creatureId = creatureId;
    this.config = getCreature(creatureId);

    this.maxHealth = overrides.health ?? this.config.baseHealth;
    this.health = this.maxHealth;
    this.speed = overrides.speed ?? this.config.baseSpeed;

    this.state = CombatState.IDLE;
    this.isEnrageLocked = false; // once true, idle/swim resolve to enraged variants
    this.isDead = false;
    this._queuedHitAfterAttack = false;

    this.sprite = scene.physics.add.sprite(x, y, creatureId);
    this.sprite.setScale(this.config.scale);
    this.sprite.setOrigin(0.5, 0.92); // bottom-center-ish anchor, matches contract section 2

    this.onDeath = null;      // external callback, set by spawner
    this.onHealthChange = null; // external callback, e.g. boss health bar hookup

    this._bindAnimationEvents();
    this.playState(CombatState.IDLE);
  }

  _bindAnimationEvents() {
    this.sprite.on('animationcomplete', (anim) => {
      const state = this._stateFromAnimKey(anim.key);
      if (state === CombatState.DEATH) {
        this._finalizeDeath();
        return;
      }
      if (state === CombatState.ATTACK || state === CombatState.HIT) {
        if (this._queuedHitAfterAttack) {
          this._queuedHitAfterAttack = false;
          this._playRaw(CombatState.HIT);
          return;
        }
        this._returnToRestingState();
      }
    });
  }

  _stateFromAnimKey(animKey) {
    // animKey shape: "<creatureId>__<state>"
    const parts = animKey.split('__');
    return parts[parts.length - 1];
  }

  _returnToRestingState() {
    this.playState(this.isEnrageLocked ? CombatState.ENRAGED : CombatState.IDLE);
  }

  /**
   * Public entry point for requesting a state transition. Applies the
   * transition rules described in the file header instead of blindly
   * playing whatever was asked for.
   */
  playState(requestedState) {
    if (this.isDead) return; // death is terminal, contract rule

    if (requestedState === CombatState.HIT && this.state === CombatState.ATTACK) {
      // Don't cancel an attack windup; queue the hit reaction after it completes.
      this._queuedHitAfterAttack = true;
      return;
    }

    if (
      (requestedState === CombatState.IDLE || requestedState === CombatState.SWIM) &&
      this.isEnrageLocked
    ) {
      // Enrage is sticky — idle/swim requests resolve to the enraged loop instead.
      this._playRaw(CombatState.ENRAGED);
      return;
    }

    this._playRaw(requestedState);
  }

  _playRaw(state) {
    this.state = state;
    const animKey = `${this.creatureId}__${state}`;
    if (this.scene.anims.exists(animKey)) {
      this.sprite.play(animKey);
    } else {
      // Missing-state fallback (AnimationBuilder already warned at load time).
      // Falling back to idle keeps the entity visibly alive instead of
      // freezing on a blank frame or throwing mid-combat.
      const fallbackKey = `${this.creatureId}__${CombatState.IDLE}`;
      if (this.scene.anims.exists(fallbackKey)) {
        this.sprite.play(fallbackKey);
      }
    }
  }

  /**
   * Applies damage, fires the hit reaction (unless it's a killing blow, which
   * goes straight to death), and evaluates the enrage threshold.
   */
  takeDamage(amount) {
    if (this.isDead) return;

    this.health = Math.max(0, this.health - amount);
    if (this.onHealthChange) this.onHealthChange(this.health, this.maxHealth);

    if (this.health <= 0) {
      this._die();
      return;
    }

    const healthFraction = this.health / this.maxHealth;
    if (!this.isEnrageLocked && healthFraction <= this.config.enrageThreshold) {
      this.isEnrageLocked = true;
    }

    this.playState(CombatState.HIT);
  }

  attack() {
    if (this.isDead) return;
    this.playState(CombatState.ATTACK);
  }

  _die() {
    this.isDead = true;
    this._queuedHitAfterAttack = false;
    this.state = CombatState.DEATH;
    this.sprite.body.setVelocity(0, 0);
    const animKey = `${this.creatureId}__${CombatState.DEATH}`;
    if (this.scene.anims.exists(animKey)) {
      this.sprite.play(animKey);
    } else {
      this._finalizeDeath();
    }
  }

  _finalizeDeath() {
    if (this.onDeath) this.onDeath(this);
  }

  destroy() {
    this.sprite.destroy();
  }
}
