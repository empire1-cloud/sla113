import Phaser from 'phaser';
import { CharacterAnimator } from './ArcadeScene';

export default class GameScene extends Phaser.Scene {
  constructor() {
    super('GameScene');
  }

  init(data) {
    // This would receive data from the arcade launcher
    this.selectedGame = data?.gameKey || 'fish-shooter';
  }

  preload() {
    // Load assets based on selected game
    switch (this.selectedGame) {
      case 'fish-shooter':
        this.load.image('ocean-bg', 'assets/generated/backgrounds/ocean.jpg');
        this.load.atlas('fish', 'assets/generated/sprites/fish.png', 'assets/generated/sprites/fish.json');
        this.load.atlas('cannon', 'assets/generated/sprites/cannon.png', 'assets/generated/sprites/cannon.json');
        this.load.image('bullet', 'assets/generated/sprites/bullet.png');
        this.load.audio('shoot', 'assets/audio/shoot.ogg');
        this.load.audio('hit', 'assets/audio/hit.ogg');
        break;
        
      case 'slots':
        this.load.image('slot-bg', 'assets/generated/backgrounds/slot-machine.jpg');
        this.load.atlas('slot-reels', 'assets/generated/sprites/slot-reels.png', 'assets/generated/sprites/slot-reels.json');
        this.load.audio('spin', 'assets/audio/spin.ogg');
        this.load.audio('win', 'assets/audio/win.ogg');
        break;
        
      default:
        // Fallback to a simple test scene
        this.load.image('test-bg', 'assets/generated/backgrounds/test.jpg');
        this.load.sprite('test-sprite', 'assets/generated/sprites/test.png', 'assets/generated/sprites/test.json');
    }
  }

  create() {
    // Add background
    this.add.image(400, 300, this.selectedGame === 'fish-shooter' ? 'ocean-bg' : 'slot-bg');
    
    // Add game title
    this.add.text(400, 100, this.selectedGame === 'fish-shooter' ? 'FISH SHOOTER' : 'SLOT MACHINE', {
      fontFamily: '"Dancing Script", cursive',
      fontSize: '36px',
      color: '#ffd700'
    }).setOrigin(0.5);
    
    // Initialize character animations if we have any
    CharacterAnimator.setupAnimations(this);
    
    // Add a test character to show sprite sheet usage
    const testChar = this.add.sprite(400, 250, 'characters', 'hero-idle-0');
    testChar.setScale(1.5);
    
    if (this.anims.get('hero-idle')) {
      testChar.play('hero-idle');
    }
    
    // Add coins counter UI
    const coinsText = this.add.text(20, 20, 'COINS: 1500', {
      fontFamily: '"Rajdhani", sans-serif',
      fontSize: '24px',
      color: '#ffff00'
    });
    
    // Add coin icon
    this.add.sprite(120, 25, 'arcade-ui', 'coin').setScale(0.5);
    
    // Add back button
    const backButton = this.add.sprite(780, 20, 'arcade-ui', 'back-button');
    bottomorigin.setOrigin(1, 0);
    backButton.setInteractive();
    backButton.on('pointerover', () => {
      backButton.setTexture('arcade-ui', 'back-button-hover');
    });
    backButton.on('pointerout', () => {
      backButton.setTexture('arcade-ui', 'back-button');
    });
    backButton.on('pointerdown', () => {
      this.scene.start('BootScene');
    });
    
    // Add instructions
    this.add.text(400, 550, 'Press SPACE to shoot / SPIN to play', {
      fontFamily: '"Rajdhani", sans-serif',
      fontSize: '18px',
      color: '#ffffff'
    }).setOrigin(0.5);
  }

  update() {
    // Game logic would go here
    // This is where you'd implement actual game mechanics
  }
}
