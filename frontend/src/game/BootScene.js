import Phaser from 'phaser';
import ArcadeScene from './ArcadeScene';

export default class BootScene extends Phaser.Scene {
  constructor() {
    super('BootScene');
  }

  preload() {
    // Load essential assets first
    this.load.image('loader-bg', 'assets/generated/loader-bg.jpg');
    this.load.image('loader-bar', 'assets/generated/loader-bar.png');
    
    // Load the main asset pack
    this.load.pack('assets', 'assets/arcade-pack.json');
  }

  create() {
    // Show loading screen briefly
    const bg = this.add.image(400, 300, 'loader-bg');
    const bar = this.add.image(400, 350, 'loader-bar').setOrigin(0.5, 0.5);
    bar.setDisplaySize(0, 20); // Start empty
    
    // Simulate loading progress
    this.tweens.add({
      targets: bar,
      duration: 1500,
      ease: 'Power2',
      delay: 500,
      onUpdate: (tween) => {
        const progress = tween.getValue();
        bar.setDisplaySize(800 * progress, 20);
      }
    });
    
    // After loading, go to arcade menu
    this.time.delayedCall(2000, () => {
      this.scene.start('ArcadeScene');
    });
  }
}
