import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { PixiParticleEmitter } from 'pixi-particles';

/**
 * CalendarController with Win Animation
 */
export class CalendarController {
  constructor(container) {
    this.container = container;
    this.rings = []; // Concentric rings

    // Add rings
    this._createRings();

    // Add center face for gold coin animation
    this.centerFace = this._createCenterFace();
    this.container.addChild(this.centerFace);
  }

  /** Creates rotating rings. */
  _createRings() {
    // Placeholder for ring creation
    // Add logic to build rotating rings here
  }

  /** Creates the center face for animation. */
  _createCenterFace() {
    const face = new PIXI.Container();
    const faceTexture = PIXI.Sprite.from('aztec_stone_face_vertex_ai_asset'); // Replace with actual texture
    face.addChild(faceTexture);
    return face;
  }

  /** Triggers the win animation. */
  triggerWinAnimation() {
    // 1. Open center face's mouth
    this._openFaceMouth();

    // 2. Emit gold coins
    this._emitGoldCoins();
  }

  /** Opens the center face's mouth. */
  _openFaceMouth() {
    gsap.to(this.centerFace.scale, {
      y: 1.2,
      duration: 0.5,
      yoyo: true,
      repeat: 1,
    });
  }

  /** Emits gold coins from the center. */
  _emitGoldCoins() {
    const coins = new PixiParticleEmitter({
      // Particle emitter configuration (customize for coins)
      particleTexture: PIXI.Texture.from('rotating_gold_coins_vertex_ai_asset'),
      startAlpha: 1,
      startScale: 0.8,
    });
    coins.play(this.centerFace.x, this.centerFace.y); // Position at the mouth
    this.container.addChild(coins.container);
  }
}

export default CalendarController;