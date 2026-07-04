// Aztec Tide (Game B) Scene Implementation
function loadAztecTide(app) {
    const stage = new PIXI.Container();

    // Aztec and Jade Crate Assets
    const aztec = PIXI.Sprite.from('assets/aztec.webp');
    aztec.anchor.set(0.5);
    aztec.x = app.screen.width / 2;
    aztec.y = app.screen.height / 2 - 150;
    stage.addChild(aztec);

    // Add Bloom Effect to Aztec Symbol
    addBloomEffect(aztec);

    const jadeCrate = PIXI.Sprite.from('assets/jade_crate.webp');
    jadeCrate.anchor.set(0.5);
    jadeCrate.x = app.screen.width / 2;
    jadeCrate.y = app.screen.height / 2 + 150;
    stage.addChild(jadeCrate);

    // Layer Addition
    app.stage.addChild(stage);

    console.log("Aztec Tide Scene loaded successfully.");
    return { stage };
}