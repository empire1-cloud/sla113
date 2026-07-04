import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * Sovereign Ballistics Engine: Gun Rig (GunContainer)
 */
export class GunContainer extends PIXI.Container {
  constructor(options) {
    super();

    this.options = {
      recoilDistance: 20, // Distance to move back on hydraulic recoil
      ...options, // Merge user options
    };

    this.pivot.set(0.5, 1); // Pivot at bottom center
    this.gunSprite = new PIXI.Sprite(PIXI.Texture.from(this.options.gunTexture)); // Placeholder for gun texture
    this.gunSprite.anchor.set(0.5, 1);
    this.addChild(this.gunSprite);

    // Add additional visuals for the double-barrel effect or decorative features
  }

  /**
   * Fires the gun with recoil animation and callbacks.
   */
  fire(onComplete = () => {}) {
    gsap.to(this.gunSprite, {
      y: `-=${this.options.recoilDistance}`,
      duration: 0.15,
      ease: 'power2.out',
      yoyo: true,
      repeat: 1,
      onComplete: () => {
        // Callback after recoil animation (e.g., spawn bullet)
        onComplete();
      },
    });
  }
}

export default GunContainer;