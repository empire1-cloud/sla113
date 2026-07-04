// Unified Core Game Stage with SceneManager
const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x000000,
});

document.body.appendChild(app.view);

// Letterbox Scaling
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
resize();

// Unified SceneManager
class SceneManager {
    constructor(app) {
        this.app = app;
        this.currentScene = null;
    }

    switchScene(newSceneInitializer) {
        this.destroyScene();
        this.clearTextureCache();
        this.currentScene = newSceneInitializer(this.app);
    }

    destroyScene() {
        if (this.currentScene && this.currentScene.stage) {
            this.currentScene.stage.removeChildren();
        }
    }

    clearTextureCache() {
        Object.keys(PIXI.utils.TextureCache).forEach((key) => {
            PIXI.utils.TextureCache[key].destroy(true);
        });
    }
}

const sceneManager = new SceneManager(app);

// Southern Lifestyle Loading Screen
function southernLifestyleLoadingScreen(app) {
    const stage = new PIXI.Container();
    const logo = PIXI.Sprite.from('assets/southern_lifestyle_logo.webp');
    logo.anchor.set(0.5);
    logo.x = app.screen.width / 2;
    logo.y = app.screen.height / 2;
    stage.addChild(logo);

    const loadingText = new PIXI.Text('Loading...', {
        fontFamily: 'Arial',
        fontSize: 36,
        fill: 0xffffff,
    });
    loadingText.anchor.set(0.5);
    loadingText.x = app.screen.width / 2;
    loadingText.y = app.screen.height / 2 + 100;
    stage.addChild(loadingText);

    app.stage.addChild(stage);

    PIXI.Loader.shared.add('assets/lowrider.webp')
        .add('assets/chrome_crate.webp')
        .add('assets/aztec.webp')
        .add('assets/jade_crate.webp')
        .load(() => {
            app.stage.removeChild(stage);
            sceneManager.switchScene(loadAztecTide);
        });
}

// Sample Sovereign Slam Game
function loadSovereignSlam(app) {
    const stage = new PIXI.Container();
    const lowrider = PIXI.Sprite.from('assets/lowrider.webp');
    lowrider.anchor.set(0.5);
    lowrider.x = app.screen.width / 2;
    lowrider.y = app.screen.height / 2 - 150;
    stage.addChild(lowrider);

    // Add Bloom Effect to Lowrider Symbol
    addBloomEffect(lowrider);

    const chromeCrate = PIXI.Sprite.from('assets/chrome_crate.webp');
    chromeCrate.anchor.set(0.5);
    chromeCrate.x = app.screen.width / 2;
    chromeCrate.y = app.screen.height / 2 + 150;
    stage.addChild(chromeCrate);

    // Add Specular Shine to Chrome Crate
    applySpecularShine(chromeCrate);

    app.stage.addChild(stage);
}

// Initialize Southern Lifestyle Loading Screen
southernLifestyleLoadingScreen(app);