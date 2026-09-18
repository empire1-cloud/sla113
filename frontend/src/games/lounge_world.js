// Pure Browser Environment Setup
// PIXI.js and GSAP are already loaded via CDN within the HTML.
// Lounge World Scene Implementation

class ChromeFGlintShader {
    static create() {
        return new PIXI.Filter(null, `
            precision mediump float;
            varying vec2 vTextureCoord;
            uniform sampler2D uSampler;
            uniform float uOffset;

            void main(void) {
                vec4 color = texture2D(uSampler, vTextureCoord);
                float sweep = smoothstep(0.4, 0.5, 1.0 - abs(vTextureCoord.x + vTextureCoord.y - uOffset));
                gl_FragColor = color + vec4(vec3(1.0) * sweep * color.a, color.a);
            }
        `, { uOffset: 0 });
    }
}

class LoungeWorld {
    constructor(stage, app) {
        this.stage = stage;
        this.app = app;
        this.isActive = false;
        this.background = null;
        this.ambientMusic = null;
        this.cars = [];
    }

    // Initialize Lounge Scene
    initialize() {
        // Create Lounge Background
        this.background = PIXI.Sprite.from('assets/lobby_background.webp');
        this.background.anchor.set(0.5);
        this.background.x = this.app.screen.width / 2;
        this.background.y = this.app.screen.height / 2;
        this.stage.addChild(this.background);

        // Add Firme F or cultural assets
        const chromeF = PIXI.Sprite.from('assets/chrome_f.webp');
        chromeF.anchor.set(0.5);
        chromeF.x = this.app.screen.width / 2;
        chromeF.y = this.app.screen.height / 2;
        this.stage.addChild(chromeF);

        // Apply Glint Shader
        const glintShader = ChromeFGlintShader.create();
        chromeF.filters = [glintShader];

        // GSAP Animation for Glint
        setInterval(() => {
            gsap.to(glintShader.uniforms, { 
                uOffset: 3.0, 
                duration: 1.5, 
                ease: "power2.inOut", 
                onComplete: () => {
                    glintShader.uniforms.uOffset = 0;
                }
            });
        }, 3000);

        // Add Boom Box
        this.addBoomBox();

        // Start Ambient Music
        this.playBackgroundMusic();

        // Add Arcade Cars
        this.addCars();

        console.log("Lounge World initialized with Firme F, boom box, and arcade cars.");
        this.isActive = true;
    }

    // Add Boom Box to the Scene
    addBoomBox() {
        const boomBox = PIXI.Sprite.from('assets/boom_box.webp');
        boomBox.anchor.set(0.5);
        boomBox.x = this.app.screen.width / 2 - 400;
        boomBox.y = this.app.screen.height / 2 + 200;
        boomBox.scale.set(1.2);
        this.stage.addChild(boomBox);
    }

    // Play Background Music
    playBackgroundMusic() {
        this.ambientMusic = new Howl({
            src: ['assets/audio/lounge_ambient_track.mp3'], // Priority soundtrack
            loop: true,
            volume: 0.7,
        });
        this.ambientMusic.play();
        console.log('Background music started.');
    }

    // Add Arcade Cars to the Scene
    addCars() {
        const carTextures = [
            'https://via.placeholder.com/150/FF0000/FFFFFF?text=Car1', 
            'https://via.placeholder.com/150/00FF00/FFFFFF?text=Car2'
        ];
        const spacing = 300;

        carTextures.forEach((texture, index) => {
            const car = PIXI.Sprite.from(texture);
            car.anchor.set(0.5);
            car.x = this.app.screen.width / 2 + (index - 0.5) * spacing;
            car.y = this.app.screen.height / 2 + 200;
            car.interactive = true;
            car.buttonMode = true;
            car.on('pointerdown', () => this.bounceCar(car));

            this.stage.addChild(car);
            this.cars.push(car);
        });
    }

    // GSAP Bounce Animation for Cars
    bounceCar(car) {
        gsap.to(car, { y: car.y - 50, duration: 0.3, ease: 'power2.out', yoyo: true, repeat: 1 });
        console.log('Car clicked and bounced:', car);
    }

    // Handle Transition to Boss World
    transitionToBoss(bossWorldName) {
        console.log(`Transitioning to boss world: ${bossWorldName}`);
        this.fadeOut(() => {
            this.stage.removeChild(this.background);
            this.stage.removeChildren();
            if (this.ambientMusic) this.ambientMusic.stop();

            // Example: Load the given boss world if available
            if (typeof BossWorld !== 'undefined') {
                const bossWorld = new BossWorld(this.stage, this.app, bossWorldName);
                bossWorld.initialize();
            } else {
                console.warn("BossWorld class not defined. Cannot complete transition.");
            }
        });
    }

    // Fade Out Lounge Scene
    fadeOut(onComplete) {
        const radialBlur = new PIXI.filters.RadialBlurFilter ? new PIXI.filters.RadialBlurFilter() : null;
        const rgbSplit = new PIXI.filters.RGBSplitFilter ? new PIXI.filters.RGBSplitFilter() : null;

        if (radialBlur) {
            radialBlur.innerRadius = 0;
            radialBlur.strength = 0;
        }
        if (rgbSplit) {
            rgbSplit.red = [-10, 0];
            rgbSplit.blue = [10, 0];
            this.stage.filters = [radialBlur, rgbSplit].filter(Boolean);
        }

        // Animating the Radial/Chromay Expansion
        const fade = new PIXI.Graphics();
        fade.beginFill(0x000000);
        fade.drawRect(0, 0, this.app.screen.width, this.app.screen.height);
        fade.endFill();
        fade.alpha = 0;
        this.stage.addChild(fade);

        const tl = gsap.timeline({
            onComplete: () => {
                this.stage.removeChild(fade);
                onComplete();
            }
        });

        tl.to(fade, { alpha: 1, duration: 1.5, ease: "power2.inOut" });
        if (radialBlur) tl.to(radialBlur, { strength: 20, duration: 2, ease: "power2.inOut" }, "-=1.5");
        if (rgbSplit) {
            tl.to(rgbSplit.red, { x: -40, duration: 2, ease: "power2.inOut" }, "-=2");
            tl.to(rgbSplit.blue, { x: 40, duration: 2, ease: "power2.inOut" }, "-=2");
        }
    }
}

// Example Usage
if (typeof window !== 'undefined') {
    const app = new PIXI.Application({
        width: 1920,
        height: 1080,
        backgroundColor: 0x000000,
    });
    document.body.appendChild(app.view);
    const lounge = new LoungeWorld(app.stage, app);
    lounge.initialize();
}

if (typeof module !== 'undefined') {
    module.exports = { LoungeWorld, ChromeFGlintShader };
}