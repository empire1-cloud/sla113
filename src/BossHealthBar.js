/**
 * BossHealthBar.js
 *
 * Assembles a health bar from the shared ui.png/json atlas pieces
 * (healthbar_bg, healthbar_left_cap, healthbar_fill, healthbar_right_cap).
 * Works with any CombatEntity that has role: 'boss' — wire it via
 * entity.onHealthChange, nothing here references a specific boss by name.
 */

export class BossHealthBar {
  /**
   * @param {Phaser.Scene} scene
   * @param {CombatEntity} bossEntity
   * @param {object} [opts]
   * @param {number} [opts.x=400] center x
   * @param {number} [opts.y=40] top y
   * @param {number} [opts.width=360] rendered width of the fill track
   */
  constructor(scene, bossEntity, opts = {}) {
    this.scene = scene;
    this.boss = bossEntity;
    this.x = opts.x ?? 400;
    this.y = opts.y ?? 40;
    this.width = opts.width ?? 360;
    this.height = opts.height ?? 28;

    this.container = scene.add.container(this.x, this.y);

    this.bg = scene.add.image(0, 0, 'ui', 'ui__healthbar_bg')
      .setDisplaySize(this.width + 16, this.height + 16);

    // Fill is a nine-slice-ish stretch of the fill frame; simple approach:
    // a rectangle sized by fraction, tinted, layered under end caps.
    this.fillMask = scene.add.rectangle(
      -this.width / 2, 0, this.width, this.height, 0xe0392b
    ).setOrigin(0, 0.5);

    this.leftCap = scene.add.image(-this.width / 2 - 8, 0, 'ui', 'ui__healthbar_left_cap')
      .setDisplaySize(20, this.height + 8);
    this.rightCap = scene.add.image(this.width / 2 + 8, 0, 'ui', 'ui__healthbar_right_cap')
      .setDisplaySize(20, this.height + 8);

    this.nameLabel = scene.add.text(0, -26, bossEntity.config.displayName, {
      fontFamily: 'Barlow Condensed, sans-serif',
      fontSize: '18px',
      color: '#c9a227',
      align: 'center',
    }).setOrigin(0.5);

    this.container.add([this.bg, this.fillMask, this.leftCap, this.rightCap, this.nameLabel]);

    bossEntity.onHealthChange = (current, max) => this.setFraction(current / max);
    this.setFraction(1);
  }

  setFraction(fraction) {
    const clamped = Phaser.Math.Clamp(fraction, 0, 1);
    this.fillMask.width = this.width * clamped;

    // Color ramps from gold-red at full health toward a warning flash near death,
    // giving a readable "this boss is close to dying" signal without new assets.
    if (clamped < 0.2) {
      this.fillMask.fillColor = 0xff2020;
    } else if (clamped < 0.5) {
      this.fillMask.fillColor = 0xe0392b;
    } else {
      this.fillMask.fillColor = 0xc9a227;
    }
  }

  destroy() {
    this.container.destroy();
  }
}
