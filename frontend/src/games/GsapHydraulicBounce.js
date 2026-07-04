import { gsap } from 'gsap';

export function skillStop(reel, targetY) {
    // Kill existing animations
    gsap.killTweensOf(reel);

    // Snap reel to the target position with hydraulic bounce
    gsap.to(reel, {
        y: targetY,
        duration: 0.05, // Instantaneous stop
        ease: "expo.out", // Hard mechanical stop
        onComplete: () => {
            // Heavy bounce effect with squash/stretch animation
            gsap.fromTo(reel,
                { scaleY: 1.1, scaleX: 0.9 }, // Squash
                {
                    scaleY: 1,
                    scaleX: 1,
                    duration: 0.3,
                    ease: "elastic.out(1, 0.3)", // Stretch rebound
                    onComplete: () => {
                        applyScreenShake(); // Add final thud with screen shake
                    }
                }
            );
        }
    });
}

function applyScreenShake() {
    gsap.to(app.stage, {
        x: "+=10", // Shake intensity
        y: "+=10",
        duration: 0.05,
        repeat: 5,
        yoyo: true,
        onComplete: () => {
            app.stage.x = 0;
            app.stage.y = 0;
        }
    });
}