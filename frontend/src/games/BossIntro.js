import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';

/**
 * BossIntro Sequence for the Bone Sovereign.
 */
export function BossIntro(app, bossTexture, backgroundContainer) {
  const stage = app.stage;

  // The Dimmer: Desaturate and reduce brightness of background
  const backgroundFilter = new PIXI.filters.ColorMatrixFilter();
  backgroundContainer.filters = [backgroundFilter];
  gsap.to(backgroundFilter, {
    matrix: [
      0.3, 0.3, 0.3, 0, 0,
      0.3, 0.3, 0.3, 0, 0,
      0.3, 0.3, 0.3, 0, 0,
      0,   0,   0,   1, 0,
    ], // Lower saturation
    brightness: 0.3, // Drop brightness
    duration: 2,
  });

  // The Warning: Neon Cyan Pulse
  const warningCircle = new PIXI.Graphics();
  warningCircle.beginFill(0x00ffff, 0.8);
  warningCircle.drawCircle(0, 0, 50);
  warningCircle.endFill();
  warningCircle.x = app.screen.width / 2;
  warningCircle.y = app.screen.height / 2;
  warningCircle.alpha = 0;
  stage.addChild(warningCircle);

  gsap.to(warningCircle, {
    alpha: 0.8,
    duration: 0.5,
    repeat: 3,
    onRepeat: () => {
      warningCircle.scale.set(1);
      gsap.to(warningCircle.scale, { x: 5, y: 5, duration: 0.5 });
    },
    onComplete: () => {
      stage.removeChild(warningCircle);
    },
  });

  // The Reveal: Boiling water displacement filter and boss scale animation
  const displacementSprite = new PIXI.Sprite(PIXI.Texture.from('water_displacement_asset'));
  const displacementFilter = new PIXI.filters.DisplacementFilter(displacementSprite);
  app.stage.addChild(displacementSprite);
  app.stage.filters = [displacementFilter];

  gsap.to(displacementSprite, {
    x: 20,
    y: 20,
    repeat: -1,
    duration: 0.1,
    yoyo: true,
  });

  const boss = new PIXI.Sprite(bossTexture);
  boss.anchor.set(0.5);
  boss.scale.set(3);
  boss.x = app.screen.width / 2;
  boss.y = app.screen.height / 2;
  stage.addChild(boss);

  gsap.to(boss.scale, {
    x: 1,
    y: 1,
    duration: 1.5,
    ease: 'elastic.out',
    onStart: () => {
      // Trigger SLA113 music here
      SLA113.playSound('heavy_aztec_bass');
    },
    onComplete: () => {
      // Screen shake on landing
      gsap.to(app.stage, {
        x: '+=10',
        y: '+=10',
        yoyo: true,
        repeat: 5,
        duration: 0.05,
        onComplete: () => {
          app.stage.x = 0;
          app.stage.y = 0;
          app.stage.filters = null; // Clear displacement filter
        },
      });
    },
  });
}

export default BossIntro;