// Test script for validating SLA113 Standards with pixi.js-legacy in Node.js
const { JSDOM } = require('jsdom');
const PIXI = require('pixi.js-legacy');
const gsap = require('gsap');

// Simulate browser environment with jsdom
const { window } = new JSDOM('<!DOCTYPE html><html><body></body></html>');
global.document = window.document;
global.window = window;
global.navigator = window.navigator;

global.Image = window.Image;
global.HTMLCanvasElement = window.HTMLCanvasElement;

global.requestAnimationFrame = (callback) => {
    return setTimeout(callback, 1000 / 60);
};
global.cancelAnimationFrame = (id) => {
    clearTimeout(id);
};

// Initialize PIXI application
const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    backgroundColor: 0x000000,
});

global.document.body.appendChild(app.view);

// Add Firme F badge
const firmeF = PIXI.Sprite.from('assets/processed/firme_f_badge.webp');
firmeF.anchor.set(0.5);
firmeF.x = app.screen.width / 2;
firmeF.y = app.screen.height / 2;
app.stage.addChild(firmeF);

// Specular Glint Shader
const glintShader = new PIXI.Filter(null, `
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

firmeF.filters = [glintShader, new PIXI.filters.BloomFilter(8)];

// GSAP Test Animations
const tl = gsap.timeline();

// Glint animation
tl.to(glintShader.uniforms, { uOffset: 3.0, duration: 1.5, ease: "power2.inOut" });
// Rose pulse animation
gsap.to(firmeF.scale, { x: 1.05, y: 1.05, duration: 2, repeat: -1, yoyo: true });

// Elastic bounce interaction
firmeF.interactive = true;
firmeF.on('pointerdown', () => {
    gsap.fromTo(firmeF.scale, { x: 0.8, y: 0.8 }, { x: 1, y: 1, duration: 0.6, ease: "elastic.out(1, 0.3)" });
    console.log("Interactives Complete !!");
});

console.log("SLA113 Test script loaded successfully. Ready for testing.");