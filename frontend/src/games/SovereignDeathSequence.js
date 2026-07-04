import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * Sovereign Death Sequence: Handles fish death visuals and coin absorption.
 */
export class SovereignDeathSequence {
  constructor(hudBalancePosition, app) {
    this.hudBalancePosition = hudBalancePosition; // Position of balance HUD
    this.app = app;
    this.coinContainer = new PIXI.ParticleContainer(100, {
      scale: true,
      position: true,
      rotation: true,
      uvs: true,
      alpha: true,
    });

    this.app.stage.addChild(this.coinContainer);
  }

  /**
   * Triggers the death sequence for a fish.
   * @param {PIXI.DisplayObject} fish - The fish that died.
   */
  trigger(fish) {
    const coins = []; // To track active coins
    const startX = fish.x;
    const startY = fish.y;

    // Spawn 10 rotating coins
    for (let i = 0; i < 10; i++) {
      const coin = new PIXI.Sprite(PIXI.Texture.from('input_file_12')); // Gold coin texture
      coin.anchor.set(0.5);
      coin.x = startX;
      coin.y = startY;
      coin.rotation = Math.random() * Math.PI * 2; // Random rotation
      coin.scale.set(0.5);

      this.coinContainer.addChild(coin);
      coins.push(coin);

      // Animate coin along parabolic arc
      this._animateCoin(coin, i, () => {
        // Coin reached HUD
        this._absorbCoin(coin, i);
      });
    }
  }

  /**
   * Animates a coin along a parabolic trajectory to the balance HUD.
   * @param {PIXI.Sprite} coin - Coin to animate.
   * @param {number} index - Coin index (for delay).
   * @param {Function} onComplete - Callback when coin reaches destination.
   */
  _animateCoin(coin, index, onComplete) {
    const targetX = this.hudBalancePosition.x;
    const targetY = this.hudBalancePosition.y;
    const controlX = coin.x + Math.random() * 100 - 50;
    const controlY = coin.y - Math.random() * 150 - 100;

    gsap.to(coin, {
      motionPath: {
        path: [
          { x: coin.x, y: coin.y },
          { x: controlX, y: controlY },
          { x: targetX, y: targetY },
        ],
        curviness: 1.5,
      },
      rotation: '+=6.28', // Full rotation during path
      duration: 1.5,
      ease: 'power2.out',
      onComplete: onComplete,
    });
  }

  /**
   * Absorbs a coin into the balance HUD, triggering visual and audio feedback.
   * @param {PIXI.Sprite} coin - Coin being absorbed.
   * @param {number} coinIndex - Index to compute audio pitch.
   */
  _absorbCoin(coin, coinIndex) {
    this.coinContainer.removeChild(coin);

    // Pulse the balance HUD
    const hudBalance = this.hudBalancePosition.displayObject; // The HUD balance sprite or container
    gsap.to(hudBalance.scale, {
      x: 1.1,
      y: 1.1,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      ease: 'power2.out',
    });

    // Play chime sound with increasing pitch
    const pitch = 800 + coinIndex * 100; // Base pitch + incremental increase
    SLA113.playSound('chime', { pitch });
  }
}

export default SovereignDeathSequence;