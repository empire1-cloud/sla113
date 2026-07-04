import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * CalendarController
 * Manages 3 concentric rotating rings for the Calendar slot layout.
 */
export class CalendarController {
  constructor(container) {
    this.container = container;
    this.rings = []; // Array of concentric rings

    // Fixed 16:9 aspect ratio
    this.containerWidth = 1920;
    this.containerHeight = 1080;

    // Create the layer-locked background
    this._addBackground();

    // Create and layout 3 concentric rings
    this._createRings();
  }

  /** Adds a static layer-locked background. */
  _addBackground() {
    const background = PIXI.Sprite.from('input_file_16'); // Placeholder background texture
    background.anchor.set(0.5);
    background.x = this.containerWidth / 2;
    background.y = this.containerHeight / 2;
    background.width = this.containerWidth;
    background.height = this.containerHeight;
    this.container.addChild(background);
  }

  /** Creates the 3 concentric rings. */
  _createRings() {
    const radii = [150, 300, 450];
    radii.forEach((radius, index) => {
      const ring = new PIXI.Container();
      ring.x = this.containerWidth / 2;
      ring.y = this.containerHeight / 2;
      ring.radius = radius;
      ring.rotationSpeed = [1, 0.5, 0.25][index]; // Rotation speeds for inner, mid, outer rings

      this._populateRing(ring, radius);
      this.container.addChild(ring);
      this.rings.push(ring);
    });
  }

  /** Populates a ring with upright symbols. */
  _populateRing(ring, radius) {
    const numSymbols = 12;

    for (let i = 0; i < numSymbols; i++) {
      const angle = (i / numSymbols) * Math.PI * 2;
      const symbol = new PIXI.Sprite(PIXI.Texture.WHITE); // Replace with actual texture
      symbol.anchor.set(0.5);
      symbol.x = Math.cos(angle) * radius;
      symbol.y = Math.sin(angle) * radius;

      // Keep symbols upright
      symbol.rotation = angle + Math.PI / 2;

      ring.addChild(symbol);
    }
  }

  /** Rotates the rings around their center points. */
  rotateRings() {
    this.rings.forEach((ring) => {
      gsap.to(ring, {
        rotation: `+=${Math.PI * 2}`,
        duration: ring.rotationSpeed * 5, // Adjust speed dynamically
        repeat: -1,
        ease: 'linear',
      });
    });
  }

  /** Calculates payline wins based on radial alignment. */
  calculatePayline() {
    this.rings.forEach((ring) => {
      ring.children.forEach((symbol) => {
        // Implement radial alignment logic here
        const angle = Math.atan2(symbol.y, symbol.x);
        symbol.rotation = angle + Math.PI / 2;
      });
    });
  }

  /** Adds stone grinding shake effect. */
  triggerStoneGrinding() {
    gsap.to(this.container, {
      x: '+=20',
      y: '+=10',
      yoyo: true,
      repeat: 5,
      duration: 0.05,
      onComplete: () => {
        gsap.to(this.container, { x: 0, y: 0, duration: 0.1 });
      },
    });
  }
}

export default CalendarController;