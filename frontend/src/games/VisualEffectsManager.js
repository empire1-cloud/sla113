import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { MotionBlurFilter } from '@pixi/filter-motion-blur';
import { DropShadowFilter } from '@pixi/filter-drop-shadow';

/**
 * VisualEffectsManager: Manages motion blur, drop shadows, and screen tints.
 */
export class VisualEffectsManager {
  constructor(app) {
    this.app = app;
    this.screenFilter = new PIXI.filters.ColorMatrixFilter();
    this.activeFrenzyTint = false; // Track if Frenzy Tint is active
    app.stage.filters = [this.screenFilter];
  }

  /**
   * Apply motion blur dynamically based on fish velocity.
   * @param {PIXI.Sprite} fish - The fish sprite to blur.
   * @param {number} velocity - The velocity of the fish (speed).
   */
  applyMotionBlur(fish, velocity) {
    const blurIntensity = Math.min(velocity / 10, 8); // Limit blur intensity

    if (!fish.filters) {
      fish.filters = []; // Ensure filters are initialized
    }

    let blurFilter = fish.filters.find((filter) => filter instanceof MotionBlurFilter);

    if (!blurFilter) {
      blurFilter = new MotionBlurFilter(velocity, 0);
      fish.filters.push(blurFilter);
    }

    blurFilter.velocity = velocity; // Update velocity dynamically
    blurFilter.blur = blurIntensity;

    // Remove blur entirely if velocity is zero
    if (velocity === 0) {
      fish.filters = fish.filters.filter((filter) => !(filter instanceof MotionBlurFilter));
    }
  }

  /**
   * Add a drop shadow underneath the fish sprite to simulate depth.
   * @param {PIXI.Sprite} fish - The fish sprite to shadow.
   */
  applyDropShadow(fish) {
    if (!fish.filters) {
      fish.filters = []; // Ensure filters are initialized
    }

    let shadowFilter = fish.filters.find((filter) => filter instanceof DropShadowFilter);

    if (!shadowFilter) {
      shadowFilter = new DropShadowFilter();
      shadowFilter.distance = 4;
      shadowFilter.alpha = 0.8; // Shadow opacity
      shadowFilter.blur = 5; // Soft blur
      shadowFilter.color = 0x000000;

      fish.filters.push(shadowFilter);
    }

    // Shadow position updates dynamically as fish moves
    shadowFilter.distance = 10 + Math.min(Math.abs(fish.y - this.app.screen.height / 2) / 50, 20);
  }

  /**
   * Apply a red or gold tint to the screen during Frenzy Mode.
   * @param {string} tint - The tint color ('red' or 'gold').
   */
  applyScreenTint(tint) {
    if (this.activeFrenzyTint) return; // Avoid duplicate tints

    this.activeFrenzyTint = true;

    const tintMatrix = tint === 'red'
      ? [
          1.2, 0.2, 0.2, 0, 0, // Enhance Red
          0.1, 0.2, 0.1, 0, 0,
          0, 0.2, 0.3, 0, 0,
          0, 0, 0, 1, 0,
        ]
      : [
          1.2, 1.0, 0.4, 0, 0, // Red-Yellow
          0.5, 1.5, 0.2, 0, 0,
          0.3, 0.9, 0.2, 0, 0,
          0, 0, 0, 1, 0,
        ];

    gsap.to(this.screenFilter, {
      matrix: tintMatrix,
      duration: 0.5,
    });
  }

  /**
   * Remove the Frenzy Mode screen tint (reset color).
   */
  clearScreenTint() {
    gsap.to(this.screenFilter, {
      matrix: [
        1, 0, 0, 0, 0,
        0, 1, 0, 0, 0,
        0, 0, 1, 0, 0,
        0, 0, 0, 1, 0,
      ],
      duration: 0.5,
      onComplete: () => {
        this.activeFrenzyTint = false;
      },
    });
  }
}

export default VisualEffectsManager;