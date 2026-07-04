import * as PIXI from 'pixi.js';
import { CircularController } from './CircularController';
import { DashboardController } from './DashboardController';

/**
 * GameObserver Module
 * Manages the real-time miniature renders in the Multiplayer Lobby.
 */
export class GameObserver {
  constructor(parentContainer) {
    this.parentContainer = parentContainer; // Parent PIXI Container
    this.miniatures = []; // Store miniature game renders

    // Configuration for preview resolution
    this.previewWidth = 320;
    this.previewHeight = 180;
  }

  /**
   * Create and render a miniature preview.
   * @param {string} gameType - Type of game ('Circular' or 'Dashboard').
   * @param {number} x - X position in the parent container.
   * @param {number} y - Y position in the parent container.
   */
  createMiniature(gameType, x, y) {
    const miniatureContainer = new PIXI.Container();
    miniatureContainer.x = x;
    miniatureContainer.y = y;
    miniatureContainer.width = this.previewWidth;
    miniatureContainer.height = this.previewHeight;

    // Add game-specific layout
    if (gameType === 'Circular') {
      const circularPreview = new CircularController(miniatureContainer);
      circularPreview.startRotation(); // Animate rings in real-time
    } else if (gameType === 'Dashboard') {
      const dashboardPreview = new DashboardController(miniatureContainer);
      dashboardPreview.spinGauges(); // Animate gauges in real-time
    }

    // Add the miniature to the parent container
    this.parentContainer.addChild(miniatureContainer);
    this.miniatures.push(miniatureContainer);
  }

  /**
   * Clear all miniatures from the lobby view.
   */
  clearMiniatures() {
    this.miniatures.forEach((miniature) => {
      this.parentContainer.removeChild(miniature);
    });
    this.miniatures = [];
  }
}

export default GameObserver;