/**
 * CannonController.js
 *
 * Player-facing cannon: tracks pointer for aim rotation, plays the fire
 * animation on shoot, and hands off to ProjectileManager for the actual
 * bullet. Kept separate from ProjectileManager so swapping cannon skins
 * (multiple players in a fish-shooter lobby) never touches projectile logic.
 */

export class CannonController {
  /**
   * @param {Phaser.Scene} scene
   * @param {number} x
   * @param {number} y
   * @param {ProjectileManager} projectileManager
   * @param {object} [opts]
   * @param {number} [opts.fireCooldownMs=220]
   * @param {() => string} [opts.getProjectileType] called each shot to pick
   *   the projectile type (e.g. upgrade to 'harpoon' on a combo streak);
   *   defaults to always firing 'bolt'.
   */
  constructor(scene, x, y, projectileManager, opts = {}) {
    this.scene = scene;
    this.x = x;
    this.y = y;
    this.projectileManager = projectileManager;
    this.fireCooldownMs = opts.fireCooldownMs ?? 220;
    this.getProjectileType = opts.getProjectileType ?? (() => 'bolt');
    this._lastFireAt = 0;

    this.sprite = scene.add.sprite(x, y, 'cannon', 'cannon__fire__0');
    this.sprite.setOrigin(0.5, 0.75);

    scene.input.on('pointermove', (pointer) => this._aimAt(pointer.x, pointer.y));
    scene.input.on('pointerdown', (pointer) => this.fire(pointer.x, pointer.y));
  }

  _aimAt(targetX, targetY) {
    const angle = Phaser.Math.Angle.Between(this.x, this.y, targetX, targetY);
    this.sprite.setRotation(angle + Math.PI / 2);
    this._aimAngle = angle;
  }

  fire(targetX, targetY) {
    const now = this.scene.time.now;
    if (now - this._lastFireAt < this.fireCooldownMs) return false;
    this._lastFireAt = now;

    this._aimAt(targetX, targetY);

    if (this.scene.anims.exists('cannon__fire')) {
      this.sprite.play('cannon__fire');
    }

    const type = this.getProjectileType();
    this.projectileManager.spawn(this.x, this.y, this._aimAngle ?? -Math.PI / 2, type);
    return true;
  }
}
