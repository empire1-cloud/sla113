// Trigger the Latin Active Rose Petal Explosion, synced with Shadyboy G-Funk audio drop
const rosePetalEmitter = new RosePetalEmitter(app.stage);

function triggerExplosionWithSync(audioDropTime) {
    // Detonate petals right on the audio drop
    setTimeout(() => {
        // Trigger the rose petal explosion at the center of the screen
        console.log("Detonating Rose Petals synced to the Shadyboy G-Funk drop...");
        rosePetalEmitter.explode(app.screen.width / 2, app.screen.height / 2);

        // Destroy ParticleContainer after 3 seconds to free GPU memory
        setTimeout(() => {
            app.stage.removeChild(rosePetalEmitter.container);
            console.log("ParticleContainer removed to free GPU memory.");
        }, 3000);
    }, audioDropTime);
}

// Example usage: Sync the explosion 2000ms after the intro begins
triggerExplosionWithSync(2000);

console.log("Rose Petal Explosion triggered and GPU memory optimization initialized.");