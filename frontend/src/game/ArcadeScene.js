import Phaser from 'phaser';

export default class ArcadeScene extends Phaser.Scene {
  constructor() {
    super('ArcadeScene');
  }

  preload() {
    // Load the asset pack that defines all our game assets
    this.load.pack('arcade', 'assets/arcade-pack.json');
    
    // Load any additional assets not in the pack
    this.load.image('logo', 'assets/generated/logo.png');
  }

  create() {
    // Add background
    this.add.image(400, 300, 'lobby-background');
    
    // Add title
    this.add.text(400, 100, 'SOUTHERN LIFESTYLE ARCADE', {
      fontFamily: '"Dancing Script", cursive',
      fontSize: '48px',
      color: '#d4af37'
    }).setOrigin(0.5);
    
    // Create a character sprite from our atlas
    const character = this.add.sprite(400, 200, 'characters', 'hero-idle-0');
    character.setScale(2);
    
    // Add animation if we have it in the atlas
    if (this.anims.get('hero-idle')) {
      character.play('hero-idle');
    }
    
    // Add UI button example
    const playButton = this.add.sprite(400, 400, 'arcade-ui', 'play-button');
    playButton.setInteractive();
    playButton.on('pointerover', () => {
      playButton.setTexture('arcade-ui', 'play-button-hover');
    });
    playButton.on('pointerout', () => {
      playButton.setTexture('arcade-ui', 'play-button');
    });
    playButton.on('pointerdown', () => {
      playButton.setTexture('arcade-ui', 'play-button-pressed');
      this.scene.start('GameScene');
    });
    playButton.on('pointerup', () => {
      playButton.setTexture('arcade-ui', 'play-button-hover');
    });
    
    // Add instruction text
    this.add.text(400, 500, 'Click PLAY to start', {
      fontFamily: '"Rajdhani", sans-serif',
      fontSize: '24px',
      color: '#ffffff'
    }).setOrigin(0.5);
  }
}

// Example of how to use animations from the atlas
export class CharacterAnimator {
  static setupAnimations(scene) {
    // These would typically be defined in your game initialization
    // based on the JSON data from Aseprite
    
    // Example idle animation (assuming the atlas has these frames)
    if (scene.anims.get('hero-idle') === null) {
      scene.anims.create({
        key: 'hero-idle',
        frames: scene.anims.generateFrameNames('characters', {
          prefix: 'hero-idle-',
          start: 0,
          end: 3,
          zeroPad: 2
        }),
        frameRate: 8,
        repeat: -1
      });
    }
    
    // Example attack animation
    if (scene.anims.get('hero-attack') === null) {
      scene.anims.create({
        key: 'hero-attack',
        frames: scene.anims.generateFrameNames('characters', {
          prefix: 'hero-attack-',
          start: 0,
          end: 5,
          zeroPad: 2
        }),
        frameRate: 15,
        repeat: 0
      });
    }
  }
}
