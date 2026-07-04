import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { RoughEase } from 'gsap/EasePack';

gsap.registerPlugin(RoughEase);

/**
 * DashboardController
 * Manages 3 rotating gauges: Left, Center, Right.
 */
export class DashboardController {
  constructor(container) {
    this.container = container;
    this.gauges = []; // Array of gauges

    // Fixed 16:9 aspect ratio
    this.containerWidth = 1920;
    this.containerHeight = 1080;

    // Create the layer-locked background
    this._addBackground();

    // Create and layout 3 gauges
    this._createGauges();
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

  /** Creates the 3 circular gauges. */
  _createGauges() {
    const gaugePositions = [
      { x: 480, y: 540 }, // Left gauge
      { x: 960, y: 540 }, // Center gauge
      { x: 1440, y: 540 }, // Right gauge
    ];

    gaugePositions.forEach((position) => {
      const gauge = new PIXI.Container();
      gauge.x = position.x;
      gauge.y = position.y;
      this._populateGauge(gauge);
      this.container.addChild(gauge);
      this.gauges.push(gauge);
    });
  }

  /** Populates a gauge with rotating symbols. */
  _populateGauge(gauge) {
    const numSymbols = 8;
    const radius = 200;

    for (let i = 0; i < numSymbols; i++) {
      const angle = (i / numSymbols) * Math.PI * 2;
      const symbol = new PIXI.Sprite(PIXI.Texture.WHITE); // Replace with actual texture
      symbol.anchor.set(0.5);
      symbol.x = Math.cos(angle) * radius;
      symbol.y = Math.sin(angle) * radius;

      gauge.addChild(symbol);
    }
  }

  /** Spins the gauges with a radial blur effect. */
  spinGauges() {
    this.gauges.forEach((gauge) => {
      gsap.to(gauge, {
        rotation: `+=${Math.PI * 4}`,
        duration: 2,
        ease: 'linear',
        onUpdate: () => {
          gauge.children.forEach((symbol) => {
            const blurFilter = new PIXI.filters.BlurFilter();
            blurFilter.blur = 5; // Adjust to simulate radial blur
            symbol.filters = [blurFilter];
          });
        },
        onComplete: () => {
          this._snapToStop(gauge);
        },
      });
    });
  }

  /** Stops spinning and snaps to the payline with vibration. */
  _snapToStop(gauge) {
    gsap.to(gauge, {
      rotation: 0,
      ease: RoughEase.ease.config({
        strength: 1.5,
        points: 20,
        taper: 'both',
        randomize: true,
        clamp: false,
      }),
      duration: 1,
      onComplete: () => {
        gauge.children.forEach((symbol) => {
          symbol.filters = null; // Remove blur
        });

        // Add hydraulic bounce effect
        gsap.to(gauge.scale, {
          x: 1.1,
          y: 1.1,
          yoyo: true,
          repeat: 1,
          duration: 0.2,
        });
      },
    });
  }
}

export default DashboardController;