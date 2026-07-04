// Full-Stage PixiJS Lounge Implementation
const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x000000,
});

document.body.appendChild(app.view);

// Letterbox Scaling Function
function resize() {
    const canvas = app.view;
    const parent = canvas.parentNode || document.body;
    const parentWidth = parent.clientWidth;
    const parentHeight = parent.clientHeight;

    const scale = Math.min(parentWidth / app.screen.width, parentHeight / app.screen.height);
    
    const newWidth = Math.ceil(app.screen.width * scale);
    const newHeight = Math.ceil(app.screen.height * scale);

    canvas.style.width = `${newWidth}px`;
    canvas.style.height = `${newHeight}px`;
    canvas.style.marginTop = `${(parentHeight - newHeight) / 2}px`;
    canvas.style.marginLeft = `${(parentWidth - newWidth) / 2}px`;
}

window.addEventListener('resize', resize);
resize(); // Initial scaling

// Build Parallax Layers
const stage = app.stage;

const bgLayer1 = PIXI.Sprite.from('assets/lobby_parallax_layer1.webp'); // Foreground
const bgLayer2 = PIXI.Sprite.from('assets/lobby_parallax_layer2.webp'); // Midground
const bgLayer3 = PIXI.Sprite.from('assets/lobby_parallax_layer3.webp'); // Background

// Configure Layers
bgLayer1.anchor.set(0.5);
bgLayer1.x = bgLayer2.x = bgLayer3.x = app.screen.width / 2;
bgLayer1.y = bgLayer2.y = bgLayer3.y = app.screen.height / 2;

bgLayer1.zIndex = 3; // Foreground
bgLayer2.zIndex = 2; // Midground
bgLayer3.zIndex = 1; // Background

// Add Layers to Stage
stage.addChild(bgLayer3, bgLayer2, bgLayer1);

// Simple Parallax Animation
app.ticker.add(() => {
    const mouseX = app.renderer.plugins.interaction.mouse.global.x;
    const mouseY = app.renderer.plugins.interaction.mouse.global.y;

    const moveFactorX = (mouseX - app.screen.width / 2) / (app.screen.width / 2);
    const moveFactorY = (mouseY - app.screen.height / 2) / (app.screen.height / 2);

    bgLayer1.x = app.screen.width / 2 + moveFactorX * 20;
    bgLayer1.y = app.screen.height / 2 + moveFactorY * 20;

    bgLayer2.x = app.screen.width / 2 + moveFactorX * 10;
    bgLayer2.y = app.screen.height / 2 + moveFactorY * 10;
});

console.log('Lounge scene with parallax background has been initialized.');