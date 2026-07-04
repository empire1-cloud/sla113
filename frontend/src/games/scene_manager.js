// SceneManager to Handle Game Transitions (Sovereign Slam ↔ Aztec Tide)
class SceneManager {
    constructor(app) {
        this.app = app; // Reference to PIXI.Application
        this.currentScene = null; // Track the active scene
    }

    // Switch to New Scene
    switchScene(newSceneInitializer) {
        // Destroy Current Scene
        this.destroyScene();

        // Clear Texture Cache
        this.clearTextureCache();

        // Load New Scene
        this.currentScene = newSceneInitializer(this.app);
        console.log("Scene switched successfully.");
    }

    // Destroy Current Scene
    destroyScene() {
        if (this.currentScene && this.currentScene.stage) {
            // Remove all children from the stage
            this.currentScene.stage.removeChildren();
            console.log("Destroyed all sprites and resources from previous scene.");
        }
    }

    // Clear PIXI Texture Cache
    clearTextureCache() {
        Object.keys(PIXI.utils.TextureCache).forEach((textureKey) => {
            PIXI.utils.TextureCache[textureKey].destroy(true);
        });
        console.log("Texture cache cleared.");
    }
}

// Sovereign Slam (Game A)
function loadSovereignSlam(app) {
    const game = { stage: new PIXI.Container() };
    const stage = game.stage;

    // Lowrider and Chrome Crate Assets
    const lowrider = PIXI.Sprite.from('assets/lowrider.webp');
    lowrider.anchor.set(0.5);
    lowrider.x = app.screen.width / 2;
    lowrider.y = app.screen.height / 2 - 150;
    stage.addChild(lowrider);

    const chromeCrate = PIXI.Sprite.from('assets/chrome_crate.webp');
    chromeCrate.anchor.set(0.5);
    chromeCrate.x = app.screen.width / 2;
    chromeCrate.y = app.screen.height / 2 + 150;
    stage.addChild(chromeCrate);

    // Add Stage to App
    app.stage.addChild(stage);

    console.log("Sovereign Slam assets loaded.");
    return game;
}

// Aztec Tide (Game B)
function loadAztecTide(app) {
    const game = { stage: new PIXI.Container() };
    const stage = game.stage;

    // Aztec and Jade Crate Assets
    const aztec = PIXI.Sprite.from('assets/aztec.webp');
    aztec.anchor.set(0.5);
    aztec.x = app.screen.width / 2;
    aztec.y = app.screen.height / 2 - 150;
    stage.addChild(aztec);

    const jadeCrate = PIXI.Sprite.from('assets/jade_crate.webp');
    jadeCrate.anchor.set(0.5);
    jadeCrate.x = app.screen.width / 2;
    jadeCrate.y = app.screen.height / 2 + 150;
    stage.addChild(jadeCrate);

    // Add Stage to App
    app.stage.addChild(stage);

    console.log("Aztec Tide assets loaded.");
    return game;
}

console.log("SceneManager ready.");

// Example Usage
const app = new PIXI.Application({ width: 1920, height: 1080 });
document.body.appendChild(app.view);
const sceneManager = new SceneManager(app);

// Example: Switch between scenes
sceneManager.switchScene(loadSovereignSlam); // Load Sovereign Slam
setTimeout(() => sceneManager.switchScene(loadAztecTide), 5000); // Load Aztec Tide after 5 seconds