import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

// CircularController Class
export class CircularController {
  constructor(container, options) {
    // Container for the concentric rings
    this.container = container;

    // Default options
    this.options = {
      numberOfRings: 3,       // Number of concentric rings
      ringRadius: [100, 200, 300],     // Radii of the rings
      rotationSpeeds: [0.5, 1, 1.5],   // Rotation speed for each ring
      ringTextures: [],       // Placeholder for ring symbols
      ...options,            // Merge with user-defined options
    };

    this.rings = []; // Array to store ring containers

    // Initialization
    this._createRings();
  }

  /**
   * Creates the concentric rings with symbols.
   */
  _createRings() {
    for (let i = 0; i < this.options.numberOfRings; i++) {
      const ring = new PIXI.Container();
      ring.radius = this.options.ringRadius[i];
      ring.rotationSpeed = this.options.rotationSpeeds[i];
      this._populateRing(ring, i);
      this.rings.push(ring);
      this.container.addChild(ring);
    }
  }

  /**
   * Populates a ring with symbols.
   * @param {PIXI.Container} ring - The ring to populate.
   * @param {number} ringIndex - Index of the ring.
   */
  _populateRing(ring, ringIndex) {
    const texture = this.options.ringTextures[ringIndex];
    const symbolsCount = 8; // Adjust as necessary

    for (let i = 0; i < symbolsCount; i++) {
      const angle = (i / symbolsCount) * Math.PI * 2;
      const symbol = new PIXI.Sprite(texture);
      symbol.anchor.set(0.5);
      symbol.x = Math.cos(angle) * ring.radius;
      symbol.y = Math.sin(angle) * ring.radius;

      // Ensure symbols stay upright
      symbol.rotation = angle + Math.PI / 2;

      ring.addChild(symbol);
    }
  }

  /**
   * Starts the ring rotation animations.
   */
  startRotation() {
    this.rings.forEach((ring) => {
      gsap.to(ring, {
        rotation: `+=${Math.PI * 2}`,
        repeat: -1,
        ease: 'linear',
        duration: ring.rotationSpeed,
      });
    });
  }

  /**
   * Stops the rotation of all rings.
   */
  stopRotation() {
    this.rings.forEach((ring) => {
      gsap.killTweensOf(ring);
    });
  }

  /**
   * Update method to adjust symbol positions dynamically during gameplay.
   */
  update(delta) {
    this.rings.forEach((ring) => {
      ring.children.forEach((symbol) => {
        const angle = Math.atan2(symbol.y, symbol.x);
        symbol.rotation = angle + Math.PI / 2;
      });
    });
  }
}

export default CircularController;