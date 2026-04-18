// SLA113 Fish Shooter Engine v2 — Sovereign Fish Arena v2
// Production Visual Layer — Sprite-based + Canvas Fallback
const GAME_CONFIG = {
  "type": "fish_shooting",
  "name": "Sovereign Fish Arena v2",
  "version": "1.0.0",
  "built_by": "SLA113"
};
const ASSET_MANIFEST = [];

(async () => {
  const app = new PIXI.Application({ width: window.innerWidth, height: window.innerHeight, backgroundColor: 0x000a14, antialias: true, resolution: window.devicePixelRatio || 1, autoDensity: true });
  document.body.appendChild(app.view);
  document.getElementById('loading').style.display = 'none';
  window.addEventListener('resize', () => app.renderer.resize(window.innerWidth, window.innerHeight));
  const W = () => app.screen.width, H = () => app.screen.height;

  // ═══ SPRITE REGISTRY ═══
  const SPRITES = GAME_CONFIG.sprites || {};
  const loadedTextures = {};

  async function loadSprite(name, cfg) {
    try {
      const bt = PIXI.BaseTexture.from(cfg.sprite_url, { crossOrigin: 'anonymous' });
      await new Promise((res, rej) => { bt.on('loaded', res); bt.on('error', rej); setTimeout(rej, 5000); });
      const frames = [];
      for (let r = 0; r < cfg.rows; r++)
        for (let c = 0; c < cfg.columns; c++) {
          if (frames.length >= cfg.total_frames) break;
          frames.push(new PIXI.Texture(bt, new PIXI.Rectangle(c * cfg.frame_width, r * cfg.frame_height, cfg.frame_width, cfg.frame_height)));
        }
      const anims = {};
      if (cfg.animations) Object.entries(cfg.animations).forEach(([k, idxs]) => { anims[k] = idxs.map(i => frames[i]).filter(Boolean); });
      loadedTextures[name] = { frames, anims, cfg };
    } catch {}
  }
  await Promise.all(Object.entries(SPRITES).map(([n, c]) => loadSprite(n, c)));

  // ═══ CANVAS SYMBOL RENDERER ═══
  function drawFishCanvas(color, size, tier) {
    const c = document.createElement('canvas');
    const s = size * 4; c.width = s * 2.5; c.height = s * 1.8;
    const ctx = c.getContext('2d');
    const cx = s * 1.2, cy = s * 0.9;
    const hex = '#' + color.toString(16).padStart(6, '0');

    // Body gradient
    const grd = ctx.createRadialGradient(cx, cy, s * 0.1, cx, cy, s);
    grd.addColorStop(0, hex);
    grd.addColorStop(0.7, hex + 'cc');
    grd.addColorStop(1, hex + '33');

    // Body
    ctx.beginPath();
    ctx.moveTo(cx + s, cy);
    ctx.quadraticCurveTo(cx + s * 0.5, cy - s * 0.7, cx - s * 0.3, cy - s * 0.5);
    ctx.quadraticCurveTo(cx - s * 0.8, cy - s * 0.3, cx - s, cy);
    ctx.quadraticCurveTo(cx - s * 0.8, cy + s * 0.3, cx - s * 0.3, cy + s * 0.5);
    ctx.quadraticCurveTo(cx + s * 0.5, cy + s * 0.7, cx + s, cy);
    ctx.fillStyle = grd; ctx.fill();
    ctx.strokeStyle = hex; ctx.lineWidth = 1.5; ctx.stroke();

    // Tail
    ctx.beginPath();
    ctx.moveTo(cx - s, cy);
    ctx.lineTo(cx - s * 1.5, cy - s * 0.45);
    ctx.quadraticCurveTo(cx - s * 1.2, cy, cx - s * 1.5, cy + s * 0.45);
    ctx.closePath();
    ctx.fillStyle = hex + 'aa'; ctx.fill();

    // Dorsal fin
    ctx.beginPath();
    ctx.moveTo(cx + s * 0.2, cy - s * 0.45);
    ctx.quadraticCurveTo(cx, cy - s * 0.9, cx - s * 0.4, cy - s * 0.5);
    ctx.fillStyle = hex + '88'; ctx.fill();

    // Eye
    ctx.beginPath(); ctx.arc(cx + s * 0.55, cy - s * 0.1, s * 0.14, 0, Math.PI * 2);
    ctx.fillStyle = '#fff'; ctx.fill();
    ctx.beginPath(); ctx.arc(cx + s * 0.58, cy - s * 0.1, s * 0.07, 0, Math.PI * 2);
    ctx.fillStyle = '#000'; ctx.fill();
    ctx.beginPath(); ctx.arc(cx + s * 0.6, cy - s * 0.12, s * 0.025, 0, Math.PI * 2);
    ctx.fillStyle = '#fff'; ctx.fill();

    // Scales pattern
    ctx.globalAlpha = 0.15;
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.arc(cx + s * (0.3 - i * 0.2), cy, s * 0.25, -Math.PI * 0.5, Math.PI * 0.5);
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // Tier glow
    if (tier >= 5) {
      ctx.shadowColor = hex; ctx.shadowBlur = 20;
      ctx.beginPath(); ctx.arc(cx, cy, s * 0.8, 0, Math.PI * 2);
      ctx.strokeStyle = hex + '44'; ctx.lineWidth = 3; ctx.stroke();
      ctx.shadowBlur = 0;
    }

    return PIXI.Texture.from(c);
  }

  function drawBossCanvas(color, size, name) {
    const c = document.createElement('canvas');
    const s = size * 3; c.width = s * 3; c.height = s * 3;
    const ctx = c.getContext('2d');
    const cx = s * 1.5, cy = s * 1.5;
    const hex = '#' + color.toString(16).padStart(6, '0');

    // Aura
    const aura = ctx.createRadialGradient(cx, cy, s * 0.2, cx, cy, s * 1.4);
    aura.addColorStop(0, hex + '22'); aura.addColorStop(0.5, hex + '11'); aura.addColorStop(1, 'transparent');
    ctx.fillStyle = aura; ctx.fillRect(0, 0, c.width, c.height);

    // Body - large ornate fish/dragon shape
    ctx.beginPath();
    ctx.moveTo(cx + s * 1.2, cy);
    ctx.bezierCurveTo(cx + s, cy - s * 0.8, cx - s * 0.2, cy - s, cx - s * 0.8, cy - s * 0.4);
    ctx.bezierCurveTo(cx - s * 1.2, cy - s * 0.1, cx - s * 1.2, cy + s * 0.1, cx - s * 0.8, cy + s * 0.4);
    ctx.bezierCurveTo(cx - s * 0.2, cy + s, cx + s, cy + s * 0.8, cx + s * 1.2, cy);
    ctx.fillStyle = hex + 'dd'; ctx.fill();
    ctx.strokeStyle = hex; ctx.lineWidth = 3; ctx.stroke();

    // Crown/horns
    ctx.beginPath();
    ctx.moveTo(cx + s * 0.3, cy - s * 0.7);
    ctx.lineTo(cx + s * 0.1, cy - s * 1.2);
    ctx.lineTo(cx + s * 0.5, cy - s * 0.65);
    ctx.moveTo(cx - s * 0.1, cy - s * 0.75);
    ctx.lineTo(cx - s * 0.2, cy - s * 1.15);
    ctx.lineTo(cx + s * 0.15, cy - s * 0.7);
    ctx.fillStyle = '#d4af37'; ctx.fill();

    // Eyes (glowing red)
    ctx.shadowColor = '#ff0000'; ctx.shadowBlur = 15;
    ctx.beginPath(); ctx.arc(cx + s * 0.5, cy - s * 0.15, s * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = '#ff0000'; ctx.fill();
    ctx.beginPath(); ctx.arc(cx + s * 0.5, cy + s * 0.15, s * 0.1, 0, Math.PI * 2);
    ctx.fillStyle = '#ff0000'; ctx.fill();
    ctx.shadowBlur = 0;

    // Armor plates
    ctx.globalAlpha = 0.3;
    for (let i = 0; i < 4; i++) {
      ctx.beginPath();
      ctx.arc(cx + s * (0.4 - i * 0.3), cy, s * 0.35, -0.8, 0.8);
      ctx.strokeStyle = '#d4af37'; ctx.lineWidth = 2; ctx.stroke();
    }
    ctx.globalAlpha = 1;

    return PIXI.Texture.from(c);
  }

  // ═══ GAME STATE ═══
  let credits = 10000, betLevel = 1, totalWon = 0, totalShots = 0;
  const BET_LEVELS = [1, 2, 5, 10, 20, 50, 100];
  let currentWeapon = 0, jackpotPool = 0;
  let bossActive = false, bossTimer = 0, frozenUntil = 0;

  const WEAPONS = [
    { name: 'CANNON', color: 0xd4af37, cost: 1, damage: 1, speed: 12, bullets: 1 },
    { name: 'LASER', color: 0x00ffcc, cost: 3, damage: 2, speed: 30, bullets: 1 },
    { name: 'CHAIN', color: 0x6666ff, cost: 5, damage: 1, speed: 10, bullets: 1 },
    { name: 'BOMB', color: 0xff4444, cost: 8, damage: 3, speed: 8, bullets: 1 },
    { name: 'AUTO', color: 0xffaa00, cost: 2, damage: 1, speed: 14, bullets: 3 },
    { name: 'RAILGUN', color: 0xff00ff, cost: 15, damage: 8, speed: 40, bullets: 1 },
  ];

  const FISH_TYPES = [
    { name: 'Clownfish', tier: 0, color: 0xff6600, hp: 1, value: 2, size: 16, speed: 1.8, pattern: 'sine' },
    { name: 'Angelfish', tier: 0, color: 0x44ccff, hp: 1, value: 3, size: 18, speed: 1.5, pattern: 'sine' },
    { name: 'Pufferfish', tier: 1, color: 0xaacc00, hp: 2, value: 5, size: 20, speed: 1.2, pattern: 'sine' },
    { name: 'Swordfish', tier: 1, color: 0x6699ff, hp: 2, value: 8, size: 24, speed: 2.5, pattern: 'linear' },
    { name: 'Barracuda', tier: 2, color: 0xcc4444, hp: 3, value: 12, size: 28, speed: 2.0, pattern: 'zigzag' },
    { name: 'Manta Ray', tier: 3, color: 0x9966ff, hp: 5, value: 25, size: 36, speed: 1.0, pattern: 'circle' },
    { name: 'Hammerhead', tier: 3, color: 0x888888, hp: 6, value: 35, size: 40, speed: 1.5, pattern: 'zigzag' },
    { name: 'Sea Turtle', tier: 4, color: 0x33cc66, hp: 8, value: 50, size: 44, speed: 0.6, pattern: 'sine' },
    { name: 'Golden Dragon', tier: 5, color: 0xd4af37, hp: 15, value: 100, size: 52, speed: 0.8, pattern: 'circle' },
    { name: 'Mermaid Queen', tier: 5, color: 0xff66cc, hp: 12, value: 80, size: 48, speed: 1.0, pattern: 'sine' },
    { name: 'Aztec Serpent', tier: 6, color: 0x00ff88, hp: 25, value: 200, size: 58, speed: 0.5, pattern: 'circle' },
    { name: 'Sovereign Whale', tier: 7, color: 0xffffff, hp: 50, value: 500, size: 72, speed: 0.3, pattern: 'drift' },
  ];
  const SPAWN_W = [15, 15, 12, 10, 8, 6, 5, 4, 4, 3, 2, 1];
  const BOSS_TYPES = [
    { name: 'JAGUAR WARRIOR', color: 0xd4af37, hp: 200, value: 1000, size: 80, speed: 0.4 },
    { name: 'QUETZALCOATL', color: 0x00ffcc, hp: 300, value: 2000, size: 90, speed: 0.3 },
    { name: 'TEZCATLIPOCA', color: 0x9900ff, hp: 500, value: 5000, size: 100, speed: 0.2 },
  ];
  const SPECIAL_FISH = [
    { name: 'TREASURE', color: 0xd4af37, hp: 10, size: 32, speed: 0.3, effect: 'credits_burst', burstMin: 50, burstMax: 500 },
    { name: 'BOMB FISH', color: 0xff0000, hp: 5, size: 28, speed: 1.5, effect: 'explode_all', radius: 200 },
    { name: 'FREEZE', color: 0x00ccff, hp: 3, size: 24, speed: 2.0, effect: 'freeze_all', duration: 3000 },
    { name: 'JACKPOT CRAB', color: 0xff00ff, hp: 20, size: 36, speed: 0.5, effect: 'jackpot_trigger' },
  ];

  // Pre-render fish textures
  const fishTexCache = {};
  FISH_TYPES.forEach((t, i) => { fishTexCache[i] = drawFishCanvas(t.color, t.size, t.tier); });
  const bossTexCache = {};
  BOSS_TYPES.forEach((t, i) => { bossTexCache[i] = drawBossCanvas(t.color, t.size, t.name); });

  // ═══ OCEAN LAYERS ═══
  const layers = { bg: new PIXI.Container(), mid: new PIXI.Container(), fish: new PIXI.Container(), fx: new PIXI.Container(), ui: new PIXI.Container() };
  Object.values(layers).forEach(l => app.stage.addChild(l));

  // Deep ocean gradient
  const oceanGfx = new PIXI.Graphics();
  for (let y = 0; y < H(); y += 2) {
    const t = y / H();
    oceanGfx.lineStyle(2, ((Math.floor(t * 12) << 16) | (Math.floor(16 + t * 16) << 8) | Math.floor(20 + t * 40)));
    oceanGfx.moveTo(0, y).lineTo(W(), y);
  }
  layers.bg.addChild(oceanGfx);

  // Light rays
  for (let i = 0; i < 8; i++) {
    const ray = new PIXI.Graphics();
    ray.beginFill(0x0066aa, 0.03);
    const x = Math.random() * W(), w = 30 + Math.random() * 80;
    ray.moveTo(x, -20); ray.lineTo(x + w, -20); ray.lineTo(x + w * 0.6 + 50, H() + 20); ray.lineTo(x - 50, H() + 20); ray.closePath();
    ray.endFill();
    layers.bg.addChild(ray);
  }

  // Bubbles
  const bubbles = [];
  for (let i = 0; i < 50; i++) {
    const b = new PIXI.Graphics();
    const sz = 1 + Math.random() * 5;
    b.beginFill(0x44aaff, 0.12).drawCircle(0, 0, sz).endFill();
    b.lineStyle(0.5, 0x66ccff, 0.1).drawCircle(0, 0, sz);
    b.x = Math.random() * W(); b.y = Math.random() * H();
    b.vy = -0.15 - Math.random() * 0.5; b.vx = (Math.random() - 0.5) * 0.15;
    b.wob = Math.random() * Math.PI * 2;
    layers.bg.addChild(b); bubbles.push(b);
  }

  // Seaweed / coral at bottom
  for (let i = 0; i < 12; i++) {
    const weed = new PIXI.Graphics();
    const x = 40 + Math.random() * (W() - 80), h = 40 + Math.random() * 80;
    const col = [0x006633, 0x338844, 0x005522, 0x228833][Math.floor(Math.random() * 4)];
    weed.beginFill(col, 0.6);
    weed.moveTo(x - 4, H()); weed.quadraticCurveTo(x + (Math.random() - 0.5) * 20, H() - h * 0.6, x, H() - h);
    weed.quadraticCurveTo(x + (Math.random() - 0.5) * 20, H() - h * 0.4, x + 4, H());
    weed.closePath(); weed.endFill();
    layers.bg.addChild(weed);
  }

  // ═══ ENTITY ARRAYS ═══
  const fishes = [], bullets = [], particles = [], dmgNums = [];

  // ═══ FISH SPAWNING ═══
  function wRng() { const tot = SPAWN_W.reduce((a, b) => a + b); let r = Math.random() * tot; for (let i = 0; i < SPAWN_W.length; i++) { r -= SPAWN_W[i]; if (r <= 0) return i; } return 0; }

  function spawnFish(idx) {
    const type = FISH_TYPES[idx !== undefined ? idx : wRng()];
    const typeIdx = FISH_TYPES.indexOf(type);
    const f = new PIXI.Container();

    // Check for registered sprite first
    const sn = type.name.toLowerCase().replace(/\s+/g, '_');
    if (loadedTextures[sn]) {
      const td = loadedTextures[sn];
      const anim = new PIXI.AnimatedSprite(td.anims.idle || td.frames.slice(0, 4));
      anim.anchor.set(0.5); anim.animationSpeed = 0.1; anim.play();
      anim.scale.set((type.size * 2.5) / td.cfg.frame_width);
      f.addChild(anim); f._anim = anim; f._td = td;
    } else {
      // Canvas-rendered fish
      const spr = new PIXI.Sprite(fishTexCache[typeIdx]);
      spr.anchor.set(0.5); spr.scale.set(0.5);
      f.addChild(spr);
    }

    // HP bar for tier 2+
    if (type.tier >= 2) {
      const hpW = type.size * 1.2;
      const bg = new PIXI.Graphics(); bg.beginFill(0x000000, 0.6).drawRoundedRect(-hpW / 2, -type.size * 0.7, hpW, 4, 2).endFill();
      const fill = new PIXI.Graphics(); fill.beginFill(0x44ff44).drawRoundedRect(-hpW / 2, -type.size * 0.7, hpW, 4, 2).endFill();
      f.addChild(bg); f.addChild(fill);
      f._hpFill = fill; f._hpW = hpW;
    }

    // Value badge for tier 4+
    if (type.tier >= 4) {
      const badge = new PIXI.Text(`x${type.value}`, { fontSize: 10, fill: type.tier >= 6 ? 0xd4af37 : 0xffffff, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 });
      badge.anchor.set(0.5); badge.y = type.size * 0.55;
      f.addChild(badge);
    }

    const left = Math.random() > 0.5;
    f.x = left ? -60 : W() + 60;
    f.y = 50 + Math.random() * (H() - 150);
    f.vx = (left ? 1 : -1) * type.speed * (0.8 + Math.random() * 0.4);
    f.vy = (Math.random() - 0.5) * 0.4;
    f.scale.x = left ? 1 : -1;
    f.hp = Math.ceil(type.hp * (1 + betLevel * 0.1)); f.maxHp = f.hp;
    f.value = type.value; f.tier = type.tier; f.sz = type.size;
    f.pattern = type.pattern; f.phase = Math.random() * Math.PI * 2;
    f.alive = true; f.interactive = true; f.cursor = 'crosshair';
    f.hitArea = new PIXI.Circle(0, 0, type.size * 1.3);
    f.on('pointerdown', () => shoot(f));

    layers.fish.addChild(f); fishes.push(f);
  }

  function spawnBoss() {
    if (bossActive) return;
    bossActive = true;
    const type = BOSS_TYPES[Math.floor(Math.random() * BOSS_TYPES.length)];
    const bi = BOSS_TYPES.indexOf(type);
    const f = new PIXI.Container();

    const sn = type.name.toLowerCase().replace(/[\s,]+/g, '_');
    if (loadedTextures[sn]) {
      const td = loadedTextures[sn];
      const anim = new PIXI.AnimatedSprite(td.anims.idle || td.frames.slice(0, 4));
      anim.anchor.set(0.5); anim.animationSpeed = 0.08; anim.play();
      anim.scale.set((type.size * 2.5) / td.cfg.frame_width);
      f.addChild(anim); f._anim = anim; f._td = td;
    } else {
      const spr = new PIXI.Sprite(bossTexCache[bi]);
      spr.anchor.set(0.5); spr.scale.set(0.5);
      f.addChild(spr);
    }

    // Boss name
    const nm = new PIXI.Text(type.name, { fontSize: 14, fill: type.color, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 3, stroke: 0x000000, strokeThickness: 4 });
    nm.anchor.set(0.5); nm.y = -type.size - 10; f.addChild(nm);

    // HP bar
    const hpW = type.size * 2;
    const bg = new PIXI.Graphics(); bg.beginFill(0x000000, 0.7).drawRoundedRect(-hpW / 2, -type.size - 4, hpW, 6, 3).endFill();
    const fill = new PIXI.Graphics(); fill.beginFill(0xff0000).drawRoundedRect(-hpW / 2, -type.size - 4, hpW, 6, 3).endFill();
    f.addChild(bg); f.addChild(fill); f._hpFill = fill; f._hpW = hpW;

    // Multiplier
    const mult = new PIXI.Text(`x${type.value}`, { fontSize: 16, fill: 0xd4af37, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 4 });
    mult.anchor.set(0.5); mult.y = type.size + 8; f.addChild(mult);

    f.x = W() + 120; f.y = H() / 2; f.vx = -0.3; f.vy = 0;
    f.hp = Math.ceil(type.hp * (1 + betLevel * 0.3)); f.maxHp = f.hp;
    f.value = type.value; f.tier = 99; f.sz = type.size; f.isBoss = true;
    f.pattern = 'boss'; f.phase = 0; f.alive = true;
    f.interactive = true; f.cursor = 'crosshair';
    f.hitArea = new PIXI.Circle(0, 0, type.size * 1.5);
    f.on('pointerdown', () => shoot(f));

    layers.fish.addChild(f); fishes.push(f);
    announce(`BOSS: ${type.name}`, type.color);
  }

  function spawnSpecial() {
    const type = SPECIAL_FISH[Math.floor(Math.random() * SPECIAL_FISH.length)];
    const f = new PIXI.Container();
    const gfx = new PIXI.Graphics();
    gfx.lineStyle(2, type.color, 0.8);
    gfx.beginFill(type.color, 0.2).drawRoundedRect(-type.size, -type.size * 0.6, type.size * 2, type.size * 1.2, 8).endFill();
    // Sparkle
    gfx.beginFill(type.color, 0.5);
    for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2; gfx.drawCircle(Math.cos(a) * type.size * 0.5, Math.sin(a) * type.size * 0.3, 2); }
    gfx.endFill();
    f.addChild(gfx);
    const lbl = new PIXI.Text(type.name, { fontSize: 9, fill: type.color, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 });
    lbl.anchor.set(0.5); f.addChild(lbl);

    f.x = Math.random() > 0.5 ? -40 : W() + 40; f.y = 80 + Math.random() * (H() - 200);
    f.vx = (f.x < 0 ? 1 : -1) * type.speed; f.vy = (Math.random() - 0.5) * 0.3;
    f.hp = type.hp; f.maxHp = type.hp; f.value = 0; f.tier = 10; f.sz = type.size;
    f.alive = true; f.specialEffect = type.effect; f.effectParams = type;
    f.pattern = 'linear'; f.phase = 0;
    f.interactive = true; f.cursor = 'crosshair';
    f.hitArea = new PIXI.Circle(0, 0, type.size * 1.5);
    f.on('pointerdown', () => shoot(f));
    layers.fish.addChild(f); fishes.push(f);
  }

  // ═══ SHOOTING ═══
  function shoot(target) {
    const w = WEAPONS[currentWeapon], cost = w.cost * betLevel;
    if (credits < cost) return;
    credits -= cost; totalShots++; jackpotPool += cost * 0.02;

    for (let b = 0; b < w.bullets; b++) {
      const angle = Math.atan2(target.y - (H() - 70), target.x - W() / 2) + (b - (w.bullets - 1) / 2) * 0.1;
      const bullet = new PIXI.Graphics();
      bullet.beginFill(w.color).drawCircle(0, 0, 3 + betLevel * 0.3).endFill();
      // Trail glow
      bullet.beginFill(w.color, 0.3).drawCircle(0, 0, 6 + betLevel * 0.5).endFill();
      if (w.name === 'LASER') { bullet.beginFill(w.color, 0.15).drawRect(-3, -H(), 6, H()).endFill(); }
      bullet.x = W() / 2; bullet.y = H() - 70;
      bullet.vx = Math.cos(angle) * w.speed; bullet.vy = Math.sin(angle) * w.speed;
      bullet.damage = w.damage * betLevel; bullet.wtype = w.name; bullet.alive = true;
      layers.fx.addChild(bullet); bullets.push(bullet);
    }
    updateHUD();
  }

  function hit(fish, bullet) {
    if (!fish.alive) return;
    fish.hp -= bullet.damage;
    if (fish._hpFill) {
      fish._hpFill.clear();
      const pct = Math.max(0, fish.hp / fish.maxHp);
      fish._hpFill.beginFill(pct > 0.5 ? 0x44ff44 : pct > 0.25 ? 0xffaa00 : 0xff0000).drawRoundedRect(-fish._hpW / 2, fish.isBoss ? -fish.sz - 4 : -fish.sz * 0.7, fish._hpW * pct, fish.isBoss ? 6 : 4, 2).endFill();
    }
    dmgNum(fish.x, fish.y - fish.sz, bullet.damage, 0xffffff);
    fish.alpha = 0.4; setTimeout(() => { if (fish.alive) fish.alpha = 1; }, 80);
    if (fish._anim && fish._td?.anims?.attack) { fish._anim.textures = fish._td.anims.attack; fish._anim.play(); setTimeout(() => { if (fish.alive && fish._anim && fish._td?.anims?.idle) { fish._anim.textures = fish._td.anims.idle; fish._anim.play(); } }, 300); }
    if (fish.hp <= 0) kill(fish);
    // Chain
    if (bullet.wtype === 'CHAIN') {
      fishes.filter(f => f.alive && f !== fish).sort((a, b) => Math.hypot(a.x - fish.x, a.y - fish.y) - Math.hypot(b.x - fish.x, b.y - fish.y)).slice(0, 3).forEach(f => {
        f.hp -= bullet.damage * 0.5; dmgNum(f.x, f.y - f.sz, Math.floor(bullet.damage * 0.5), 0x6666ff);
        const ln = new PIXI.Graphics(); ln.lineStyle(2, 0x6666ff, 0.8).moveTo(fish.x, fish.y).lineTo(f.x, f.y); ln.life = 15; layers.fx.addChild(ln); particles.push(ln);
        if (f.hp <= 0) kill(f);
      });
    }
    if (bullet.wtype === 'BOMB') {
      const exp = new PIXI.Graphics(); exp.beginFill(0xff4444, 0.2).drawCircle(0, 0, 120).endFill(); exp.lineStyle(2, 0xff4444, 0.4).drawCircle(0, 0, 120);
      exp.x = fish.x; exp.y = fish.y; exp.life = 20; layers.fx.addChild(exp); particles.push(exp);
      fishes.filter(f => f.alive && f !== fish && Math.hypot(f.x - fish.x, f.y - fish.y) < 120).forEach(f => { f.hp -= bullet.damage; if (f.hp <= 0) kill(f); });
    }
  }

  function kill(fish) {
    fish.alive = false;
    const win = fish.value * betLevel; credits += win; totalWon += win;
    if (fish._anim && fish._td?.anims?.death) { fish._anim.textures = fish._td.anims.death; fish._anim.loop = false; fish._anim.play(); fish._anim.onComplete = () => { fish.visible = false; }; }
    else { setTimeout(() => { fish.visible = false; }, 200); }
    // Special effects
    if (fish.specialEffect === 'credits_burst') { const b = fish.effectParams.burstMin + Math.floor(Math.random() * (fish.effectParams.burstMax - fish.effectParams.burstMin)); credits += b; announce(`TREASURE! +${b}`, 0xd4af37); }
    else if (fish.specialEffect === 'explode_all') { fishes.filter(f => f.alive && Math.hypot(f.x - fish.x, f.y - fish.y) < 200).forEach(f => { f.hp = 0; kill(f); }); announce('BOMB!', 0xff0000); }
    else if (fish.specialEffect === 'freeze_all') { frozenUntil = Date.now() + 3000; announce('FREEZE!', 0x00ccff); }
    else if (fish.specialEffect === 'jackpot_trigger') { const jp = Math.floor(jackpotPool); credits += jp; jackpotPool = 0; announce(`JACKPOT! +${jp}`, 0xff00ff); }
    if (fish.isBoss) { bossActive = false; announce(`BOSS KILLED! +${win}`, 0xd4af37); }
    // Particles
    for (let p = 0; p < (fish.tier >= 5 ? 25 : 10); p++) {
      const pt = new PIXI.Graphics(); pt.beginFill(fish.tier >= 5 ? 0xd4af37 : 0x44aaff).drawCircle(0, 0, 1 + Math.random() * 3).endFill();
      pt.x = fish.x; pt.y = fish.y; pt.vx = (Math.random() - 0.5) * 7; pt.vy = (Math.random() - 0.5) * 7; pt.life = 25;
      layers.fx.addChild(pt); particles.push(pt);
    }
    dmgNum(fish.x, fish.y - fish.sz - 15, `+${win}`, fish.tier >= 5 ? 0xd4af37 : 0x44ff44);
    updateHUD();
  }

  function dmgNum(x, y, text, color) {
    const t = new PIXI.Text(String(text), { fontSize: String(text).startsWith('+') ? 16 : 11, fill: color, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 });
    t.anchor.set(0.5); t.x = x; t.y = y; t.vy = -1.5; t.life = 45;
    layers.ui.addChild(t); dmgNums.push(t);
  }

  function announce(text, color) {
    const t = new PIXI.Text(text, { fontSize: 30, fill: color, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 4, stroke: 0x000000, strokeThickness: 5 });
    t.anchor.set(0.5); t.x = W() / 2; t.y = H() / 2 - 60; t.life = 100;
    layers.ui.addChild(t); dmgNums.push(t);
  }

  // ═══ TURRET ═══
  const turret = new PIXI.Container();
  const tBase = new PIXI.Graphics(); tBase.beginFill(0x1a1a1a).drawRoundedRect(-35, -8, 70, 28, 6).endFill(); tBase.lineStyle(2, 0xd4af37).drawRoundedRect(-35, -8, 70, 28, 6);
  const tBarrel = new PIXI.Graphics(); tBarrel.beginFill(0x333333).drawRect(-5, -45, 10, 45).endFill(); tBarrel.lineStyle(1, 0xd4af37).drawRect(-5, -45, 10, 45);
  turret.addChild(tBarrel); turret.addChild(tBase);
  turret.x = W() / 2; turret.y = H() - 35; layers.ui.addChild(turret);
  const cross = new PIXI.Graphics();
  cross.lineStyle(1.5, 0xff0000, 0.5).drawCircle(0, 0, 20).moveTo(-24, 0).lineTo(24, 0).moveTo(0, -24).lineTo(0, 24);
  cross.lineStyle(1, 0xd4af37, 0.25).drawCircle(0, 0, 10);
  cross.zIndex = 999; layers.ui.addChild(cross);
  app.view.addEventListener('mousemove', e => { cross.x = e.offsetX; cross.y = e.offsetY; tBarrel.rotation = Math.atan2(e.offsetY - turret.y, e.offsetX - turret.x) + Math.PI / 2; });

  // ═══ HUD ═══
  const mkHud = (css) => { const d = document.createElement('div'); d.style.cssText = css; document.body.appendChild(d); return d; };
  const hudMain = mkHud('position:fixed;top:8px;left:50%;transform:translateX(-50%);color:#d4af37;font:12px monospace;text-transform:uppercase;letter-spacing:2px;z-index:100;background:rgba(0,0,0,0.85);padding:8px 20px;border:1px solid #d4af3730;display:flex;gap:20px');
  const hudWeapons = mkHud('position:fixed;bottom:8px;left:50%;transform:translateX(-50%);color:#d4af37;font:10px monospace;text-transform:uppercase;letter-spacing:1px;z-index:100;background:rgba(0,0,0,0.85);padding:6px 16px;border:1px solid #d4af3730;display:flex;gap:10px');
  const hudJP = mkHud('position:fixed;top:8px;right:12px;color:#ff00ff;font:15px monospace;font-weight:bold;text-transform:uppercase;letter-spacing:3px;z-index:100;background:rgba(0,0,0,0.85);padding:10px 20px;border:1px solid #ff00ff30');

  function updateHUD() {
    hudMain.innerHTML = `<span>CREDITS: <b style="color:#fff">${credits.toLocaleString()}</b></span><span>BET: <b>x${betLevel}</b></span><span>WON: <b style="color:#44ff44">${totalWon.toLocaleString()}</b></span>`;
    hudWeapons.innerHTML = WEAPONS.map((w, i) => `<span style="color:${i === currentWeapon ? '#' + w.color.toString(16).padStart(6, '0') : '#444'};cursor:pointer;padding:2px 6px;border:1px solid ${i === currentWeapon ? '#' + w.color.toString(16).padStart(6, '0') + '60' : '#222'};background:${i === currentWeapon ? '#' + w.color.toString(16).padStart(6, '0') + '15' : 'transparent'}" data-w="${i}">[${i + 1}] ${w.name}</span>`).join('');
    hudJP.innerHTML = `JACKPOT: <b style="color:#ffd700">${Math.floor(jackpotPool).toLocaleString()}</b>`;
    document.getElementById('score').textContent = credits.toLocaleString();
  }
  updateHUD();
  hudWeapons.addEventListener('click', e => { const i = e.target.dataset.w; if (i !== undefined) { currentWeapon = parseInt(i); updateHUD(); } });
  document.addEventListener('keydown', e => {
    const n = parseInt(e.key); if (n >= 1 && n <= 6) { currentWeapon = n - 1; updateHUD(); }
    if (e.key === 'q') { const i = BET_LEVELS.indexOf(betLevel); betLevel = BET_LEVELS[Math.max(0, i - 1)]; updateHUD(); }
    if (e.key === 'e') { const i = BET_LEVELS.indexOf(betLevel); betLevel = BET_LEVELS[Math.min(BET_LEVELS.length - 1, i + 1)]; updateHUD(); }
  });

  // ═══ SPAWN TIMERS ═══
  for (let i = 0; i < 15; i++) spawnFish();
  setInterval(() => { if (fishes.filter(f => f.alive).length < 20) spawnFish(); }, 1500);
  setInterval(spawnSpecial, 20000);
  setTimeout(spawnBoss, 25000);
  setInterval(() => { bossTimer += 1000; if (bossTimer >= 45000) { bossTimer = 0; spawnBoss(); } }, 1000);

  // ═══ GAME LOOP ═══
  app.ticker.add(() => {
    const now = Date.now(), frozen = now < frozenUntil;

    fishes.forEach(f => {
      if (!f.alive) return;
      if (frozen && !f.isBoss) { f.alpha = 0.5 + Math.sin(now / 200) * 0.2; return; }
      f.alpha = 1;
      const t = now / 1000 + f.phase;
      if (f.pattern === 'sine') { f.x += f.vx; f.y += Math.sin(t * 2) * 1.5; }
      else if (f.pattern === 'zigzag') { f.x += f.vx; f.y += Math.sin(t * 4) * 2.5; }
      else if (f.pattern === 'circle') { f.x += f.vx; f.y += Math.cos(t * 1.5) * 2; }
      else if (f.pattern === 'drift') { f.x += f.vx * 0.5; f.y += Math.sin(t * 0.5) * 0.8; }
      else if (f.pattern === 'boss') { if (f.x > W() * 0.7) f.vx = -0.4; else if (f.x < W() * 0.3) f.vx = 0.4; f.x += f.vx; f.y = H() / 2 + Math.sin(t) * H() * 0.25; }
      else { f.x += f.vx; f.y += f.vy; }
      if (f.y < 40) f.vy = Math.abs(f.vy || 0.5); if (f.y > H() - 90) f.vy = -Math.abs(f.vy || 0.5);
      if (!f.isBoss && (f.x < -100 || f.x > W() + 100)) { f.alive = false; f.visible = false; }
    });

    for (let i = fishes.length - 1; i >= 0; i--) if (!fishes[i].alive && !fishes[i].visible) { layers.fish.removeChild(fishes[i]); fishes.splice(i, 1); }

    bullets.forEach(b => {
      if (!b.alive) return;
      b.x += b.vx; b.y += b.vy;
      if (b.x < -20 || b.x > W() + 20 || b.y < -20 || b.y > H() + 20) { b.alive = false; b.visible = false; return; }
      fishes.forEach(f => { if (f.alive && b.alive && Math.hypot(f.x - b.x, f.y - b.y) < f.sz * 1.2) { hit(f, b); if (b.wtype !== 'LASER') { b.alive = false; b.visible = false; } } });
    });
    for (let i = bullets.length - 1; i >= 0; i--) if (!bullets[i].alive) { layers.fx.removeChild(bullets[i]); bullets.splice(i, 1); }

    for (let i = particles.length - 1; i >= 0; i--) { const p = particles[i]; if (p.vx !== undefined) { p.x += p.vx; p.y += p.vy; } p.life--; p.alpha = Math.max(0, p.life / 25); if (p.life <= 0) { layers.fx.removeChild(p); particles.splice(i, 1); } }
    for (let i = dmgNums.length - 1; i >= 0; i--) { const d = dmgNums[i]; d.y += d.vy || -1; d.life--; d.alpha = Math.max(0, d.life / 45); if (d.life <= 0) { layers.ui.removeChild(d); dmgNums.splice(i, 1); } }

    bubbles.forEach(b => { b.x += b.vx + Math.sin(now / 1000 + b.wob) * 0.08; b.y += b.vy; if (b.y < -10) { b.y = H() + 10; b.x = Math.random() * W(); } });
  });
})();
