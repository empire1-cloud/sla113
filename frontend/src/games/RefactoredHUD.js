import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { GlowFilter } from '@pixi/filter-glow';

/**
 * Refactored HUD UI
 */
export class RefactoredHUD {
  constructor(app, resources) {
    this.app = app;
    this.resources = resources; // Contains textures and assets like input_file_11
    this.hudContainer = new PIXI.Container();

    // Create Balance and Bet windows with Chrome-Sweep Shader
    this.balanceWindow = this._createChromeWindow('Balance: $1000', 200, 50);
    this.betWindow = this._createChromeWindow('Bet: $10', 200, 120);

    // Create the 'S' Rose Emblem Home Button
    this.homeButton = this._createHomeButton();

    this.hudContainer.addChild(this.balanceWindow, this.betWindow, this.homeButton);
    this.app.stage.addChild(this.hudContainer);
  }

  /**
   * Creates a window (Balance/Bet) with Chrome-Sweep Shader.
   */
  _createChromeWindow(label, x, y) {
    const container = new PIXI.Container();
    container.x = x;
    container.y = y;

    const window = new PIXI.Sprite(PIXI.Texture.WHITE); // Base rectangle
    window.width = 150;
    window.height = 50;
    window.tint = 0x666666;
    container.addChild(window);

    // Chrome-sweep light
    const sweep = new PIXI.Graphics();
    sweep.beginFill(0xffffff, 0.5);
    sweep.drawRect(-50, 0, 50, 50);
    sweep.endFill();
    sweep.x = -50;
    container.addChild(sweep);

    gsap.to(sweep, {
      x: 200,
      duration: 2,
      repeat: -1,
      ease: 'power2.inOut',
    });

    // Label text
    const text = new PIXI.Text(label, { fontFamily: 'Arial', fontSize: 16, fill: 0xffffff });
    text.anchor.set(0.5);
    text.x = window.width / 2;
    text.y = window.height / 2;
    container.addChild(text);

    return container;
  }

  /**
   * Creates the 'S' Rose Emblem Home Button with Neon Glow.
   */
  _createHomeButton() {
    const rose = new PIXI.Sprite(this.resources['input_file_11']); // S Rose Emblem texture
    rose.anchor.set(0.5);
    rose.x = 50;
    rose.y = 200;
    rose.width = 100;
    rose.height = 100;

    // Neon Glow Filter
    const glow = new GlowFilter({
      color: 0xff0066,
      distance: 15,
      outerStrength: 4,
      innerStrength: 2,
    });
    rose.filters = [glow];

    gsap.to(rose, {
      alpha: 0.8,
      duration: 0.3,
      repeat: -1,
      yoyo: true,
    });

    return rose;
  }

  /**
   * Plays Hydraulic Bounce animation on gun change.
   * @param {PIXI.Sprite} gun - The gun sprite to animate.
   */
  playGunBounce(gun) {
    gsap.to(gun.scale, {
      x: 0.8,
      y: 1.2,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      ease: 'power2.out',
    });
  }
}

export default RefactoredHUD;