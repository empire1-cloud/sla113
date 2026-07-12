/**
 * FxManagers.js
 *
 * Two small, focused managers for one-shot visual effects:
 *   - ImpactFxManager: spark burst at a bullet-hit location.
 *   - CoinFxManager: coin pop + optional multiplier burst at a kill location.
 *
 * Both spawn a sprite, play a non-looping animation, and self-destroy on
 * 'animationcomplete' — no manual timers, no leaked sprites.
 */

export class ImpactFxManager {
  constructor(scene) {
    this.scene = scene;
  }

  playAt(x, y) {
    if (!this.scene.anims.exists('impact__spark')) return;
    const fx = this.scene.add.sprite(x, y, 'impacts', 'impact__spark__0');
    fx.play('impact__spark');
    fx.once('animationcomplete', () => fx.destroy());
  }
}

export class CoinFxManager {
  constructor(scene) {
    this.scene = scene;
  }

  /**
   * @param {number} x
   * @param {number} y
   * @param {number} [value=1] coin value, shown as floating text
   * @param {number} [multiplier=1] if > 1, adds a burst variant + multiplier label
   */
  playAt(x, y, value = 1, multiplier = 1) {
    const animKey = multiplier > 1 ? 'coin__burst' : 'coin__spin';
    if (this.scene.anims.exists(animKey)) {
      const fx = this.scene.add.sprite(x, y, 'coins', `coin__${multiplier > 1 ? 'burst' : 'spin'}__0`);
      fx.play(animKey);
      fx.once('animationcomplete', () => fx.destroy());
    }

    const labelText = multiplier > 1 ? `+${value} x${multiplier}` : `+${value}`;
    const label = this.scene.add.text(x, y - 20, labelText, {
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: multiplier > 1 ? '20px' : '16px',
      color: multiplier > 1 ? '#ff8844' : '#c9a227',
    }).setOrigin(0.5);

    this.scene.tweens.add({
      targets: label,
      y: y - 60,
      alpha: 0,
      duration: 700,
      ease: 'Cubic.easeOut',
      onComplete: () => label.destroy(),
    });
  }
}
