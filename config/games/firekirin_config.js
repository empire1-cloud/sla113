// FireKirin Base Engine - Phaser 3 Configuration
export const CONFIG = {
  type: Phaser.AUTO,
  width: 1280,
  height: 720,
  backgroundColor: '#001428',
  parent: 'game-container',
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { y: 0 },
      debug: false
    }
  },
  scene: [] // Scenes added in index.js
};

// Game Constants
export const GAME = {
  // Token system
  startingTokens: 1000,
  tokenCostPerShot: {
    normal: 1,
    laser: 5,
    cannon: 10
  },
  
  // Weapon configs
  weapons: {
    normal: {
      name: 'Normal Gun',
      fireRate: 200,
      damage: 10,
      bulletSpeed: 800,
      costPerShot: 1
    },
    laser: {
      name: 'Laser Gun',
      fireRate: 50,
      damagePerTick: 5,
      beamWidth: 8,
      costPerSecond: 5
    },
    cannon: {
      name: 'Locked Cannon',
      fireRate: 1000,
      damage: 50,
      bulletSpeed: 600,
      costPerShot: 10,
      burstCount: 3
    }
  },
  
  // Fish configs
  fish: {
    types: [
      { name: 'small', hp: 10, multiplier: 2, speed: 100, size: 0.5 },
      { name: 'medium', hp: 30, multiplier: 5, speed: 80, size: 0.75 },
      { name: 'large', hp: 60, multiplier: 10, speed: 60, size: 1.0 },
      { name: 'boss', hp: 150, multiplier: 20, speed: 40, size: 1.5 },
      { name: 'golden', hp: 100, multiplier: 50, speed: 70, size: 1.0 },
      { name: 'legendary', hp: 300, multiplier: 100, speed: 30, size: 2.0 }
    ],
    baseValue: 10,
    spawnInterval: 2000,
    waveSize: { min: 3, max: 8 }
  },
  
  // Jackpot configs
  jackpot: {
    baseChance: 0.02,
    minPool: 500,
    startingPool: 1000,
    contributionRate: 0.05,
    multipliers: {
      mini: 2,
      minor: 5,
      major: 10,
      grand: 50
    }
  }
};
