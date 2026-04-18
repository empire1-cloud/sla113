// SLA113 Video Slots v2 — Aztec Gold v2
// Production Visual Layer
const GAME_CONFIG = {
  "type": "slot_machine",
  "name": "Aztec Gold v2",
  "version": "1.0.0",
  "built_by": "SLA113"
};
const ASSET_MANIFEST = [];

(async () => {
  const app = new PIXI.Application({ width: window.innerWidth, height: window.innerHeight, backgroundColor: 0x080010, antialias: true, resolution: window.devicePixelRatio || 1, autoDensity: true });
  document.body.appendChild(app.view);
  document.getElementById('loading').style.display = 'none';
  window.addEventListener('resize', () => app.renderer.resize(window.innerWidth, window.innerHeight));
  const W = () => app.screen.width, H = () => app.screen.height;

  // ═══ SYMBOL DEFINITIONS ═══
  const customSyms = GAME_CONFIG.custom_symbols;
  const BASE = customSyms && customSyms.length >= 5 ? customSyms.map(s => ({
    name: s.name, color: parseInt((s.color || '#d4af37').replace('#', ''), 16),
    weight: s.weight || 5, p3: s.payout || 5, p4: (s.payout || 5) * 3, p5: (s.payout || 5) * 10, shape: 'gem',
  })) : [
    { name: '7',       color: 0xff0000, weight: 2,  p3: 50, p4: 150, p5: 500, shape: 'seven' },
    { name: 'DIAMOND', color: 0x00c8ff, weight: 3,  p3: 25, p4: 75,  p5: 250, shape: 'diamond' },
    { name: 'CROWN',   color: 0xd4af37, weight: 4,  p3: 15, p4: 45,  p5: 150, shape: 'crown' },
    { name: 'BELL',    color: 0xffaa00, weight: 6,  p3: 10, p4: 30,  p5: 100, shape: 'bell' },
    { name: 'CHERRY',  color: 0xff4466, weight: 8,  p3: 5,  p4: 15,  p5: 50,  shape: 'cherry' },
    { name: 'LEMON',   color: 0x88ff44, weight: 10, p3: 3,  p4: 10,  p5: 30,  shape: 'fruit' },
    { name: 'PLUM',    color: 0x9944ff, weight: 10, p3: 3,  p4: 10,  p5: 30,  shape: 'fruit' },
    { name: 'ORANGE',  color: 0xff8800, weight: 10, p3: 4,  p4: 12,  p5: 40,  shape: 'fruit' },
  ];
  const WILD =    { name: 'WILD',    color: 0x00ff88, weight: 3, p3: 0, p4: 0, p5: 0, special: 'wild', shape: 'wild' };
  const SCATTER = { name: 'SCATTER', color: 0xff00ff, weight: 3, p3: 0, p4: 0, p5: 0, special: 'scatter', shape: 'scatter' };
  const BONUS =   { name: 'BONUS',   color: 0xd4af37, weight: 2, p3: 0, p4: 0, p5: 0, special: 'bonus', shape: 'bonus' };
  const COIN =    { name: 'COIN',    color: 0xffd700, weight: 2, p3: 0, p4: 0, p5: 0, special: 'coin', shape: 'coin' };
  const ALL = [WILD, SCATTER, BONUS, COIN, ...BASE];

  // ═══ CANVAS SYMBOL RENDERER ═══
  function renderSymbol(sym, size) {
    const c = document.createElement('canvas'); c.width = size; c.height = size;
    const ctx = c.getContext('2d'); const cx = size / 2, cy = size / 2, r = size * 0.35;
    const hex = '#' + sym.color.toString(16).padStart(6, '0');

    // Background glow
    const glow = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.4);
    glow.addColorStop(0, hex + '33'); glow.addColorStop(1, 'transparent');
    ctx.fillStyle = glow; ctx.fillRect(0, 0, size, size);

    if (sym.shape === 'seven') {
      ctx.font = `bold ${size * 0.55}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.shadowColor = hex; ctx.shadowBlur = 15;
      ctx.fillStyle = hex; ctx.fillText('7', cx, cy);
      ctx.shadowBlur = 0; ctx.strokeStyle = '#fff3'; ctx.lineWidth = 1; ctx.strokeText('7', cx, cy);
    } else if (sym.shape === 'diamond') {
      ctx.beginPath(); ctx.moveTo(cx, cy - r); ctx.lineTo(cx + r * 0.8, cy); ctx.lineTo(cx, cy + r); ctx.lineTo(cx - r * 0.8, cy); ctx.closePath();
      const dg = ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
      dg.addColorStop(0, '#ffffff88'); dg.addColorStop(0.3, hex); dg.addColorStop(0.7, hex + 'cc'); dg.addColorStop(1, '#ffffff44');
      ctx.fillStyle = dg; ctx.fill();
      ctx.strokeStyle = '#ffffff66'; ctx.lineWidth = 1.5; ctx.stroke();
      // Shine
      ctx.beginPath(); ctx.moveTo(cx - r * 0.3, cy - r * 0.3); ctx.lineTo(cx + r * 0.1, cy - r * 0.5); ctx.lineTo(cx + r * 0.3, cy - r * 0.1);
      ctx.fillStyle = '#ffffff44'; ctx.fill();
    } else if (sym.shape === 'crown') {
      ctx.beginPath();
      ctx.moveTo(cx - r, cy + r * 0.3); ctx.lineTo(cx - r, cy - r * 0.2);
      ctx.lineTo(cx - r * 0.5, cy + r * 0.1); ctx.lineTo(cx, cy - r);
      ctx.lineTo(cx + r * 0.5, cy + r * 0.1); ctx.lineTo(cx + r, cy - r * 0.2);
      ctx.lineTo(cx + r, cy + r * 0.3); ctx.closePath();
      const cg = ctx.createLinearGradient(cx, cy - r, cx, cy + r);
      cg.addColorStop(0, '#ffd700'); cg.addColorStop(1, '#b8860b');
      ctx.fillStyle = cg; ctx.fill();
      ctx.strokeStyle = '#fff4'; ctx.lineWidth = 1; ctx.stroke();
      // Gems on crown
      ctx.fillStyle = '#ff0000'; ctx.beginPath(); ctx.arc(cx, cy - r * 0.3, 3, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#00c8ff'; ctx.beginPath(); ctx.arc(cx - r * 0.45, cy, 2.5, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#00c8ff'; ctx.beginPath(); ctx.arc(cx + r * 0.45, cy, 2.5, 0, Math.PI * 2); ctx.fill();
    } else if (sym.shape === 'bell') {
      ctx.beginPath();
      ctx.moveTo(cx, cy - r); ctx.quadraticCurveTo(cx + r * 1.2, cy - r * 0.3, cx + r, cy + r * 0.5);
      ctx.lineTo(cx - r, cy + r * 0.5); ctx.quadraticCurveTo(cx - r * 1.2, cy - r * 0.3, cx, cy - r); ctx.closePath();
      const bg = ctx.createLinearGradient(cx - r, cy, cx + r, cy);
      bg.addColorStop(0, hex + 'aa'); bg.addColorStop(0.4, hex); bg.addColorStop(0.6, '#ffd700'); bg.addColorStop(1, hex + 'aa');
      ctx.fillStyle = bg; ctx.fill();
      ctx.strokeStyle = '#fff3'; ctx.lineWidth = 1; ctx.stroke();
      ctx.beginPath(); ctx.arc(cx, cy + r * 0.6, r * 0.15, 0, Math.PI * 2); ctx.fillStyle = hex; ctx.fill();
    } else if (sym.shape === 'cherry') {
      const drawBall = (bx, by) => {
        const cg = ctx.createRadialGradient(bx - 3, by - 3, 2, bx, by, r * 0.4);
        cg.addColorStop(0, '#ff8888'); cg.addColorStop(0.5, hex); cg.addColorStop(1, '#880022');
        ctx.beginPath(); ctx.arc(bx, by, r * 0.4, 0, Math.PI * 2); ctx.fillStyle = cg; ctx.fill();
        ctx.beginPath(); ctx.arc(bx - r * 0.12, by - r * 0.12, r * 0.08, 0, Math.PI * 2); ctx.fillStyle = '#ffffff66'; ctx.fill();
      };
      drawBall(cx - r * 0.3, cy + r * 0.2); drawBall(cx + r * 0.3, cy + r * 0.2);
      ctx.strokeStyle = '#228822'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cx - r * 0.3, cy + r * 0.2); ctx.quadraticCurveTo(cx - r * 0.1, cy - r * 0.8, cx + r * 0.1, cy - r * 0.5);
      ctx.moveTo(cx + r * 0.3, cy + r * 0.2); ctx.quadraticCurveTo(cx + r * 0.1, cy - r * 0.6, cx + r * 0.1, cy - r * 0.5); ctx.stroke();
      ctx.beginPath(); ctx.ellipse(cx + r * 0.2, cy - r * 0.55, r * 0.25, r * 0.12, 0.3, 0, Math.PI * 2); ctx.fillStyle = '#44aa22'; ctx.fill();
    } else if (sym.shape === 'wild') {
      ctx.shadowColor = hex; ctx.shadowBlur = 20;
      ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, ir = i % 2 === 0 ? r : r * 0.5;
        ctx[i === 0 ? 'moveTo' : 'lineTo'](cx + Math.cos(a) * ir, cy + Math.sin(a) * ir); }
      ctx.closePath(); ctx.fillStyle = hex; ctx.fill(); ctx.shadowBlur = 0;
      ctx.font = `bold ${size * 0.2}px monospace`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#000'; ctx.fillText('WILD', cx, cy);
    } else if (sym.shape === 'scatter') {
      ctx.shadowColor = hex; ctx.shadowBlur = 25;
      ctx.beginPath(); ctx.arc(cx, cy, r * 0.8, 0, Math.PI * 2);
      const sg = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 0.8);
      sg.addColorStop(0, '#ffffff'); sg.addColorStop(0.3, hex); sg.addColorStop(1, hex + '44');
      ctx.fillStyle = sg; ctx.fill(); ctx.shadowBlur = 0;
      // Rays
      for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6;
        ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * r * 0.5, cy + Math.sin(a) * r * 0.5);
        ctx.lineTo(cx + Math.cos(a) * r * 1.1, cy + Math.sin(a) * r * 1.1);
        ctx.strokeStyle = hex + '66'; ctx.lineWidth = 2; ctx.stroke(); }
      ctx.font = `bold ${size * 0.14}px monospace`; ctx.textAlign = 'center'; ctx.fillStyle = '#fff'; ctx.fillText('SCATTER', cx, cy + 1);
    } else if (sym.shape === 'bonus') {
      ctx.beginPath(); ctx.arc(cx, cy, r * 0.7, 0, Math.PI * 2);
      const bgg = ctx.createRadialGradient(cx - 5, cy - 5, 5, cx, cy, r * 0.7);
      bgg.addColorStop(0, '#ffd700'); bgg.addColorStop(1, '#8B6914');
      ctx.fillStyle = bgg; ctx.fill(); ctx.strokeStyle = '#fff3'; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.font = `bold ${size * 0.22}px monospace`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#000'; ctx.fillText('BONUS', cx, cy);
    } else if (sym.shape === 'coin') {
      ctx.beginPath(); ctx.arc(cx, cy, r * 0.65, 0, Math.PI * 2);
      const cgg = ctx.createRadialGradient(cx - 4, cy - 4, 3, cx, cy, r * 0.65);
      cgg.addColorStop(0, '#fff4'); cgg.addColorStop(0.5, '#ffd700'); cgg.addColorStop(1, '#b8860b');
      ctx.fillStyle = cgg; ctx.fill(); ctx.strokeStyle = '#d4af37'; ctx.lineWidth = 2; ctx.stroke();
      ctx.font = `bold ${size * 0.28}px serif`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#8B6914'; ctx.fillText('$', cx, cy);
    } else {
      // Generic gem/fruit
      ctx.beginPath(); ctx.arc(cx, cy, r * 0.7, 0, Math.PI * 2);
      const fg = ctx.createRadialGradient(cx - r * 0.2, cy - r * 0.2, r * 0.1, cx, cy, r * 0.7);
      fg.addColorStop(0, '#ffffff66'); fg.addColorStop(0.4, hex); fg.addColorStop(1, hex + '88');
      ctx.fillStyle = fg; ctx.fill();
      ctx.strokeStyle = '#ffffff33'; ctx.lineWidth = 1; ctx.stroke();
      ctx.beginPath(); ctx.arc(cx - r * 0.2, cy - r * 0.2, r * 0.15, 0, Math.PI * 2); ctx.fillStyle = '#ffffff33'; ctx.fill();
      if (sym.name.length <= 6) { ctx.font = `bold ${size * 0.14}px monospace`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff'; ctx.fillText(sym.name, cx, cy + r * 0.45); }
    }
    return PIXI.Texture.from(c);
  }

  // Pre-render all symbol textures
  const SYM_PX = 80;
  const symTextures = ALL.map(s => renderSymbol(s, SYM_PX));

  // ═══ GAME STATE ═══
  const REELS = 5, ROWS = 3;
  let credits = 10000, bet = 10, lines = 20, spinning = false;
  let freeSpins = 0, freeSpinMult = 1, totalWins = 0, cascadeCount = 0;
  let stickyWilds = [];
  const JP = { GRAND: { pool: 50000, color: 0xff0000 }, MAJOR: { pool: 10000, color: 0xd4af37 }, MINOR: { pool: 2000, color: 0x00c8ff }, MINI: { pool: 500, color: 0x44ff44 } };

  const pool = []; ALL.forEach((s, i) => { for (let w = 0; w < s.weight; w++) pool.push(i); });
  const rng = () => pool[Math.floor(Math.random() * pool.length)];

  const PL = [[1,1,1,1,1],[0,0,0,0,0],[2,2,2,2,2],[0,1,2,1,0],[2,1,0,1,2],[0,0,1,2,2],[2,2,1,0,0],[1,0,1,2,1],[1,2,1,0,1],[0,1,0,1,0],[2,1,2,1,2],[0,1,1,1,0],[2,1,1,1,2],[1,0,0,0,1],[1,2,2,2,1],[0,0,1,0,0],[2,2,1,2,2],[0,2,0,2,0],[2,0,2,0,2],[1,0,2,0,1]];

  // ═══ LAYOUT ═══
  const SW = 80, SH = 76, machW = REELS * SW + 30, machH = ROWS * SH + 20;
  const mx = W() / 2 - machW / 2, my = H() / 2 - machH / 2 - 25;

  // Cabinet
  const cab = new PIXI.Graphics();
  cab.beginFill(0x0c0016).drawRoundedRect(mx - 25, my - 70, machW + 50, machH + 210, 14).endFill();
  cab.lineStyle(2, 0xd4af37, 0.4).drawRoundedRect(mx - 25, my - 70, machW + 50, machH + 210, 14);
  cab.lineStyle(1, 0xd4af37, 0.15).drawRoundedRect(mx - 20, my - 65, machW + 40, machH + 200, 10);
  app.stage.addChild(cab);

  // Title
  const title = new PIXI.Text(GAME_CONFIG.name || 'SOVEREIGN SLOTS', { fontSize: 18, fill: 0xd4af37, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 4 });
  title.anchor.set(0.5); title.x = W() / 2; title.y = my - 40; app.stage.addChild(title);

  // Jackpot bar
  const jpTexts = {};
  Object.entries(JP).forEach(([name, jp], i) => {
    const x = mx + i * (machW / 4) + machW / 8;
    const bg = new PIXI.Graphics(); bg.beginFill(0x000000, 0.6).drawRoundedRect(x - 45, my - 60, 90, 18, 4).endFill();
    bg.lineStyle(1, jp.color, 0.4).drawRoundedRect(x - 45, my - 60, 90, 18, 4);
    app.stage.addChild(bg);
    const txt = new PIXI.Text(`${name}: ${jp.pool.toLocaleString()}`, { fontSize: 8, fill: jp.color, fontFamily: 'monospace', fontWeight: 'bold' });
    txt.anchor.set(0.5); txt.x = x; txt.y = my - 51; app.stage.addChild(txt); jpTexts[name] = txt;
  });

  // Reel window
  const reelBg = new PIXI.Graphics(); reelBg.beginFill(0x050008).drawRect(mx, my, machW, machH).endFill(); app.stage.addChild(reelBg);

  // Grid of symbol sprites
  const grid = [];
  const symSprites = [];
  for (let r = 0; r < REELS; r++) {
    grid.push([]); symSprites.push([]);
    for (let row = 0; row < ROWS; row++) {
      const idx = rng(); grid[r].push(idx);
      const spr = new PIXI.Sprite(symTextures[idx]);
      spr.anchor.set(0.5);
      spr.x = mx + 15 + r * SW + SW / 2;
      spr.y = my + 10 + row * SH + SH / 2;
      spr.width = SW - 8; spr.height = SH - 8;
      app.stage.addChild(spr);
      symSprites[r].push(spr);
    }
  }

  // Reel separators
  for (let r = 1; r < REELS; r++) {
    const sep = new PIXI.Graphics(); sep.lineStyle(1, 0x222222).moveTo(mx + 15 + r * SW - 2, my).lineTo(mx + 15 + r * SW - 2, my + machH);
    app.stage.addChild(sep);
  }

  // Win / Free spin text
  const winText = new PIXI.Text('', { fontSize: 22, fill: 0xd4af37, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 });
  winText.anchor.set(0.5); winText.x = W() / 2; winText.y = my + machH + 14; app.stage.addChild(winText);
  const fsBanner = new PIXI.Text('', { fontSize: 16, fill: 0xff00ff, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 3, stroke: 0x000000, strokeThickness: 3 });
  fsBanner.anchor.set(0.5); fsBanner.x = W() / 2; fsBanner.y = my - 14; fsBanner.visible = false; app.stage.addChild(fsBanner);

  function renderGrid() {
    for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) {
      symSprites[r][row].texture = symTextures[grid[r][row]];
      symSprites[r][row].alpha = 1; symSprites[r][row].scale.set(1);
    }
  }

  // ═══ CONTROLS ═══
  const btnY = my + machH + 40;
  function mkBtn(label, x, w, color, cb) {
    const b = new PIXI.Graphics(); b.beginFill(color).drawRoundedRect(0, 0, w, 40, 5).endFill();
    const t = new PIXI.Text(label, { fontSize: 14, fill: 0x000000, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 2 });
    t.anchor.set(0.5); t.x = w / 2; t.y = 20; b.addChild(t); b.x = x; b.y = btnY;
    b.interactive = true; b.cursor = 'pointer'; b.on('pointerdown', cb); app.stage.addChild(b); return { b, t };
  }
  const spinBtn = mkBtn('SPIN', W() / 2 - 75, 150, 0xd4af37, () => spin());
  const betBtn = mkBtn(`BET: ${bet}`, W() / 2 - 210, 90, 0x333333, () => { if (!spinning) { const bs = [1,5,10,25,50,100]; bet = bs[(bs.indexOf(bet) + 1) % bs.length]; betBtn.t.text = `BET: ${bet}`; updateHUD(); }});
  const lineBtn = mkBtn(`${lines}L`, W() / 2 + 120, 70, 0x333333, () => { if (!spinning) { const ls = [1,5,9,15,20]; lines = ls[(ls.indexOf(lines) + 1) % ls.length]; lineBtn.t.text = `${lines}L`; updateHUD(); }});

  // HUD
  const hud = document.createElement('div');
  hud.style.cssText = 'position:fixed;bottom:8px;left:50%;transform:translateX(-50%);color:#d4af37;font:11px monospace;text-transform:uppercase;letter-spacing:2px;z-index:100;background:rgba(0,0,0,0.85);padding:8px 20px;border:1px solid #d4af3730';
  document.body.appendChild(hud);

  function updateHUD() {
    const cost = freeSpins > 0 ? 0 : bet * lines;
    const fs = freeSpins > 0 ? ` | FREE: ${freeSpins} (x${freeSpinMult})` : '';
    hud.textContent = `CREDITS: ${credits.toLocaleString()} | COST: ${cost} | WON: ${totalWins.toLocaleString()}${fs}`;
    document.getElementById('score').textContent = credits.toLocaleString();
    Object.entries(JP).forEach(([n, j]) => { if (jpTexts[n]) jpTexts[n].text = `${n}: ${Math.floor(j.pool).toLocaleString()}`; });
  }
  updateHUD();

  // ═══ SPIN ═══
  const delay = ms => new Promise(r => setTimeout(r, ms));

  async function spin() {
    if (spinning) return;
    const cost = bet * lines;
    if (freeSpins <= 0 && credits < cost) return;
    spinning = true; cascadeCount = 0; winText.text = '';
    if (freeSpins > 0) { freeSpins--; fsBanner.text = `FREE SPINS: ${freeSpins} (x${freeSpinMult})`; if (freeSpins <= 0) { fsBanner.visible = false; stickyWilds = []; freeSpinMult = 1; } }
    else { credits -= cost; }
    Object.values(JP).forEach(j => { j.pool += cost * 0.0025; });

    // Animate: rapid symbol cycling then settle per reel
    for (let frame = 0; frame < 18; frame++) {
      for (let r = 0; r < REELS; r++) {
        if (frame >= 5 + r * 3) continue;
        for (let row = 0; row < ROWS; row++) { grid[r][row] = rng(); }
      }
      renderGrid();
      await delay(40 + frame * 5);
    }
    // Final result
    for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) grid[r][row] = rng();
    stickyWilds.forEach(sw => { grid[sw.r][sw.row] = 0; });
    renderGrid();

    // Evaluate
    let totalPay = 0; let cascading = true;
    while (cascading) {
      const { pay, wins, sc, bn, co } = evalGrid();
      if (pay > 0 || sc >= 3 || bn >= 3 || co >= 6) {
        totalPay += pay * (freeSpinMult > 1 ? freeSpinMult : 1);
        cascadeCount++;
        hlWins(wins); await delay(500);
        if (sc >= 3) { const nfs = sc >= 5 ? 25 : sc >= 4 ? 15 : 10; freeSpins += nfs; freeSpinMult = sc >= 4 ? 3 : 2; fsBanner.text = `FREE SPINS: ${freeSpins} (x${freeSpinMult})`; fsBanner.visible = true; totalPay += bet * lines * (sc >= 5 ? 50 : sc >= 4 ? 10 : 5);
          for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) if (ALL[grid[r][row]].special === 'wild') stickyWilds.push({ r, row }); }
        if (bn >= 3) { const prizes = [5,10,15,25,50,100,200]; totalPay += prizes[Math.floor(Math.random() * prizes.length)] * bet; winText.text = 'BONUS WHEEL!'; await delay(1000); }
        if (co >= 6) { let coinVal = 0; for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) if (ALL[grid[r][row]].special === 'coin') coinVal += [10,25,50,100,250][Math.floor(Math.random()*5)] * bet; totalPay += coinVal; winText.text = 'HOLD & SPIN!'; await delay(1000); }
        // Jackpot
        Object.entries(JP).forEach(([n, j]) => { if (Math.random() < (n === 'GRAND' ? 0.0001 : n === 'MAJOR' ? 0.001 : n === 'MINOR' ? 0.005 : 0.02) * cascadeCount) { totalPay += Math.floor(j.pool); winText.text = `${n} JACKPOT! +${Math.floor(j.pool).toLocaleString()}`; j.pool *= 0.1; } });
        if (wins.length > 0) { wins.forEach(pos => { const [r, row] = pos.split('-').map(Number); grid[r][row] = -1; });
          await delay(300);
          for (let r = 0; r < REELS; r++) { const col = grid[r].filter(s => s !== -1); while (col.length < ROWS) col.unshift(rng()); grid[r] = col; }
          renderGrid(); await delay(200);
        } else { cascading = false; }
      } else { cascading = false; }
    }
    if (totalPay > 0) { credits += totalPay; totalWins += totalPay; winText.text = `WIN: ${totalPay.toLocaleString()}${cascadeCount > 1 ? ` (x${cascadeCount} CASCADE)` : ''}`; winText.style.fill = totalPay >= bet * lines * 20 ? 0xff0000 : totalPay >= bet * lines * 5 ? 0xd4af37 : 0x44ff44; }
    updateHUD(); spinning = false;
  }

  function evalGrid() {
    let pay = 0; const wins = new Set(); let sc = 0, bn = 0, co = 0;
    for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) { const s = ALL[grid[r][row]]; if (s?.special === 'scatter') sc++; if (s?.special === 'bonus') bn++; if (s?.special === 'coin') co++; }
    for (let l = 0; l < Math.min(lines, PL.length); l++) {
      const ls = PL[l].map((row, r) => grid[r][row]);
      let pi = ls.find(i => ALL[i] && !ALL[i].special); if (pi === undefined) pi = ls[0];
      let cnt = 0; for (let i = 0; i < REELS; i++) { const s = ALL[ls[i]]; if (s?.special === 'wild' || ls[i] === pi) cnt++; else break; }
      if (cnt >= 3 && ALL[pi]) { const s = ALL[pi]; pay += (cnt === 5 ? s.p5 : cnt === 4 ? s.p4 : s.p3) * bet; for (let i = 0; i < cnt; i++) wins.add(`${i}-${PL[l][i]}`); }
    }
    return { pay, wins: [...wins], sc, bn, co };
  }

  function hlWins(positions) {
    for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) {
      if (positions.includes(`${r}-${row}`)) { symSprites[r][row].scale.set(1.15); }
      else { symSprites[r][row].alpha = 0.3; }
    }
  }

  document.addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); spin(); } });
  renderGrid(); updateHUD();
})();
