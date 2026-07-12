/**
 * ProjectileManager.js
 *
 * Pooled projectile group. Spawns from CannonController, checks overlap
 * against whatever CombatEntity list the scene registers, and triggers
 * ImpactFxManager + CoinFxManager on a successful hit. Pooling (reuse dead
 * bullets instead of destroy/recreate) matters here because a fish-shooter
 * can have dozens of bullets in flight at once.
 *
 * Supports more than one projectile type (contract section 5:
 * `projectile__<type>__<index>`) — each type has its own speed/damage,
 * looked up at spawn time so CannonController can pick a type per shot
 * (e.g. an upgraded harpoon during a combo) without ProjectileManager
 * knowing why.
 */

export class ProjectileManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object} opts
   * @param {number} [opts.speed=600] bolt speed
   * @param {number} [opts.damage=5] bolt damage
   * @param {number} [opts.harpoonSpeed=420]
   * @param {number} [opts.harpoonDamage=18]
   * @param {number} [opts.maxLifeMs=2000]
   */
  constructor(scene, opts = {}) {
    this.scene = scene;
    this.maxLifeMs = opts.maxLifeMs ?? 2000;

    this.projectileTypes = {
      bolt: { speed: opts.speed ?? 600, damage: opts.damage ?? 5 },
      harpoon: { speed: opts.harpoonSpeed ?? 420, damage: opts.harpoonDamage ?? 18 },
    };

    this.group = scene.physics.add.group({
      defaultKey: 'projectiles',
      defaultFrame: 'projectile__bolt__0',
      maxSize: 60,
    });

    /** @type {CombatEntity[]} populated by the scene each frame or on spawn/death */
    this.targets = [];

    this.onHitTarget = null; // scene can hook this for score/combo logic
  }

  setTargets(combatEntities) {
    this.targets = combatEntities;
  }

  spawn(x, y, angle, type = 'bolt') {
    const spec = this.projectileTypes[type] || this.projectileTypes.bolt;
    const frame = `projectile__${type}__0`;
    const animKey = `projectile__${type}`;

    const bullet = this.group.get(x, y, 'projectiles', frame);
    if (!bullet) return null; // pool exhausted, drop silently rather than error mid-combat

    bullet.setActive(true).setVisible(true);
    bullet.body.reset(x, y);
    bullet.setRotation(angle + Math.PI / 2);
    bullet.setFrame(frame);

    if (this.scene.anims.exists(animKey)) {
      bullet.play(animKey);
    }

    const vx = Math.cos(angle) * spec.speed;
    const vy = Math.sin(angle) * spec.speed;
    bullet.body.setVelocity(vx, vy);

    bullet._spawnedAt = this.scene.time.now;
    bullet._damage = spec.damage;
    return bullet;
  }

  /** Call once per frame from the scene's update loop. */
  update() {
    const now = this.scene.time.now;

    this.group.children.each((bullet) => {
      if (!bullet.active) return;

      if (now - bullet._spawnedAt > this.maxLifeMs || this._isOffscreen(bullet)) {
        this._recycle(bullet);
        return;
      }

      for (const entity of this.targets) {
        if (entity.isDead) continue;
        const dist = Phaser.Math.Distance.Between(
          bullet.x, bullet.y, entity.sprite.x, entity.sprite.y
        );
        const hitRadius = 30 * (entity.config.scale || 1);
        if (dist < hitRadius) {
          this._onHit(bullet, entity);
          return;
        }
      }
    });
  }

  _isOffscreen(bullet) {
    const cam = this.scene.cameras.main;
    return (
      bullet.x < -50 || bullet.x > cam.width + 50 ||
      bullet.y < -50 || bullet.y > cam.height + 50
    );
  }

  _onHit(bullet, entity) {
    entity.takeDamage(bullet._damage ?? this.projectileTypes.bolt.damage);
    if (this.onHitTarget) this.onHitTarget(entity, bullet);
    this._recycle(bullet);
  }

  _recycle(bullet) {
    bullet.setActive(false).setVisible(false);
    bullet.body.setVelocity(0, 0);
  }
}
