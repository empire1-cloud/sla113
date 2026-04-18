// SLA113 Fish Shooter v3 — Aztec Depths v5
// FireKirin Production Parity
const GAME_CONFIG = {
  "type": "fish_shooting",
  "name": "Aztec Depths v5",
  "version": "1.0.0",
  "built_by": "SLA113",
  "sprites": {
    "quetzalflare_prismwing": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/m9d2kcms_spritesheet1%20%282%29.jpg",
      "frame_width": 200,
      "frame_height": 200,
      "columns": 5,
      "rows": 5,
      "total_frames": 25,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3
        ],
        "attack": [
          4,
          5,
          6,
          7
        ],
        "fire_breath": [
          8,
          9,
          10,
          11
        ],
        "lightning": [
          12,
          13
        ],
        "wing_spread": [
          14,
          15,
          16,
          17
        ],
        "death": [
          20,
          21,
          22,
          23,
          24
        ]
      }
    },
    "mictlantecuilti_bone_sovereign": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/aufgqv07_spritesheet1%20%285%29.jpg",
      "frame_width": 256,
      "frame_height": 341,
      "columns": 4,
      "rows": 3,
      "total_frames": 12,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3
        ],
        "shield": [
          4
        ],
        "attack": [
          5,
          6,
          7
        ],
        "fire": [
          8,
          9
        ],
        "explosion": [
          10
        ],
        "defend": [
          11
        ]
      }
    },
    "quetzalcoatl_fireborn": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/vr76ezmx_spritesheet1%20%284%29.jpg",
      "frame_width": 256,
      "frame_height": 256,
      "columns": 4,
      "rows": 4,
      "total_frames": 16,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3
        ],
        "fire_breath": [
          4,
          5,
          6,
          7
        ],
        "attack": [
          8,
          9,
          10,
          11
        ],
        "death": [
          12,
          13,
          14,
          15
        ]
      }
    },
    "jaguar_warrior": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/xooi0xfr_boss%20%283%29.jpg",
      "frame_width": 512,
      "frame_height": 512,
      "columns": 1,
      "rows": 1,
      "total_frames": 1,
      "animations": {
        "idle": [
          0
        ]
      }
    },
    "ocelotl_voidmane": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/ncd8zsod_unnamed%20%284%29.jpg",
      "frame_width": 270,
      "frame_height": 340,
      "columns": 4,
      "rows": 3,
      "total_frames": 12,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3
        ],
        "attack": [
          4,
          5,
          6,
          7
        ],
        "wing_spread": [
          8,
          9,
          10,
          11
        ]
      }
    },
    "aztec_fish_species": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/cvci6vxx_spritesheet2_fish.jpg",
      "frame_width": 200,
      "frame_height": 200,
      "columns": 5,
      "rows": 5,
      "total_frames": 25,
      "animations": {
        "tiny_fish": [
          0,
          1,
          2,
          3
        ],
        "small_fish": [
          4,
          5,
          6,
          7
        ],
        "medium_fish": [
          8,
          9,
          10,
          11
        ],
        "jellyfish": [
          12,
          13
        ],
        "shark": [
          14,
          15,
          16,
          17
        ],
        "pufferfish": [
          18
        ],
        "large_fish": [
          19,
          20,
          21
        ],
        "serpent": [
          22,
          23
        ],
        "treasure": [
          24
        ]
      }
    },
    "three_worlds_pyramid": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/jdc5h7c3_threeworlds%20%281%29.jpg",
      "frame_width": 341,
      "frame_height": 1024,
      "columns": 3,
      "rows": 1,
      "total_frames": 3,
      "animations": {
        "fire_world": [
          0
        ],
        "teal_world": [
          1
        ],
        "void_world": [
          2
        ]
      }
    },
    "aztec_temple_guardians": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/2u8qf3cj_unnamed%20%283%29.jpg",
      "frame_width": 256,
      "frame_height": 256,
      "columns": 4,
      "rows": 4,
      "total_frames": 16,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3
        ],
        "power": [
          4,
          5,
          6,
          7
        ],
        "attack": [
          8,
          9,
          10,
          11
        ],
        "summon": [
          12,
          13,
          14,
          15
        ]
      }
    }
  },
  "background_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/jdc5h7c3_threeworlds%20%281%29.jpg"
};
const ASSET_MANIFEST = [];

