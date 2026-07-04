import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * BulletPool: Manages recycling and reusing bullet objects for efficiency.
 */
export class BulletPool {
  constructor(options) {
    this.options = {
      maxBullets: 100, // Maximum bullets allowed in pool
      bulletTexture: PIXI.Texture.WHITE, // Placeholder texture (replace with actual texture)
      trailEffect: null, // Optional trail effect
      ...options,
    };

    this.pool = []; // Array to store bullet instances
    this.activeBullets = []; // Bullets currently in use
  }

  /**
   * Initializes the bullet pool with preloaded bullet instances.
   */
  initialize(stage) {
    for (let i = 0; i < this.options.maxBullets; i++) {
      const bullet = new PIXI.Sprite(this.options.bulletTexture);
      bullet.visible = false;
      bullet.anchor.set(0.5);
      this.pool.push(bullet);
      stage.addChild(bullet);
    }
  }

  /**
   * Fires a bullet from the pool.
   * @param {object} props - Bullet properties (position, angle, speed).
   */
  fire(props) {
    if (this.pool.length === 0) return; // No bullets available

    const bullet = this.pool.pop();
    bullet.visible = true;
    bullet.x = props.x;
    bullet.y = props.y;
    bullet.rotation = props.angle;

    const speed = props.muzzleVelocity || 20;

    // Easing to make it feel "powerful"
    gsap.to(bullet, {
      x: `+=${Math.cos(props.angle) * speed}`,
      y: `+=${Math.sin(props.angle) * speed}`,
      duration: 0.3,
      ease: 'power2.out',
      onComplete: () => {
        this.remove(bullet);
      },
    });

    this.activeBullets.push(bullet);
  }

  /**
   * Removes a bullet from the active bullets array and places it back in the pool.
   * @param {PIXI.Sprite} bullet - The bullet to be returned to the pool.
   */
  remove(bullet) {
    bullet.visible = false;
    this.activeBullets = this.activeBullets.filter((b) => b !== bullet);
    this.pool.push(bullet);
  }

  /**
   * Updates trail or additional effects per frame.
   * @param {number} delta - Delta time for updates.
   */
  update(delta) {
    if (this.options.trailEffect) {
      this.activeBullets.forEach((bullet) => {
        this.options.trailEffect.update(bullet, delta);
      });
    }
  }
}

export default BulletPool;