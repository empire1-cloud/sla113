// Main Stage Setup with Letterbox Scaling
const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x000000,
});

document.body.appendChild(app.view);

// Resize Function for Letterbox Scaling
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

// Add Event Listener to Window Resize
window.addEventListener('resize', resize);
resize(); // Initial Resize

console.log("PIXI.Application initialized with Letterbox scaling.");