(async () => {
  const app = new PIXI.Application({ width: window.innerWidth, height: window.innerHeight, backgroundColor: 0x000a14, antialias: true, resolution: window.devicePixelRatio || 1, autoDensity: true });
  app.view.style.touchAction = 'none';
  document.body.appendChild(app.view);
  document.getElementById('loading').style.display = 'none';
  window.addEventListener('resize', () => app.renderer.resize(window.innerWidth, window.innerHeight));
  const W = () => app.screen.width, H = () => app.screen.height;

  // ═══ SPRITE LOADER (PNG transparent support) ═══
  const SPRITES = GAME_CONFIG.sprites || {};
  const loadedTex = {};
  async function loadSheet(name, cfg) {
    try {
      const img = new Image(); img.crossOrigin = 'anonymous';
      img.src = cfg.sprite_url;
      await new Promise((res, rej) => { img.onload = res; img.onerror = rej; setTimeout(rej, 10000); });
      const bt = PIXI.BaseTexture.from(img);
      const frames = [];
      for (let r = 0; r < cfg.rows; r++)
        for (let c = 0; c < cfg.columns; c++) {
          if (frames.length >= cfg.total_frames) break;
          frames.push(new PIXI.Texture(bt, new PIXI.Rectangle(c * cfg.frame_width, r * cfg.frame_height, cfg.frame_width, cfg.frame_height)));
        }
      const anims = {};
      if (cfg.animations) Object.entries(cfg.animations).forEach(([k, idxs]) => { anims[k] = idxs.map(i => frames[i]).filter(Boolean); });
      loadedTex[name] = { frames, anims, cfg };
    } catch {}
  }
  await Promise.all(Object.entries(SPRITES).map(([n, c]) => loadSheet(n, c)));

  // Fish tier to spritesheet anim mapping
  const TIER_ANIM = { 0:'tiny_fish', 1:'tiny_fish', 2:'small_fish', 3:'small_fish', 4:'medium_fish', 5:'shark', 6:'shark', 7:'large_fish', 8:'large_fish', 9:'shark', 10:'serpent', 11:'serpent' };
  function getFishFrames(tierIdx) {
    const s = loadedTex['aztec_fish_species'];
    return s ? (s.anims[TIER_ANIM[tierIdx] || 'medium_fish'] || null) : null;
  }

  // Canvas fish/boss renderers
  function drawFish(color, sz, tier) {
    const c = document.createElement('canvas'), s = sz * 4; c.width = s * 2.5; c.height = s * 1.8;
    const x = c.getContext('2d'), cx = s * 1.2, cy = s * 0.9, h = '#' + color.toString(16).padStart(6, '0');
    const g = x.createRadialGradient(cx, cy, s * 0.1, cx, cy, s);
    g.addColorStop(0, h); g.addColorStop(0.7, h + 'cc'); g.addColorStop(1, h + '33');
    x.beginPath(); x.moveTo(cx + s, cy);
    x.quadraticCurveTo(cx + s * 0.5, cy - s * 0.7, cx - s * 0.3, cy - s * 0.5);
    x.quadraticCurveTo(cx - s * 0.8, cy - s * 0.3, cx - s, cy);
    x.quadraticCurveTo(cx - s * 0.8, cy + s * 0.3, cx - s * 0.3, cy + s * 0.5);
    x.quadraticCurveTo(cx + s * 0.5, cy + s * 0.7, cx + s, cy);
    x.fillStyle = g; x.fill(); x.strokeStyle = h; x.lineWidth = 1.5; x.stroke();
    x.beginPath(); x.moveTo(cx - s, cy); x.lineTo(cx - s * 1.5, cy - s * 0.45); x.quadraticCurveTo(cx - s * 1.2, cy, cx - s * 1.5, cy + s * 0.45); x.closePath(); x.fillStyle = h + 'aa'; x.fill();
    x.beginPath(); x.moveTo(cx + s * 0.2, cy - s * 0.45); x.quadraticCurveTo(cx, cy - s * 0.9, cx - s * 0.4, cy - s * 0.5); x.fillStyle = h + '88'; x.fill();
    x.beginPath(); x.arc(cx + s * 0.55, cy - s * 0.1, s * 0.14, 0, Math.PI * 2); x.fillStyle = '#fff'; x.fill();
    x.beginPath(); x.arc(cx + s * 0.58, cy - s * 0.1, s * 0.07, 0, Math.PI * 2); x.fillStyle = '#000'; x.fill();
    x.globalAlpha = 0.12; for (let i = 0; i < 5; i++) { x.beginPath(); x.arc(cx + s * (0.3 - i * 0.2), cy, s * 0.25, -Math.PI * 0.5, Math.PI * 0.5); x.strokeStyle = '#fff'; x.lineWidth = 1; x.stroke(); } x.globalAlpha = 1;
    if (tier >= 5) { x.shadowColor = h; x.shadowBlur = 20; x.beginPath(); x.arc(cx, cy, s * 0.8, 0, Math.PI * 2); x.strokeStyle = h + '44'; x.lineWidth = 3; x.stroke(); }
    return PIXI.Texture.from(c);
  }
  function drawBoss(color, sz) {
    const c = document.createElement('canvas'), s = sz * 3; c.width = s * 3; c.height = s * 3;
    const x = c.getContext('2d'), cx = s * 1.5, cy = s * 1.5, h = '#' + color.toString(16).padStart(6, '0');
    const a = x.createRadialGradient(cx, cy, s * 0.2, cx, cy, s * 1.4);
    a.addColorStop(0, h + '22'); a.addColorStop(1, 'transparent'); x.fillStyle = a; x.fillRect(0, 0, c.width, c.height);
    x.beginPath(); x.moveTo(cx + s * 1.2, cy);
    x.bezierCurveTo(cx + s, cy - s * 0.8, cx - s * 0.2, cy - s, cx - s * 0.8, cy - s * 0.4);
    x.bezierCurveTo(cx - s * 1.2, cy - s * 0.1, cx - s * 1.2, cy + s * 0.1, cx - s * 0.8, cy + s * 0.4);
    x.bezierCurveTo(cx - s * 0.2, cy + s, cx + s, cy + s * 0.8, cx + s * 1.2, cy);
    x.fillStyle = h + 'dd'; x.fill(); x.strokeStyle = h; x.lineWidth = 3; x.stroke();
    x.beginPath(); x.moveTo(cx + s * 0.3, cy - s * 0.5); x.lineTo(cx + s * 0.1, cy - s * 0.85); x.lineTo(cx + s * 0.5, cy - s * 0.5); x.fillStyle = '#d4af37'; x.fill();
    x.shadowColor = '#ff0000'; x.shadowBlur = 15;
    x.beginPath(); x.arc(cx + s * 0.4, cy - s * 0.1, s * 0.08, 0, Math.PI * 2); x.fillStyle = '#ff0000'; x.fill();
    x.beginPath(); x.arc(cx + s * 0.4, cy + s * 0.1, s * 0.08, 0, Math.PI * 2); x.fill();
    return PIXI.Texture.from(c);
  }

  // ═══ GAME STATE ═══
  let credits = 10000, betLevel = 1, totalWon = 0, totalShots = 0;
  const BET_LEVELS = [0.01, 0.05, 0.10, 0.25, 0.50, 1.00, 5.00, 10.00];
  let currentWeapon = 0, jackpotPool = 500, frozenUntil = 0, bossActive = false;
  let autoFire = false, lockedTarget = null;

  const WEAPONS = [
    { name: 'CANNON', color: 0xd4af37, cost: 1, damage: 1, speed: 14, bullets: 1, icon: 'C' },
    { name: 'LASER', color: 0x00ffcc, cost: 3, damage: 2, speed: 35, bullets: 1, icon: 'L' },
    { name: 'CHAIN', color: 0x6666ff, cost: 5, damage: 1, speed: 12, bullets: 1, icon: 'Z' },
    { name: 'BOMB', color: 0xff4444, cost: 8, damage: 3, speed: 10, bullets: 1, icon: 'B' },
    { name: 'AUTO', color: 0xffaa00, cost: 2, damage: 1, speed: 16, bullets: 3, icon: 'A' },
    { name: 'RAILGUN', color: 0xff00ff, cost: 15, damage: 8, speed: 45, bullets: 1, icon: 'R' },
  ];

  const FISH = [
    { name: 'Clownfish', tier: 0, color: 0xff6600, hp: 1, val: 2, sz: 16, spd: 1.8, pat: 'sine' },
    { name: 'Angelfish', tier: 0, color: 0x44ccff, hp: 1, val: 3, sz: 18, spd: 1.5, pat: 'sine' },
    { name: 'Pufferfish', tier: 1, color: 0xaacc00, hp: 2, val: 5, sz: 20, spd: 1.2, pat: 'sine' },
    { name: 'Swordfish', tier: 1, color: 0x6699ff, hp: 2, val: 8, sz: 24, spd: 2.5, pat: 'linear' },
    { name: 'Barracuda', tier: 2, color: 0xcc4444, hp: 3, val: 12, sz: 28, spd: 2.0, pat: 'zigzag' },
    { name: 'Manta Ray', tier: 3, color: 0x9966ff, hp: 5, val: 25, sz: 36, spd: 1.0, pat: 'circle' },
    { name: 'Hammerhead', tier: 3, color: 0x888888, hp: 6, val: 35, sz: 40, spd: 1.5, pat: 'zigzag' },
    { name: 'Sea Turtle', tier: 4, color: 0x33cc66, hp: 8, val: 50, sz: 44, spd: 0.6, pat: 'sine' },
    { name: 'Golden Dragon', tier: 5, color: 0xd4af37, hp: 15, val: 100, sz: 52, spd: 0.8, pat: 'circle' },
    { name: 'Mermaid Queen', tier: 5, color: 0xff66cc, hp: 12, val: 80, sz: 48, spd: 1.0, pat: 'sine' },
    { name: 'Aztec Serpent', tier: 6, color: 0x00ff88, hp: 25, val: 200, sz: 58, spd: 0.5, pat: 'circle' },
    { name: 'Sovereign', tier: 7, color: 0xffffff, hp: 50, val: 500, sz: 72, spd: 0.3, pat: 'drift' },
  ];
  const SW = [15,15,12,10,8,6,5,4,4,3,2,1];
  const BOSSES = [
    { name: 'JAGUAR WARRIOR', color: 0xd4af37, hp: 200, val: 1000, sz: 80 },
    { name: 'QUETZALCOATL', color: 0x00ffcc, hp: 300, val: 2000, sz: 90 },
    { name: 'TEZCATLIPOCA', color: 0x9900ff, hp: 500, val: 5000, sz: 100 },
  ];
  const SPECIALS = [
    { name: 'TREASURE', color: 0xd4af37, hp: 10, sz: 32, spd: 0.3, fx: 'burst', min: 50, max: 500 },
    { name: 'BOMB FISH', color: 0xff0000, hp: 5, sz: 28, spd: 1.5, fx: 'explode', rad: 200 },
    { name: 'FREEZE', color: 0x00ccff, hp: 3, sz: 24, spd: 2.0, fx: 'freeze', dur: 3000 },
    { name: 'JACKPOT CRAB', color: 0xff00ff, hp: 20, sz: 36, spd: 0.5, fx: 'jackpot' },
  ];

  // Pre-render textures
  const fishTex = FISH.map((f, i) => drawFish(f.color, f.sz, f.tier));
  const bossTex = BOSSES.map(b => drawBoss(b.color, b.sz));

  // ═══ LAYERS ═══
  const L = {}; ['bg','mid','fish','fx','ui','hud'].forEach(n => { L[n] = new PIXI.Container(); app.stage.addChild(L[n]); });

  // ═══ BACKGROUND ═══
  if (GAME_CONFIG.background_url) {
    try {
      const img = new Image(); img.crossOrigin = 'anonymous'; img.src = GAME_CONFIG.background_url;
      await new Promise((r, e) => { img.onload = r; img.onerror = e; setTimeout(e, 8000); });
      const bgSpr = new PIXI.Sprite(PIXI.Texture.from(img));
      bgSpr.width = W(); bgSpr.height = H(); L.bg.addChild(bgSpr);
    } catch {
      const g = new PIXI.Graphics();
      for (let y = 0; y < H(); y += 2) { const t = y / H(); g.lineStyle(2, (Math.floor(t * 12) << 16) | (Math.floor(16 + t * 16) << 8) | Math.floor(20 + t * 40)); g.moveTo(0, y).lineTo(W(), y); }
      L.bg.addChild(g);
    }
  } else {
    const g = new PIXI.Graphics();
    for (let y = 0; y < H(); y += 2) { const t = y / H(); g.lineStyle(2, (Math.floor(t * 12) << 16) | (Math.floor(16 + t * 16) << 8) | Math.floor(20 + t * 40)); g.moveTo(0, y).lineTo(W(), y); }
    L.bg.addChild(g);
  }

  // Light rays + bubbles
  for (let i = 0; i < 6; i++) { const r = new PIXI.Graphics(); r.beginFill(0x0066aa, 0.025); const x = Math.random() * W(), w = 30 + Math.random() * 60; r.moveTo(x, -20).lineTo(x + w, -20).lineTo(x + w * 0.6 + 40, H() + 20).lineTo(x - 40, H() + 20); r.closePath(); r.endFill(); L.bg.addChild(r); }
  const bubbles = [];
  for (let i = 0; i < 40; i++) { const b = new PIXI.Graphics(); const s = 1 + Math.random() * 4; b.beginFill(0x44aaff, 0.1).drawCircle(0, 0, s).endFill(); b.x = Math.random() * W(); b.y = Math.random() * H(); b.vy = -0.15 - Math.random() * 0.4; b.vx = (Math.random() - 0.5) * 0.1; L.mid.addChild(b); bubbles.push(b); }

  // ═══ ENTITIES ═══
  const fishes = [], bullets = [], particles = [], dmgNums = [];

  // ═══ JACKPOT BANNER (FireKirin style) ═══
  const jpBar = new PIXI.Graphics();
  jpBar.beginFill(0x1a0020, 0.9).drawRoundedRect(W() / 2 - 180, 4, 360, 36, 6).endFill();
  jpBar.lineStyle(2, 0xd4af37, 0.6).drawRoundedRect(W() / 2 - 180, 4, 360, 36, 6);
  L.hud.addChild(jpBar);
  const jpNames = ['MINI', 'MINOR', 'MAJOR', 'GRAND'];
  const jpColors = [0x44ff44, 0x00c8ff, 0xd4af37, 0xff0000];
  const jpPools = [22.96, 103.50, 532.37, 1524.95];
  let jpCycleIdx = 0;
  const jpLabel = new PIXI.Text('MINI', { fontSize: 11, fill: 0x44ff44, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 2 });
  jpLabel.anchor.set(0.5); jpLabel.x = W() / 2 - 60; jpLabel.y = 22; L.hud.addChild(jpLabel);
  const jpAmount = new PIXI.Text('$22.96', { fontSize: 16, fill: 0xffffff, fontFamily: 'monospace', fontWeight: 'bold' });
  jpAmount.anchor.set(0.5); jpAmount.x = W() / 2 + 30; jpAmount.y = 22; L.hud.addChild(jpAmount);
  setInterval(() => { jpCycleIdx = (jpCycleIdx + 1) % 4; jpLabel.text = jpNames[jpCycleIdx]; jpLabel.style.fill = jpColors[jpCycleIdx]; jpAmount.text = '$' + (jpPools[jpCycleIdx] + jackpotPool * [0.01, 0.05, 0.2, 0.74][jpCycleIdx]).toFixed(2); }, 3000);

  // ═══ PLAYER CORNERS (FireKirin style) ═══
  function makeCorner(x, y, align) {
    const bg = new PIXI.Graphics();
    bg.beginFill(0x004400, 0.85).drawRoundedRect(0, 0, 130, 44, 8).endFill();
    bg.lineStyle(1.5, 0x44ff44, 0.5).drawRoundedRect(0, 0, 130, 44, 8);
    bg.x = x; bg.y = y;
    const bal = new PIXI.Text('10,000.00', { fontSize: 15, fill: 0x44ff44, fontFamily: 'monospace', fontWeight: 'bold' });
    bal.anchor.set(align === 'left' ? 0 : 1, 0.5); bal.x = align === 'left' ? 10 : 120; bal.y = 15;
    const id = new PIXI.Text('ID: YOU', { fontSize: 8, fill: 0x44ff44, fontFamily: 'monospace' });
    id.x = align === 'left' ? 10 : 50; id.y = 30;
    bg.addChild(bal); bg.addChild(id);
    L.hud.addChild(bg);
    return bal;
  }
  const myBal = makeCorner(8, 6, 'left');
  makeCorner(W() - 138, 6, 'right');

  // ═══ SIDE MENU BUTTONS (FireKirin style) ═══
  function sideBtn(x, y, label, color, icon, onClick) {
    const cont = new PIXI.Container(); cont.x = x; cont.y = y;
    const bg = new PIXI.Graphics();
    bg.lineStyle(2, color, 0.6); bg.beginFill(color, 0.1).drawCircle(0, 0, 26).endFill();
    cont.addChild(bg);
    const ico = new PIXI.Text(icon, { fontSize: 16, fill: color, fontFamily: 'monospace', fontWeight: 'bold' });
    ico.anchor.set(0.5); cont.addChild(ico);
    const lbl = new PIXI.Text(label, { fontSize: 7, fill: color, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 1 });
    lbl.anchor.set(0.5); lbl.y = 34; cont.addChild(lbl);
    cont.interactive = true; cont.cursor = 'pointer';
    cont.on('pointerdown', onClick);
    L.hud.addChild(cont);
    return cont;
  }

  // Left side
  sideBtn(36, H() / 2 - 80, 'MENU', 0x4488ff, '≡', () => showTutorial());
  sideBtn(36, H() / 2, 'SCREEN', 0xff8844, '⛶', () => { if (document.fullscreenElement) document.exitFullscreen(); else document.body.requestFullscreen(); });
  sideBtn(36, H() / 2 + 80, 'INFO', 0xffcc00, '?', () => showTutorial());

  // Right side
  sideBtn(W() - 36, H() / 2 - 80, 'LASER', 0x00ffcc, '⚡', () => { currentWeapon = 1; updateHUD(); });
  sideBtn(W() - 36, H() / 2, 'LOCKED', 0x9966ff, '◎', () => { lockedTarget = lockedTarget ? null : fishes.find(f => f.alive); });
  sideBtn(W() - 36, H() / 2 + 80, 'AUTO', 0xff4444, '↻', () => { autoFire = !autoFire; });

  // Room navigation arrows
  const mkArrow = (x, dir) => { const a = new PIXI.Text(dir > 0 ? '»' : '«', { fontSize: 32, fill: 0xffffff, fontFamily: 'monospace' }); a.anchor.set(0.5); a.x = x; a.y = H() / 2 - 160; a.alpha = 0.4; a.interactive = true; a.cursor = 'pointer'; a.on('pointerover', () => a.alpha = 0.8); a.on('pointerout', () => a.alpha = 0.4); L.hud.addChild(a); };
  mkArrow(70, -1); mkArrow(W() - 70, 1);

  // ═══ TURRET (Ornate, FireKirin style) ═══
  const turret = new PIXI.Container(); turret.x = W() / 2; turret.y = H() - 50;
  // Base — ornate circular platform
  const tBase = new PIXI.Graphics();
  tBase.beginFill(0x1a1a1a).drawCircle(0, 8, 40).endFill();
  tBase.lineStyle(2, 0xd4af37, 0.6).drawCircle(0, 8, 40);
  tBase.lineStyle(1, 0xd4af37, 0.3).drawCircle(0, 8, 35);
  // Gear details
  for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; tBase.lineStyle(1, 0x444444).moveTo(Math.cos(a) * 32, 8 + Math.sin(a) * 32).lineTo(Math.cos(a) * 40, 8 + Math.sin(a) * 40); }
  turret.addChild(tBase);
  // Barrel
  const tBarrel = new PIXI.Graphics();
  tBarrel.beginFill(0x333333).drawRect(-6, -55, 12, 55).endFill();
  tBarrel.lineStyle(1.5, 0xd4af37).drawRect(-6, -55, 12, 55);
  tBarrel.beginFill(0xd4af37).drawCircle(0, -55, 6).endFill();
  turret.addChild(tBarrel);
  // Bet display on turret
  const betDisp = new PIXI.Text('0.10', { fontSize: 11, fill: 0xd4af37, fontFamily: 'monospace', fontWeight: 'bold' });
  betDisp.anchor.set(0.5); betDisp.y = 8; turret.addChild(betDisp);
  L.hud.addChild(turret);

  // +/- bet buttons
  const mkBetBtn = (x, label, dir) => {
    const b = new PIXI.Graphics(); b.beginFill(dir > 0 ? 0x44aa44 : 0xaa4444, 0.8).drawCircle(0, 0, 16).endFill();
    b.lineStyle(1, dir > 0 ? 0x66ff66 : 0xff6666).drawCircle(0, 0, 16);
    const t = new PIXI.Text(label, { fontSize: 18, fill: 0xffffff, fontFamily: 'monospace', fontWeight: 'bold' });
    t.anchor.set(0.5); b.addChild(t);
    b.x = turret.x + x; b.y = H() - 50; b.interactive = true; b.cursor = 'pointer';
    b.on('pointerdown', () => {
      const i = BET_LEVELS.indexOf(betLevel);
      betLevel = BET_LEVELS[Math.max(0, Math.min(BET_LEVELS.length - 1, i + dir))];
      betDisp.text = betLevel.toFixed(2); updateHUD();
    });
    L.hud.addChild(b);
  };
  mkBetBtn(-70, '−', -1); mkBetBtn(70, '+', 1);

  // Bet value bar
  const betBar = new PIXI.Graphics();
  betBar.beginFill(0x111111, 0.8).drawRoundedRect(W() / 2 - 120, H() - 16, 240, 12, 3).endFill();
  betBar.lineStyle(1, 0x333333).drawRoundedRect(W() / 2 - 120, H() - 16, 240, 12, 3);
  const betFill = new PIXI.Graphics();
  betFill.beginFill(0xd4af37).drawRoundedRect(W() / 2 - 118, H() - 14, 100, 8, 2).endFill();
  L.hud.addChild(betBar); L.hud.addChild(betFill);

  // Crosshair
  const cross = new PIXI.Graphics();
  cross.lineStyle(1, 0xff0000, 0.5).drawCircle(0, 0, 18).moveTo(-22, 0).lineTo(22, 0).moveTo(0, -22).lineTo(0, 22);
  cross.lineStyle(1, 0xd4af37, 0.2).drawCircle(0, 0, 9);
  cross.zIndex = 999; L.hud.addChild(cross);
  app.view.addEventListener('mousemove', e => { cross.x = e.offsetX; cross.y = e.offsetY; tBarrel.rotation = Math.atan2(e.offsetY - turret.y, e.offsetX - turret.x) + Math.PI / 2; });

  // ═══ FISH SPAWNING ═══
  function wRng() { const t = SW.reduce((a, b) => a + b); let r = Math.random() * t; for (let i = 0; i < SW.length; i++) { r -= SW[i]; if (r <= 0) return i; } return 0; }

  function spawnFish(idx) {
    const type = FISH[idx !== undefined ? idx : wRng()]; const ti = FISH.indexOf(type);
    const f = new PIXI.Container();
    // Sprite or canvas
    const frames = getFishFrames(ti);
    if (frames && frames.length > 0) {
      const a = new PIXI.AnimatedSprite(frames); a.anchor.set(0.5); a.animationSpeed = 0.08; a.play(); a.scale.set((type.sz * 2.8) / 200); f.addChild(a); f._a = a;
    } else {
      const s = new PIXI.Sprite(fishTex[ti]); s.anchor.set(0.5); s.scale.set(0.5); f.addChild(s);
    }
    // Coin value label (FireKirin style — shows bet value above fish)
    const coinVal = (type.val * betLevel).toFixed(2);
    const vt = new PIXI.Text(coinVal, { fontSize: 9, fill: type.tier >= 5 ? 0xd4af37 : 0xffffff, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 });
    vt.anchor.set(0.5); vt.y = -type.sz * 0.7 - 5; f.addChild(vt); f._valText = vt;
    // HP bar (tier 2+)
    if (type.tier >= 2) { const bg = new PIXI.Graphics(); bg.beginFill(0x000000, 0.6).drawRoundedRect(-type.sz * 0.6, -type.sz * 0.6, type.sz * 1.2, 3, 1).endFill(); const fl = new PIXI.Graphics(); fl.beginFill(0x44ff44).drawRoundedRect(-type.sz * 0.6, -type.sz * 0.6, type.sz * 1.2, 3, 1).endFill(); f.addChild(bg); f.addChild(fl); f._hf = fl; f._hw = type.sz * 1.2; }

    const left = Math.random() > 0.5;
    f.x = left ? -50 : W() + 50; f.y = 55 + Math.random() * (H() - 160);
    f.vx = (left ? 1 : -1) * type.spd * (0.8 + Math.random() * 0.4); f.vy = (Math.random() - 0.5) * 0.4;
    f.scale.x = left ? 1 : -1;
    f.hp = Math.ceil(type.hp * (1 + betLevel * 0.5)); f.mhp = f.hp; f.val = type.val; f.tier = type.tier; f.sz = type.sz; f.pat = type.pat; f.ph = Math.random() * Math.PI * 2; f.alive = true;
    f.interactive = true; f.cursor = 'crosshair'; f.hitArea = new PIXI.Circle(0, 0, type.sz * 1.3);
    f.on('pointerdown', () => shoot(f));
    L.fish.addChild(f); fishes.push(f);
  }

  function spawnBoss() {
    if (bossActive) return; bossActive = true;
    const type = BOSSES[Math.floor(Math.random() * BOSSES.length)]; const bi = BOSSES.indexOf(type);
    const f = new PIXI.Container();
    const sn = type.name.toLowerCase().replace(/[\s,]+/g, '_');
    if (loadedTex[sn]) { const td = loadedTex[sn]; const a = new PIXI.AnimatedSprite(td.anims.idle || td.frames.slice(0, 4)); a.anchor.set(0.5); a.animationSpeed = 0.08; a.play(); a.scale.set((type.sz * 2.5) / td.cfg.frame_width); f.addChild(a); f._a = a; f._td = td; }
    else { const s = new PIXI.Sprite(bossTex[bi]); s.anchor.set(0.5); s.scale.set(0.5); f.addChild(s); }
    const nm = new PIXI.Text(type.name, { fontSize: 13, fill: type.color, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 2, stroke: 0x000000, strokeThickness: 4 }); nm.anchor.set(0.5); nm.y = -type.sz - 12; f.addChild(nm);
    const hw = type.sz * 2; const bg = new PIXI.Graphics(); bg.beginFill(0x000000, 0.7).drawRoundedRect(-hw / 2, -type.sz - 5, hw, 5, 2).endFill(); const fl = new PIXI.Graphics(); fl.beginFill(0xff0000).drawRoundedRect(-hw / 2, -type.sz - 5, hw, 5, 2).endFill(); f.addChild(bg); f.addChild(fl); f._hf = fl; f._hw = hw;
    const mt = new PIXI.Text(`x${type.val}`, { fontSize: 15, fill: 0xd4af37, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 4 }); mt.anchor.set(0.5); mt.y = type.sz + 10; f.addChild(mt);
    f.x = W() + 120; f.y = H() / 2; f.vx = -0.3; f.vy = 0; f.hp = Math.ceil(type.hp * (1 + betLevel * 0.5)); f.mhp = f.hp; f.val = type.val; f.tier = 99; f.sz = type.sz; f.isBoss = true; f.pat = 'boss'; f.ph = 0; f.alive = true;
    f.interactive = true; f.cursor = 'crosshair'; f.hitArea = new PIXI.Circle(0, 0, type.sz * 1.5);
    f.on('pointerdown', () => shoot(f));
    L.fish.addChild(f); fishes.push(f);
    announce(`BOSS: ${type.name}`, type.color);
  }

  function spawnSpecial() {
    const type = SPECIALS[Math.floor(Math.random() * SPECIALS.length)];
    const f = new PIXI.Container();
    const gfx = new PIXI.Graphics(); gfx.lineStyle(2, type.color, 0.8); gfx.beginFill(type.color, 0.2).drawRoundedRect(-type.sz, -type.sz * 0.6, type.sz * 2, type.sz * 1.2, 8).endFill();
    f.addChild(gfx);
    const lbl = new PIXI.Text(type.name, { fontSize: 8, fill: type.color, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 }); lbl.anchor.set(0.5); f.addChild(lbl);
    f.x = Math.random() > 0.5 ? -40 : W() + 40; f.y = 80 + Math.random() * (H() - 200);
    f.vx = (f.x < 0 ? 1 : -1) * type.spd; f.vy = (Math.random() - 0.5) * 0.3;
    f.hp = type.hp; f.mhp = type.hp; f.val = 0; f.tier = 10; f.sz = type.sz; f.alive = true; f.sfx = type.fx; f.sfxP = type; f.pat = 'linear'; f.ph = 0;
    f.interactive = true; f.cursor = 'crosshair'; f.hitArea = new PIXI.Circle(0, 0, type.sz * 1.5); f.on('pointerdown', () => shoot(f));
    L.fish.addChild(f); fishes.push(f);
  }

  // ═══ SHOOTING ═══
  function shoot(target) {
    const w = WEAPONS[currentWeapon], cost = w.cost * betLevel;
    if (credits < cost) return;
    credits -= cost; totalShots++; jackpotPool += cost * 0.02;
    for (let b = 0; b < w.bullets; b++) {
      const angle = Math.atan2(target.y - turret.y, target.x - turret.x) + (b - (w.bullets - 1) / 2) * 0.08;
      const bul = new PIXI.Graphics(); bul.beginFill(w.color).drawCircle(0, 0, 3 + betLevel * 0.2).endFill(); bul.beginFill(w.color, 0.2).drawCircle(0, 0, 7).endFill();
      if (w.name === 'LASER') { bul.beginFill(w.color, 0.12).drawRect(-3, -H(), 6, H()).endFill(); }
      bul.x = turret.x; bul.y = turret.y - 50; bul.vx = Math.cos(angle) * w.speed; bul.vy = Math.sin(angle) * w.speed;
      bul.dmg = w.damage * betLevel; bul.wt = w.name; bul.alive = true;
      L.fx.addChild(bul); bullets.push(bul);
    }
    updateHUD();
  }

  function hit(fish, bul) {
    if (!fish.alive) return;
    fish.hp -= bul.dmg;
    if (fish._hf) { fish._hf.clear(); const p = Math.max(0, fish.hp / fish.mhp); fish._hf.beginFill(p > 0.5 ? 0x44ff44 : p > 0.25 ? 0xffaa00 : 0xff0000).drawRoundedRect(-fish._hw / 2, fish.isBoss ? -fish.sz - 5 : -fish.sz * 0.6, fish._hw * p, fish.isBoss ? 5 : 3, 1).endFill(); }
    dmg(fish.x, fish.y - fish.sz, bul.dmg, 0xffffff);
    fish.alpha = 0.4; setTimeout(() => { if (fish.alive) fish.alpha = 1; }, 80);
    if (fish.hp <= 0) kill(fish);
    if (bul.wt === 'CHAIN') fishes.filter(f => f.alive && f !== fish).sort((a, b) => Math.hypot(a.x - fish.x, a.y - fish.y) - Math.hypot(b.x - fish.x, b.y - fish.y)).slice(0, 3).forEach(f => { f.hp -= bul.dmg * 0.5; if (f.hp <= 0) kill(f); const ln = new PIXI.Graphics(); ln.lineStyle(2, 0x6666ff, 0.8).moveTo(fish.x, fish.y).lineTo(f.x, f.y); ln.life = 12; L.fx.addChild(ln); particles.push(ln); });
    if (bul.wt === 'BOMB') { const ex = new PIXI.Graphics(); ex.beginFill(0xff4444, 0.15).drawCircle(0, 0, 120).endFill(); ex.lineStyle(2, 0xff4444, 0.3).drawCircle(0, 0, 120); ex.x = fish.x; ex.y = fish.y; ex.life = 18; L.fx.addChild(ex); particles.push(ex); fishes.filter(f => f.alive && f !== fish && Math.hypot(f.x - fish.x, f.y - fish.y) < 120).forEach(f => { f.hp -= bul.dmg; if (f.hp <= 0) kill(f); }); }
  }

  function kill(fish) {
    fish.alive = false; const win = fish.val * betLevel; credits += win; totalWon += win;
    if (fish.sfx === 'burst') { const b = fish.sfxP.min + Math.floor(Math.random() * (fish.sfxP.max - fish.sfxP.min)); credits += b; announce(`TREASURE! +$${b.toFixed(2)}`, 0xd4af37); }
    else if (fish.sfx === 'explode') { fishes.filter(f => f.alive && Math.hypot(f.x - fish.x, f.y - fish.y) < 200).forEach(f => { f.hp = 0; kill(f); }); announce('BOMB!', 0xff0000); }
    else if (fish.sfx === 'freeze') { frozenUntil = Date.now() + 3000; announce('FREEZE!', 0x00ccff); }
    else if (fish.sfx === 'jackpot') { const jp = Math.floor(jackpotPool); credits += jp; jackpotPool = 100; announce(`JACKPOT! +$${jp.toFixed(2)}`, 0xff00ff); }
    if (fish.isBoss) { bossActive = false; announce(`BOSS KILLED! +$${win.toFixed(2)}`, 0xd4af37); }
    // Coin scatter particles
    for (let p = 0; p < (fish.tier >= 5 ? 20 : 8); p++) {
      const pt = new PIXI.Graphics(); pt.beginFill(fish.tier >= 5 ? 0xd4af37 : 0xffd700).drawCircle(0, 0, 2 + Math.random() * 3).endFill();
      pt.x = fish.x; pt.y = fish.y; pt.vx = (Math.random() - 0.5) * 8; pt.vy = (Math.random() - 0.5) * 8; pt.life = 30; L.fx.addChild(pt); particles.push(pt);
    }
    dmg(fish.x, fish.y - fish.sz - 12, `+$${win.toFixed(2)}`, 0x44ff44);
    setTimeout(() => { fish.visible = false; }, 150);
    updateHUD();
  }

  function dmg(x, y, text, color) { const t = new PIXI.Text(String(text), { fontSize: String(text).startsWith('+') ? 15 : 10, fill: color, fontFamily: 'monospace', fontWeight: 'bold', stroke: 0x000000, strokeThickness: 3 }); t.anchor.set(0.5); t.x = x; t.y = y; t.vy = -1.5; t.life = 50; L.ui.addChild(t); dmgNums.push(t); }
  function announce(text, color) { const t = new PIXI.Text(text, { fontSize: 28, fill: color, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 4, stroke: 0x000000, strokeThickness: 5 }); t.anchor.set(0.5); t.x = W() / 2; t.y = H() / 2 - 40; t.life = 100; L.ui.addChild(t); dmgNums.push(t); }

  // ═══ TUTORIAL MODAL ═══
  let tutorialOpen = false;
  function showTutorial() {
    if (tutorialOpen) return; tutorialOpen = true;
    const overlay = new PIXI.Graphics(); overlay.beginFill(0x000000, 0.7).drawRect(0, 0, W(), H()).endFill(); overlay.interactive = true;
    const box = new PIXI.Graphics(); box.beginFill(0x002222, 0.95).drawRoundedRect(W() / 2 - 300, H() / 2 - 200, 600, 400, 12).endFill();
    box.lineStyle(2, 0x00ccaa).drawRoundedRect(W() / 2 - 300, H() / 2 - 200, 600, 400, 12);
    const title = new PIXI.Text('GAME INTRODUCTION', { fontSize: 18, fill: 0x00ccaa, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 3 }); title.anchor.set(0.5); title.x = W() / 2; title.y = H() / 2 - 170;
    const body = new PIXI.Text('Click fish to shoot. Higher tier = more HP = more reward.\n\nWeapons: [1] Cannon [2] Laser [3] Chain [4] Bomb [5] Auto [6] Railgun\n\nQ/E to change bet. Bosses spawn every 45s.\n\nSpecial fish: Treasure (credit burst), Bomb (AOE kill),\nFreeze (stun all), Jackpot Crab (wins pool).\n\nLASER: Side button — piercing beam\nLOCKED: Auto-target nearest fish\nAUTO: Hold-to-fire mode', { fontSize: 11, fill: 0xcccccc, fontFamily: 'monospace', wordWrap: true, wordWrapWidth: 520 }); body.x = W() / 2 - 270; body.y = H() / 2 - 130;
    const close = new PIXI.Text('✕', { fontSize: 24, fill: 0xff4444, fontFamily: 'monospace' }); close.anchor.set(0.5); close.x = W() / 2 + 270; close.y = H() / 2 - 175; close.interactive = true; close.cursor = 'pointer';
    close.on('pointerdown', () => { L.ui.removeChild(overlay); L.ui.removeChild(box); L.ui.removeChild(title); L.ui.removeChild(body); L.ui.removeChild(close); tutorialOpen = false; });
    L.ui.addChild(overlay); L.ui.addChild(box); L.ui.addChild(title); L.ui.addChild(body); L.ui.addChild(close);
  }

  function updateHUD() {
    myBal.text = credits.toFixed(2);
    betDisp.text = betLevel.toFixed(2);
    betFill.clear(); betFill.beginFill(0xd4af37).drawRoundedRect(W() / 2 - 118, H() - 14, Math.min(236, (BET_LEVELS.indexOf(betLevel) / (BET_LEVELS.length - 1)) * 236), 8, 2).endFill();
    document.getElementById('score').textContent = credits.toFixed(2);
  }
  updateHUD();

  document.addEventListener('keydown', e => {
    const n = parseInt(e.key); if (n >= 1 && n <= 6) { currentWeapon = n - 1; }
    if (e.key === 'q') { const i = BET_LEVELS.indexOf(betLevel); betLevel = BET_LEVELS[Math.max(0, i - 1)]; betDisp.text = betLevel.toFixed(2); updateHUD(); }
    if (e.key === 'e') { const i = BET_LEVELS.indexOf(betLevel); betLevel = BET_LEVELS[Math.min(BET_LEVELS.length - 1, i + 1)]; betDisp.text = betLevel.toFixed(2); updateHUD(); }
  });

  // ═══ SPAWN TIMERS ═══
  for (let i = 0; i < 15; i++) spawnFish();
  setInterval(() => { if (fishes.filter(f => f.alive).length < 20) spawnFish(); }, 1500);
  setInterval(spawnSpecial, 18000);
  setTimeout(spawnBoss, 20000);
  setInterval(() => { if (!bossActive) spawnBoss(); }, 45000);

  // ═══ GAME LOOP ═══
  app.ticker.add(() => {
    const now = Date.now(), frozen = now < frozenUntil;
    fishes.forEach(f => {
      if (!f.alive) return;
      if (frozen && !f.isBoss) { f.alpha = 0.5 + Math.sin(now / 200) * 0.2; return; } f.alpha = 1;
      const t = now / 1000 + f.ph;
      if (f.pat === 'sine') { f.x += f.vx; f.y += Math.sin(t * 2) * 1.5; }
      else if (f.pat === 'zigzag') { f.x += f.vx; f.y += Math.sin(t * 4) * 2.5; }
      else if (f.pat === 'circle') { f.x += f.vx; f.y += Math.cos(t * 1.5) * 2; }
      else if (f.pat === 'drift') { f.x += f.vx * 0.5; f.y += Math.sin(t * 0.5) * 0.8; }
      else if (f.pat === 'boss') { if (f.x > W() * 0.7) f.vx = -0.4; else if (f.x < W() * 0.3) f.vx = 0.4; f.x += f.vx; f.y = H() / 2 + Math.sin(t) * H() * 0.25; }
      else { f.x += f.vx; f.y += f.vy; }
      if (f.y < 45) f.vy = Math.abs(f.vy || 0.5); if (f.y > H() - 80) f.vy = -Math.abs(f.vy || 0.5);
      if (!f.isBoss && (f.x < -100 || f.x > W() + 100)) { f.alive = false; f.visible = false; }
      // Update value label
      if (f._valText) f._valText.text = (f.val * betLevel).toFixed(2);
    });
    for (let i = fishes.length - 1; i >= 0; i--) if (!fishes[i].alive && !fishes[i].visible) { L.fish.removeChild(fishes[i]); fishes.splice(i, 1); }
    bullets.forEach(b => { if (!b.alive) return; b.x += b.vx; b.y += b.vy; if (b.x < -20 || b.x > W() + 20 || b.y < -20 || b.y > H() + 20) { b.alive = false; b.visible = false; return; } fishes.forEach(f => { if (f.alive && b.alive && Math.hypot(f.x - b.x, f.y - b.y) < f.sz * 1.2) { hit(f, b); if (b.wt !== 'LASER') { b.alive = false; b.visible = false; } } }); });
    for (let i = bullets.length - 1; i >= 0; i--) if (!bullets[i].alive) { L.fx.removeChild(bullets[i]); bullets.splice(i, 1); }
    for (let i = particles.length - 1; i >= 0; i--) { const p = particles[i]; if (p.vx !== undefined) { p.x += p.vx; p.y += p.vy; } p.life--; p.alpha = Math.max(0, p.life / 25); if (p.life <= 0) { L.fx.removeChild(p); particles.splice(i, 1); } }
    for (let i = dmgNums.length - 1; i >= 0; i--) { const d = dmgNums[i]; d.y += d.vy || -1; d.life--; d.alpha = Math.max(0, d.life / 50); if (d.life <= 0) { L.ui.removeChild(d); dmgNums.splice(i, 1); } }
    bubbles.forEach(b => { b.x += b.vx + Math.sin(now / 1000) * 0.05; b.y += b.vy; if (b.y < -10) { b.y = H() + 10; b.x = Math.random() * W(); } });
    // Auto-fire
    if (autoFire && fishes.length > 0) { const closest = fishes.filter(f => f.alive).sort((a, b) => Math.hypot(a.x - turret.x, a.y - turret.y) - Math.hypot(b.x - turret.x, b.y - turret.y))[0]; if (closest && Math.random() < 0.1) shoot(closest); }
  });
})();
