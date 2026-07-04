import * as PIXI from 'pixi.js';

const app = new PIXI.Application({
    width: 1920,
    height: 1080,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
    backgroundColor: 0x1e1e1e, // Deep grey for a sleek lobby look
});

document.body.appendChild(app.view);

// Scrollable Lobby View
const lobbyContainer = new PIXI.Container();
const scrollableMask = new PIXI.Graphics()
    .beginFill(0x000000)
    .drawRect(0, 0, 1920, 1080) // Limits the scrolling area
    .endFill();
lobbyContainer.mask = scrollableMask;
app.stage.addChild(scrollableMask);

// Add tables dynamically
const tables = [];
const TABLE_COUNT = 10; // Example: Number of tables in the lobby
for (let i = 0; i < TABLE_COUNT; i++) {
    const table = new PIXI.Container();
    const tableBackground = new PIXI.Graphics()
        .beginFill(0x303030)
        .drawRoundedRect(100, i * 150 + 50, 1720, 100, 10) // Table shapes
        .endFill();

    const tableText = new PIXI.Text(`Table ${i + 1}`, {
        fontSize: 32,
        fill: 0xffffff,
        fontWeight: 'bold',
    });
    tableText.x = 130;
    tableText.y = i * 150 + 80;

    table.addChild(tableBackground, tableText);
    tables.push(table);
    lobbyContainer.addChild(table);
}

// Add scrolling logic
let dy = 0;
window.addEventListener('wheel', (e) => {
    e.preventDefault();
    dy += e.deltaY * 0.1;
    dy = Math.min(Math.max(dy, 0), TABLE_COUNT * 150 - 1080);
    lobbyContainer.y = -dy;
});

app.stage.addChild(lobbyContainer);