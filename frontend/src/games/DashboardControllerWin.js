import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { PixiParticleEmitter } from 'pixi-particles';

/**
 * DashboardController with Win Animation
 */
export class DashboardController {
  constructor(container) {
    this.container = container;
    this.gauges = []; // Array of gauges

    // Add gauges
    this._createGauges();

    // Headlights
    this.headlights = new PIXI.Container();
    this._addHeadlights();
  }

  /** Creates gauges. */
  _createGauges() {
    // Placeholder code for gauge creation
    // Add logic to build gauges and needles here
  }

  /** Adds flashing headlights to the UI. */
  _addHeadlights() {
    const leftLight = new PIXI.Sprite(PIXI.Texture.from('chrome_gauge_vertex_ai_asset')); // Add proper textures here
    const rightLight = new PIXI.Sprite(PIXI.Texture.from('chrome_gauge_vertex_ai_asset'));

    [leftLight, rightLight].forEach((light, i) => {
      light.anchor.set(0.5);
      light.alpha = 0;
      light.x = i === 0 ? -200 : 200;
      this.headlights.addChild(light);
    });

    this.container.addChild(this.headlights);
  }

  /** Triggers win animation with sparks and flashing headlights. */
  triggerWinAnimation() {
    // 1. Animate needles to redline and spark
    this.gauges.forEach((gauge) => {
      const needle = gauge.needle; // Assume each gauge has a needle
      gsap.to(needle, {
        rotation: Math.PI / 2, // Example redline rotation
        duration: 1,
        onComplete: () => {
          this._createSparks(gauge);
        },
      });
    });

    // 2. Flash headlights (UI effect)
    this._flashHeadlights();
  }

  /** Creates sparks at needle redline. */
  _createSparks(gauge) {
    const sparks = new PixiParticleEmitter({
      // Particle emitter configuration (customize for sparks)
      startAlpha: 1,
      startScale: 0.5,
    });
    sparks.play(gauge.x, gauge.y); // Position at gauge
    this.container.addChild(sparks.container);
  }

  /** Flashes headlights. */
  _flashHeadlights() {
    this.headlights.children.forEach((light) => {
      gsap.to(light, {
        alpha: 1,
        duration: 0.1,
        repeat: 5,
        yoyo: true,
      });
    });
  }
}

export default DashboardController;