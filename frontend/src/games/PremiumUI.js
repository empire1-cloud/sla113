import * as PIXI from 'pixi.js';
import { gsap } from 'gsap';
import { PixiPlugin } from 'gsap/PixiPlugin';

gsap.registerPlugin(PixiPlugin);
PixiPlugin.registerPIXI(PIXI);

const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x0F0F0F, // Dark, glassy background
});

// Glassmorphism UI container
const glassOverlay = new PIXI.Container();
const glassPanel = new PIXI.Graphics();

glassPanel.beginFill(0x242424, 0.5) // Semi-transparent
    .drawRoundedRect(100, 100, 1720, 880, 15) // Rounded rectangle glass panel
    .endFill();

glassOverlay.addChild(glassPanel);
app.stage.addChild(glassOverlay);

// Layers for Sovereign Slam slot
const fxLayer = new PIXI.Container();
const uiLayer = new PIXI.Container();
app.stage.addChild(fxLayer, uiLayer);

// Hydraulic Snap (Skill-Stop) with Elastic Vibrations
function hydraulicSnap(reelContainer, targetY) {
    gsap.killTweensOf(reelContainer);

    gsap.to(reelContainer, {
        y: targetY,
        duration: 0.05,
        ease: "none",
        onComplete: () => {
            // Elastic bounce after snap
            gsap.fromTo(reelContainer, 
                { y: targetY - 15 }, // Offset for elastic effect
                { 
                    y: targetY, 
                    duration: 0.4, 
                    ease: "elastic.out(1, 0.3)",
                    onStart: () => triggerScreenShake(8) // Trigger screen shake
                }
            );
        }
    });
}

// Screen Shake Effect
function triggerScreenShake(intensity) {
    gsap.to(app.stage, {
        x: `+=${intensity}`,
        y: `+=${intensity}`,
        duration: 0.05,
        repeat: 3,
        yoyo: true,
        onComplete: () => { app.stage.x = 0; app.stage.y = 0; }
    });
}

export { app, hydraulicSnap, triggerScreenShake };