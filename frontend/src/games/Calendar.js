import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { PixiParticleEmitter } from 'pixi-particles'; 
/**
 * DashboardController Win Animation Extensions
 */
export class DashboardController {
static initParticleEmitter(app) {
    // Example particle emitter configuration
    const emitterConfig = {
        // Define particle settings here
        alpha: { start: 1, end: 0 },
        scale: { start: 0.5, end: 1 },
        color: { start: "#ffffff", end: "#ff0000" },
        speed: { start: 200, end: 50 },
        lifetime: { min: 0.5, max: 1 },
        frequency: 0.008,
        maxParticles: 500,
        addAtBack: false,
        pos: { x: 0, y: 0 },
        // ... other PixiParticleEmitter settings ...
    };
    const emitter = new PixiParticleEmitter(app.stage, emitterConfig);
    emitter.emit = true;
    return emitter;
}
}
