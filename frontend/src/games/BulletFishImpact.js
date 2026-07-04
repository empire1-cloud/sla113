import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * Handles the visual and physical feedback of bullet collisions with fish.
 * Includes impact vector, jiggle animation, white flash, and spark effects.
 */
export function handleBulletFishImpact(bullet, fish, particleContainer) {
  // Calculate the impact vector (opposite of bullet velocity)
  const impactVector = {
    x: bullet.velocity.x * -1,
    y: bullet.velocity.y * -1,
  };

  const distance = Math.hypot(impactVector.x, impactVector.y);
  impactVector.x /= distance; // Normalize vector
  impactVector.y /= distance;

  // Jiggle the fish away from the point of impact
  const jiggleDistance = 10; // Distance to jiggle

  gsap.to(fish, {
    x: `+=${impactVector.x * jiggleDistance}`,
    y: `+=${impactVector.y * jiggleDistance}`,
    duration: 0.1,
    ease: 'back.out',
  });

  // Flash white for 2 frames (60 ms)
  const flashFilter = new PIXI.filters.ColorMatrixFilter();
  flashFilter.brightness(2, false);
  fish.filters = [flashFilter];
  gsap.to(flashFilter, {
    brightness: 1,
    duration: 0.06,
    onComplete: () => {
      fish.filters = null;
    },
  });

  // Spawn spark particle
  spawnSparkParticle(bullet, particleContainer);
}

/**
 * Spawns a spark particle that flies away from the point of impact.
 */
function spawnSparkParticle(bullet, particleContainer) {
  const spark = new PIXI.Sprite(PIXI.Texture.from('spark_asset')); // Replace with actual texture
  spark.anchor.set(0.5);
  spark.x = bullet.x;
  spark.y = bullet.y;
  spark.scale.set(0.3);

  const sparkVelocity = {
    x: bullet.velocity.x * -0.5, // Opposite and slower velocity
    y: bullet.velocity.y * -0.5,
  };

  gsap.to(spark, {
    x: `+=${sparkVelocity.x * 20}`,
    y: `+=${sparkVelocity.y * 20}`,
    alpha: 0,
    scaleX: 0.1,
    scaleY: 0.1,
    duration: 0.5,
    onComplete: () => {
      particleContainer.removeChild(spark);
    },
  });

  particleContainer.addChild(spark);
}