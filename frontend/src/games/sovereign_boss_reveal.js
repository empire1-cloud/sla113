// Latin Active Boss Reveal Logic with 808-Kick Synced Screen Shake
class SovereignBossReveal {
    constructor(stage, app, lounge) {
        this.stage = stage;
        this.app = app;
        this.lounge = lounge; // Inject lounge instance for transitions
        this.screenShakeIntensity = 20; // Intensity of screen shake
        this.isShaking = false;
    }

    // Start the Boss Reveal Sequence
    startReveal(boneSovereignTexture) {
        // Add the Bone Sovereign sprite
        this.boneSovereign = PIXI.Sprite.from(boneSovereignTexture);
        this.boneSovereign.anchor.set(0.5);
        this.boneSovereign.x = this.app.screen.width / 2;
        this.boneSovereign.y = this.app.screen.height / 2;
        this.boneSovereign.scale.set(0.5);
        this.stage.addChild(this.boneSovereign);

        // Scale up Bone Sovereign
        gsap.to(this.boneSovereign.scale, { x: 3.0, y: 3.0, duration: 0 }); // Start oversized for impact
        gsap.to(this.boneSovereign.scale, { x: 1.0, y: 1.0, duration: 1, ease: "power4.out" })
          .add(() => {
              this.triggerHydraulicLanding();
              this.initializeNeonIgnition();
          });
}
        triggerHydraulicLanding() {
        this.triggerScreenShake();

        // Particle Burst logic
        const particleContainer = new PIXI.ParticleContainer(500, { vertices: true });
        this.stage.addChild(particleContainer);
        for (let i = 0; i < 500; i++) {
            const goldCoin = PIXI.Sprite.from('assets/input_file_12_s.webp');
            goldCoin.anchor.set(0.5);
            goldCoin.x = this.boneSovereign.x;
            goldCoin.y = this.boneSovereign.y;
            goldCoin.scale.set(0.2);
            particleContainer.addChild(goldCoin);

            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 200 + 100;
            gsap.to(goldCoin, {
                x: this.boneSovereign.x + Math.cos(angle) * distance,
                y: this.boneSovereign.y + Math.sin(angle) * distance,
                alpha: 0,
                duration: 1.5,
                onComplete: () => particleContainer.removeChild(goldCoin)
            });
        }
    }

    initializeNeonIgnition() {
        const neonBloom = new PIXI.filters.BloomFilter();
        neonBloom.bloomScale = 0;
        neonBloom.threshold = 0.5;
        this.boneSovereign.filters = [neonBloom];

        gsap.to(neonBloom, {
            bloomScale: 1.5,
            yoyo: true,
            repeat: -1,
            duration: 0.2, // Adjust timing to sync with Talkbox
        });
    }

    


    // Sync Screen Shake Effects
    syncScreenShakeTo808() {
        const kickPattern = [0, 0.5, 1, 1.5, 2]; // Example 808-kick timings in seconds
        kickPattern.forEach((time, index) => {
            gsap.delayedCall(time, () => {
                this.triggerScreenShake();
                if (index === kickPattern.length - 1) {
                    this.stopScreenShake(); // Stop shaking after last kick
                }
            });
        });
    }

    // Trigger a single screen shake
    triggerScreenShake() {
        if (this.isShaking) return;
        this.isShaking = true;

        gsap.to(this.stage, {
            x: `+=${this.screenShakeIntensity}`,
            yoyo: true,
            repeat: 5, // Shake for 5 frames per kick
            duration: 0.05,
            onComplete: () => {
                this.stage.x = 0;
                this.isShaking = false;
            },
        });
    }

    // Stop the shake (failsafe, if needed)
    stopScreenShake() {
        this.isShaking = false;
        gsap.killTweensOf(this.stage);
        this.stage.x = 0;
        this.stage.y = 0;
    }

    // Trigger Sovereign Bleed Particle Effect on Boss Hits
    triggerSovereignBleed(x, y, numCoins) {
        const particleContainer = new PIXI.ParticleContainer(numCoins, { vertices: true });
        this.stage.addChild(particleContainer);
        for (let i = 0; i < numCoins; i++) {
            const coin = PIXI.Sprite.from('assets/processed/small_gold_s.webp');
            coin.anchor.set(0.5);
            coin.x = x;
            coin.y = y;
            coin.scale.set(0.3);
            particleContainer.addChild(coin);

            // Animate Coin Particles
            const angle = Math.random() * Math.PI * 2;
            const distance = Math.random() * 100 + 50;
            gsap.to(coin, {
                x: x + Math.cos(angle) * distance,
                y: y + Math.sin(angle) * distance,
                alpha: 0,
                duration: 1.5,
                onComplete: () => particleContainer.removeChild(coin)
            });
        }
    }

    // Trigger Final Sovereign Fountain after Boss Death
    triggerSovereignFountain(playerX, playerY) {
        const numCoins = 1000;
        const particleContainer = new PIXI.ParticleContainer(numCoins, { vertices: true });
        this.stage.addChild(particleContainer);

        for (let i = 0; i < numCoins; i++) {
            const coin = PIXI.Sprite.from('assets/processed/small_gold_s.webp');
            coin.anchor.set(0.5);
            coin.x = this.app.screen.width / 2;
            coin.y = this.app.screen.height / 2;
            coin.scale.set(0.3);
            particleContainer.addChild(coin);

            // Magnetize Coins to Player Position
            gsap.to(coin, {
                x: playerX,
                y: playerY,
                duration: 3,
                ease: 'power2.out',
                onComplete: () => particleContainer.removeChild(coin)
            });
        }

        // Victory Flash and Remove Boss
        this.triggerVictoryFlash();
    }

    // Victory Screen Flash
    triggerVictoryFlash() {
        const flash = new PIXI.Graphics();
        flash.beginFill(0xffffff);
        flash.drawRect(0, 0, this.app.screen.width, this.app.screen.height);
        flash.endFill();
        this.stage.addChild(flash);
        gsap.to(flash, { alpha: 0, duration: 0.1, onComplete: () => this.stage.removeChild(flash) });
    }
}

// Example Usage (Integration with the full sequence)
const lounge = new LoungeWorld(app.stage, app); // Injected Lounge Instance
const bossReveal = new SovereignBossReveal(app.stage, app, lounge);

// Start Lounge, then Transition to Boss
lounge.initialize();

// Example Trigger Reveal
bossReveal.startReveal('assets/processed/bone_sovereign.webp');