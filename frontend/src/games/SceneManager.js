class SceneManager {
    constructor(audioEngine) {
        this.currentScene = null;
        this.audioEngine = audioEngine; // Audio engine reference
    }

    // Core Transition Logic
    playTransitionAnimation(animation) {
        switch (animation) {
            case "aztec_gate_opening":
                console.log("Animating Aztec Gates...");
                this.audioEngine.playSoundEffect("stone_grinding", { volume: 1.0, loop: true });
                // Simulate animation and stop sound
                setTimeout(() => {
                    console.log("Aztec Gate Animation Complete.");
                    this.audioEngine.stopSoundEffect("stone_grinding");
                }, 3000); // Example duration
                break;
            default:
                console.log("No animation defined for:", animation);
        }
    }

    // Load a specific scene
    loadScene(sceneId) {
        // Inject Aztec Bonus Transition
        if (sceneId === "aztec_tide") {
            console.log("[AAA Transition]: Starting Aztec Bonus Experience...");
            this.playTransitionAnimation("aztec_gate_opening");
        }

        if (this.currentScene) {
            this.unloadScene(); // Ensure proper cleanup
        }

        if (sceneId === "sovereign_slam") {
            this.currentScene = new SovereignSlamScene(this.audioEngine);
        } else if (sceneId === "aztec_tide") {
            this.currentScene = new AztecTideScene(this.audioEngine);
        }

        this.currentScene.init(); // Initialize new scene
    }

    // Unload the current scene (clean assets)
    unloadScene() {
        if (this.currentScene) {
            this.currentScene.destroy(); // Clear associated assets
            this.currentScene = null;
        }
    }
}

// Example scenes enforcing asset-locking
class SovereignSlamScene {
    constructor(audioEngine) {
        this.audioEngine = audioEngine; // Add audio reference
    }

    init() {
        console.log("Initializing Sovereign Slam Scene");
        this.assets = ["lowrider_symbol", "chrome_emblem", "sovereign_background"];
        this.loadAssets();
    }

    loadAssets() {
        this.assets.forEach(asset => console.log(`Loading ${asset}`)); // Replace placeholders with actual loader calls
    }

    destroy() {
        console.log("Unloading Sovereign Slam assets");
    }
}

class AztecTideScene {
    constructor(audioEngine) {
        this.audioEngine = audioEngine; // Audio engine support
    }

    init() {
        console.log("Initializing Aztec Tide Scene");
        // Play Aztec whistle at scene start (warning sound)
        this.audioEngine.playSoundEffect("aztec_whistle", { volume: 0.8 });
        this.assets = ["aztec_fish", "sun_stone", "aztec_background"];
        this.loadAssets();
    }

    loadAssets() {
        // Play stone-grinding sound during asset loading
        this.audioEngine.playSoundEffect("stone_grinding", { volume: 1.0, loop: true });
        this.assets.forEach(asset => console.log(`Loading ${asset}`)); // Replace placeholders with actual loader calls
    }

    destroy() {
        // Play angelic chime during treasure reveal
        this.audioEngine.playSoundEffect("angelic_chime", { volume: 1.2 });
        console.log("Unloading Aztec Tide assets");
    }
}

export default SceneManager;