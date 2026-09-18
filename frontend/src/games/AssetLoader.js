import * as PIXI from 'pixi.js';

// Configure WebP asset loader
PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST; // Retains sharp edges for chrome textures

const assetLoader = new PIXI.Loader();

// Add asset paths (example WebP spritesheets)
const assets = [
    { name: "lowrider_symbol", url: "assets/lowrider_symbol.webp" },
    { name: "aztec_fish", url: "assets/aztec_fish.webp" },
    { name: "chrome_emblem", url: "assets/chrome_emblem.webp" },
    { name: "sun_stone", url: "assets/aztec_sun_stone.webp" }
];

assets.forEach(asset => assetLoader.add(asset.name, asset.url));

// Load assets
assetLoader.load((loader, resources) => {
    console.log("Assets loaded:", resources);
});

export default assetLoader;