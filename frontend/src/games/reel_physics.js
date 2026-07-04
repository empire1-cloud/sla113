// Reel Animation with Hydraulic Physics
function stopReelWithHydraulics(reel, targetY, onComplete) {
    // Reel Stops: Overshoot and Snap Back
    const overshootAmount = 20; // Pixels to overshoot
    const duration = 0.05; // Duration of the animation

    gsap.to(reel, {
        y: targetY - overshootAmount, // Overshoot target
        duration: duration,
        ease: "power2.out", // Fast ease for overshoot
        onComplete: () => {
            gsap.to(reel, {
                y: targetY, // Snap back to target
                duration: duration,
                ease: "elastic.out(1, 0.3)", // Elastic snap-back
                onComplete: onComplete, // Trigger any callback
            });
        },
    });

    // Trigger Screen Shake on Reel Stop
    triggerScreenShake();
}

// Screen Shake Implementation (Heavier, Mechanical Feel)
function triggerScreenShake(intensity = 10, duration = 0.05) {
    const originalX = app.stage.x;
    const originalY = app.stage.y;

    gsap.to(app.stage, {
        x: `+=${intensity}`,
        y: `+=${intensity}`,
        duration: duration,
        yoyo: true,
        repeat: 5,
        onComplete: () => {
            app.stage.x = originalX;
            app.stage.y = originalY;
        },
    });

    console.log("Screen shake triggered with intensity:", intensity);
}

// Hook into Reel Stop Logic
function onReelStop(reel, targetY) {
    stopReelWithHydraulics(reel, targetY, () => {
        console.log("Reel stopped at target position with hydraulic physics.");
    });
}

console.log("Reel animation updated with hydraulic physics and screen shake.");