import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { PixiParticleEmitter } from 'pixi-particles';
import { BloomFilter } from '@pixi/filter-bloom';

/**
 * Spirit Skull Homing Module
 */
export class SpiritSkull {
  constructor(container, fishArray) {
    this.container = container; // Game container
    this.fishArray = fishArray; // List of fish available for targeting

    // Spirit Skull Properties
    this.skull = new PIXI.Sprite(PIXI.Texture.from('spirit_skull_asset')); // Replace with Vertex AI asset texture
    this.skull.anchor.set(0.5);
    this.skull.x = 0;
    this.skull.y = 0;
    this.skull.velocity = { x: 0, y: -10 }; // Initial velocity (upward)
    this.maxForce = 1; // Steering force limit for turning radius
    this.maxSpeed = 10; // Constant forward speed

    // Bloom Filter for Neon Glow
    this.skull.filters = [new BloomFilter({ threshold: 0.5, bloomScale: 2 })];

    // Particle Trail
    this.particleContainer = new PIXI.ParticleContainer();
    this.container.addChild(this.particleContainer);

    this.container.addChild(this.skull);
    this.target = null; // Target to home in on
  }

  /**
   * Finds the highest value target in range (within 500px).
   */
  findHighestValueTarget() {
    let bestTarget = null;
    let bestValue = 0;

    this.fishArray.forEach((fish) => {
      const distance = Math.hypot(fish.x - this.skull.x, fish.y - this.skull.y);
      if (distance <= 500 && fish.value > bestValue) {
        bestValue = fish.value;
        bestTarget = fish;
      }
    });

    this.target = bestTarget;
  }

  /**
   * Updates the Spirit Skull's steering behavior.
   */
  update(delta) {
    if (!this.target) return;

    // Calculate desired direction toward the target
    const desired = {
      x: this.target.x - this.skull.x,
      y: this.target.y - this.skull.y,
    };
    const distance = Math.hypot(desired.x, desired.y);

    // Normalize and scale to maxSpeed
    desired.x = (desired.x / distance) * this.maxSpeed;
    desired.y = (desired.y / distance) * this.maxSpeed;

    // Compute the steering force
    const steer = {
      x: desired.x - this.skull.velocity.x,
      y: desired.y - this.skull.velocity.y,
    };
    const steerForce = Math.hypot(steer.x, steer.y);
    if (steerForce > this.maxForce) {
      steer.x = (steer.x / steerForce) * this.maxForce;
      steer.y = (steer.y / steerForce) * this.maxForce;
    }

    // Apply steering to velocity
    this.skull.velocity.x += steer.x;
    this.skull.velocity.y += steer.y;

    // Move the skull
    this.skull.x += this.skull.velocity.x * delta;
    this.skull.y += this.skull.velocity.y * delta;

    // Spawn trail particles
    this._spawnTrail();

    // Check for impact
    if (distance <= 10) {
      this._onHit(this.target);
    }
  }

  /**
   * Spawns particles for the Spirit Skull's trail.
   */
  _spawnTrail() {
    const particle = new PIXI.Sprite(PIXI.Texture.from('neon_trail_asset')); // Replace with trail texture
    particle.anchor.set(0.5);
    particle.x = this.skull.x;
    particle.y = this.skull.y;
    particle.alpha = 0.8;
    particle.scale.set(0.5);

    gsap.to(particle, {
      alpha: 0,
      scaleX: 0.1,
      scaleY: 0.1,
      duration: 0.5,
      onComplete: () => {
        this.particleContainer.removeChild(particle);
      },
    });

    this.particleContainer.addChild(particle);
  }

  /**
   * Handles Spirit Skull impact with the target.
   */
  _onHit(target) {
    // Trigger SovereignImpact
    this._impactWithPhysics(target);

    // Remove skull from play
    this.container.removeChild(this.skull);
    this.target = null; // Reset target
  }

  /**
   * Triggers SovereignImpact effects (Flash + Shake + Coins).
   */
  _impactWithPhysics(target) {
    // Flash target white
    const flashFilter = new PIXI.filters.ColorMatrixFilter();
    target.filters = [flashFilter];
    flashFilter.brightness(2, false);
    gsap.to(flashFilter, {
      brightness: 1,
      duration: 0.06,
      onComplete: () => {
        target.filters = null;
      },
    });

    // Radial screen shake
    gsap.to(this.container, {
      x: '+=10',
      y: '+=10',
      yoyo: true,
      repeat: 5,
      duration: 0.05,
      onComplete: () => {
        gsap.to(this.container, { x: 0, y: 0, duration: 0.1 });
      },
    });

    // Coin burst
    const coins = new PixiParticleEmitter({
      particleTexture: PIXI.Texture.from('coin_asset'),
      startAlpha: 1,
      startScale: 0.5,
      endScale: 1.5,
    });
    coins.play(target.x, target.y);
    this.container.addChild(coins.container);
  }

  /**
   * Play ghostly whistle, pitching up as the skull nears.
   */
  playGhostlyWhistle(distance) {
    const pitch = Math.max(1000, 4000 - distance * 6); // Increases as target gets closer
    SLA113.playSound('ghostly_whistle', { pitch });
  }
}

export default SpiritSkull;