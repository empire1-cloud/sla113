// Southern Lifestyle Loading Scene Implementation
const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x000000,
});

document.body.appendChild(app.view);

// Create Loading Assets
const stage = app.stage;

// Southern Lifestyle Logo
const logo = PIXI.Sprite.from('assets/southern_lifestyle_logo.webp');
logo.anchor.set(0.5);
logo.x = app.screen.width / 2;
logo.y = app.screen.height / 2 - 100;
stage.addChild(logo);

// Loading Text
const loadingText = new PIXI.Text('Loading...', {
    fontFamily: 'Arial',
    fontSize: 36,
    fill: 0xffffff,
    align: 'center',
});
loadingText.anchor.set(0.5);
loadingText.x = app.screen.width / 2;
loadingText.y = app.screen.height / 2 + 100;
stage.addChild(loadingText);

// Pulsing Loading Animation
app.ticker.add(() => {
    loadingText.alpha = 0.5 + Math.sin(Date.now() / 200) * 0.5; // Smooth fading
});

// Preload Assets
const loader = PIXI.Loader.shared;
loader.add('assets/lobby_parallax_layer1.webp')
      .add('assets/lobby_parallax_layer2.webp')
      .add('assets/lobby_parallax_layer3.webp')
      .add('assets/firme_f_banner.webp')
      .add('assets/audio/lounge_ambient_track.mp3')
      .load(onAssetsLoaded);

function onAssetsLoaded() {
    console.log('All assets preloaded. Transitioning to Lounge Scene...');

    // Fade Out Logo and Loading Text
    const fadeGraphics = new PIXI.Graphics();
    fadeGraphics.beginFill(0x000000, 1);
    fadeGraphics.drawRect(0, 0, app.screen.width, app.screen.height);
    fadeGraphics.endFill();
    fadeGraphics.alpha = 0;
    stage.addChild(fadeGraphics);

    gsap.to(fadeGraphics, {
        alpha: 1,
        duration: 1,
        onComplete: () => {
            stage.removeChildren(); // Clear loading screen assets

            // Start Lounge Scene
            startLoungeScene();
        },
    });
}

// Start Lounge Scene
function startLoungeScene() {
    const lounge = new LoungeWorld(app.stage, app);
    lounge.initialize();
}

console.log('Southern Lifestyle Loading Screen Initialized.');