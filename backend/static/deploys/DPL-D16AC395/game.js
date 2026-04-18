// SLA113 Video Slots v2 — Gold Rush Slots
// Production Visual Layer
const GAME_CONFIG = {
  "type": "slot_machine",
  "name": "Gold Rush Slots",
  "version": "1.0.0",
  "built_by": "SLA113",
  "sprites": {
    "g-wolf": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/kfmzgzqn_spritesheet1.png",
      "frame_width": 410,
      "frame_height": 512,
      "columns": 5,
      "rows": 4,
      "total_frames": 19,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3,
          4
        ],
        "walk": [
          5,
          6,
          7,
          8,
          9
        ],
        "run": [
          10,
          11,
          12,
          13
        ],
        "ultra": [
          14
        ],
        "hit": [
          15
        ],
        "die": [
          16,
          17,
          18
        ]
      }
    },
    "aztec_fish_species_v2": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/594ce0tv_image.png",
      "frame_width": 512,
      "frame_height": 512,
      "columns": 4,
      "rows": 4,
      "total_frames": 15,
      "animations": {
        "gold_pair": [
          0
        ],
        "blue_school": [
          1,
          2,
          3
        ],
        "gold_school": [
          4
        ],
        "blue_school_dense": [
          5
        ],
        "gold_school_dense": [
          6
        ],
        "silver_school": [
          7
        ],
        "cyan_serpent": [
          8
        ],
        "cursed_black": [
          9
        ],
        "cursed_school": [
          10,
          11
        ],
        "cyan_serpent_alt": [
          12
        ],
        "treasure_fish": [
          13
        ],
        "golden_puffer": [
          14
        ]
      }
    },
    "jaguar_warrior_champion": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/zvo9csfi_image.jpeg",
      "frame_width": 400,
      "frame_height": 400,
      "columns": 4,
      "rows": 5,
      "total_frames": 19,
      "animations": {
        "idle": [
          0
        ],
        "walk": [
          4
        ],
        "attack": [
          5,
          8,
          9
        ],
        "ground_slam": [
          6
        ],
        "swing": [
          3,
          7
        ],
        "hurt": [
          12
        ],
        "ultra": [
          15
        ],
        "death": [
          16,
          17,
          18
        ]
      }
    },
    "jaguar_warrior_elite": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/m8pbtswb_image.jpeg",
      "frame_width": 320,
      "frame_height": 400,
      "columns": 5,
      "rows": 5,
      "total_frames": 23,
      "animations": {
        "idle": [
          0,
          1
        ],
        "walk": [
          5,
          6
        ],
        "attack": [
          6,
          7,
          11,
          12
        ],
        "ground_slam": [
          8,
          13
        ],
        "swing": [
          9
        ],
        "hurt": [
          15
        ],
        "ultra": [
          17
        ],
        "death": [
          19,
          20,
          21
        ]
      }
    },
    "wolf_xolotl_pack": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/pbmyew6l_image.png",
      "frame_width": 400,
      "frame_height": 340,
      "columns": 5,
      "rows": 6,
      "total_frames": 28,
      "animations": {
        "idle": [
          0,
          1,
          2,
          3,
          4
        ],
        "stand": [
          5,
          6,
          7,
          8,
          9
        ],
        "walk": [
          10,
          11,
          12,
          13
        ],
        "howl": [
          12
        ],
        "run": [
          15,
          16,
          17,
          18
        ],
        "turn": [
          20,
          21,
          22,
          23
        ],
        "die": [
          25,
          26,
          27
        ]
      }
    },
    "wolf_xolotls_arena": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/zfvily4d_image.png",
      "frame_width": 2048,
      "frame_height": 2048,
      "columns": 1,
      "rows": 1,
      "total_frames": 1,
      "animations": {
        "idle": [
          0
        ]
      }
    },
    "aztec_wolf_male": {
      "sprite_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/z1ncb721_boss%20%281%29.jpg",
      "frame_width": 1024,
      "frame_height": 1024,
      "columns": 1,
      "rows": 1,
      "total_frames": 1,
      "animations": {
        "idle": [
          0
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
    }
  },
  "background_url": "/api/sla113/sprites/proxy?url=https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/zfvily4d_image.png"
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

  // ═══ JUWA-TIER LAYOUT ═══
  const LOB=GAME_CONFIG.lobby||{};
  const THEME=parseInt((LOB.theme_color||'#d4af37').replace('#',''),16)||0xd4af37;
  const isMobile=/Mobi|Android|iPhone|iPad|iPod|Tablet/i.test(navigator.userAgent)||('ontouchstart' in window);
  const scale=isMobile?Math.min(W()/640,1):1;
  const SW = Math.floor(88*scale), SH = Math.floor(84*scale), machW = REELS * SW + 34, machH = ROWS * SH + 24;
  const mx = W() / 2 - machW / 2, my = H() / 2 - machH / 2 - 10;

  // ═══ AUDIO ═══
  let AC=null,masterGain=null;
  function audio(){if(!AC){try{AC=new(window.AudioContext||window.webkitAudioContext)();masterGain=AC.createGain();masterGain.gain.value=window.__sla_volume||0.7;masterGain.connect(AC.destination);window.__sla_master_gain=masterGain;}catch(_){}}return AC;}
  function sfx(freq,dur,type='square',vol=0.15){const ac=audio();if(!ac)return;const t=ac.currentTime;const o=ac.createOscillator();o.type=type;o.frequency.setValueAtTime(freq,t);const g=ac.createGain();g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(vol,t+0.01);g.gain.exponentialRampToValueAtTime(0.001,t+dur);o.connect(g).connect(masterGain);o.start(t);o.stop(t+dur);}
  function sfxWin(){[523,659,784,1046].forEach((f,i)=>setTimeout(()=>sfx(f,0.3,'triangle',0.18),i*90));}
  function sfxJp(){for(let i=0;i<8;i++)setTimeout(()=>sfx(800+i*120,0.25,'square',0.2),i*60);}
  ['click','keydown','touchstart','pointerdown'].forEach(ev=>document.addEventListener(ev,()=>{const a=audio();if(a&&a.state==='suspended')a.resume();},{once:true}));

  // ═══ METALLIC CABINET (canvas-drawn 3D brushed metal frame) ═══
  function drawMetalFrame(){
    const c=document.createElement('canvas');c.width=machW+80;c.height=machH+240;const x=c.getContext('2d');
    // Outer bevel
    const og=x.createLinearGradient(0,0,0,c.height);og.addColorStop(0,'#4a3818');og.addColorStop(0.5,'#2a1a08');og.addColorStop(1,'#1a0e04');
    x.fillStyle=og;x.fillRect(0,0,c.width,c.height);
    // Inner panel
    const ig=x.createLinearGradient(0,0,0,c.height);ig.addColorStop(0,'#18100a');ig.addColorStop(0.5,'#0a0508');ig.addColorStop(1,'#140a0e');
    x.fillStyle=ig;x.fillRect(18,18,c.width-36,c.height-36);
    // Gold piping
    x.strokeStyle='#d4af37';x.lineWidth=2;x.strokeRect(12,12,c.width-24,c.height-24);
    x.strokeStyle='#d4af3755';x.lineWidth=1;x.strokeRect(22,22,c.width-44,c.height-44);
    // Rivets
    for(let i=0;i<12;i++){const px=30+i*(c.width-60)/11;[20,c.height-20].forEach(py=>{const rg=x.createRadialGradient(px,py,1,px,py,5);rg.addColorStop(0,'#ffd966');rg.addColorStop(1,'#4a3818');x.fillStyle=rg;x.beginPath();x.arc(px,py,4,0,Math.PI*2);x.fill();});}
    // Brushed metal noise
    x.globalAlpha=0.04;for(let i=0;i<2000;i++){x.fillStyle=Math.random()<0.5?'#fff':'#000';x.fillRect(Math.random()*c.width,Math.random()*c.height,1,1);}x.globalAlpha=1;
    return PIXI.Texture.from(c);
  }
  const cab=new PIXI.Sprite(drawMetalFrame());cab.x=mx-40;cab.y=my-80;app.stage.addChild(cab);

  // Title plate
  const title = new PIXI.Text(GAME_CONFIG.name || 'SOVEREIGN SLOTS', { fontSize: Math.floor(20*scale), fill: THEME, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 5, stroke: 0x000000, strokeThickness: 3, dropShadow:true, dropShadowColor:THEME, dropShadowBlur:12, dropShadowAlpha:0.7, dropShadowDistance:0 });
  title.anchor.set(0.5); title.x = W() / 2; title.y = my - 52; app.stage.addChild(title);

  // 4 Jackpot tiers with live amounts
  const jpTexts = {};
  Object.entries(JP).forEach(([name, jp], i) => {
    const x = mx + i * (machW / 4) + machW / 8;
    const bgC=document.createElement('canvas');bgC.width=110;bgC.height=28;const bx=bgC.getContext('2d');
    const bg2=bx.createLinearGradient(0,0,0,28);bg2.addColorStop(0,'#1a0a1a');bg2.addColorStop(1,'#000');bx.fillStyle=bg2;bx.fillRect(0,0,110,28);
    bx.strokeStyle='#'+jp.color.toString(16).padStart(6,'0');bx.lineWidth=1.5;bx.strokeRect(1,1,108,26);
    bx.shadowColor=bx.strokeStyle;bx.shadowBlur=8;bx.strokeRect(1,1,108,26);
    const bgS=new PIXI.Sprite(PIXI.Texture.from(bgC));bgS.x=x-55;bgS.y=my-68;app.stage.addChild(bgS);
    const txt = new PIXI.Text(`${name}\n${jp.pool.toLocaleString()}`, { fontSize: 9, fill: jp.color, fontFamily: 'monospace', fontWeight: 'bold', align:'center', letterSpacing:1 });
    txt.anchor.set(0.5); txt.x = x; txt.y = my - 54; app.stage.addChild(txt); jpTexts[name] = txt;
  });

  // Reel window
  const reelBg = new PIXI.Graphics(); reelBg.beginFill(0x050008).drawRect(mx, my, machW, machH).endFill();
  reelBg.lineStyle(2,THEME,0.6).drawRect(mx,my,machW,machH);
  app.stage.addChild(reelBg);

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

  // ═══ GLOWING SPIN BUTTON + TOUCH CONTROLS ═══
  const btnY = my + machH + 40;

  function drawSpinButton(glow){
    const c=document.createElement('canvas');c.width=180;c.height=56;const x=c.getContext('2d');
    const g=x.createRadialGradient(90,28,4,90,28,90);g.addColorStop(0,'#ffd966');g.addColorStop(0.4,'#d4af37');g.addColorStop(1,'#8a6a1e');
    x.fillStyle=g;x.beginPath();x.roundRect(4,4,172,48,8);x.fill();
    x.shadowColor=glow?'#ffd966':'#d4af37';x.shadowBlur=glow?22:10;x.strokeStyle='#ffd966';x.lineWidth=2;x.beginPath();x.roundRect(4,4,172,48,8);x.stroke();
    x.shadowBlur=0;x.fillStyle='#000';x.font='bold 22px monospace';x.textAlign='center';x.textBaseline='middle';x.letterSpacing='6px';x.fillText('SPIN',90,28);
    return PIXI.Texture.from(c);
  }
  const spinTex=[drawSpinButton(false),drawSpinButton(true)];
  const spinBtn={b:new PIXI.Sprite(spinTex[0])};spinBtn.b.anchor.set(0.5);spinBtn.b.x=W()/2;spinBtn.b.y=btnY+20;spinBtn.b.interactive=true;spinBtn.b.cursor='pointer';spinBtn.b.on('pointerdown',()=>spin());app.stage.addChild(spinBtn.b);
  // pulse glow while idle
  let _pt=0;app.ticker.add(d=>{_pt+=d;if(!spinning){spinBtn.b.scale.set(1+Math.sin(_pt*0.08)*0.03);spinBtn.b.texture=Math.floor(_pt*0.1)%2?spinTex[1]:spinTex[0];}else{spinBtn.b.scale.set(0.95);spinBtn.b.texture=spinTex[1];}});

  function mkBtn(label, x, w, color, cb) {
    const b = new PIXI.Graphics();
    b.beginFill(color,0.9).drawRoundedRect(0, 0, w, 40, 6).endFill();
    b.lineStyle(1.5,THEME,0.6).drawRoundedRect(0, 0, w, 40, 6);
    const t = new PIXI.Text(label, { fontSize: 13, fill: 0xffffff, fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 2 });
    t.anchor.set(0.5); t.x = w / 2; t.y = 20; b.addChild(t); b.x = x; b.y = btnY;
    b.interactive = true; b.cursor = 'pointer'; b.on('pointerdown', cb); app.stage.addChild(b); return { b, t };
  }
  const betBtn = mkBtn(`BET: ${bet}`, W() / 2 - 210, 90, 0x222, () => { if (!spinning) { const bs = [1,5,10,25,50,100]; bet = bs[(bs.indexOf(bet) + 1) % bs.length]; betBtn.t.text = `BET: ${bet}`; updateHUD(); sfx(440,0.08); }});
  const lineBtn = mkBtn(`${lines}L`, W() / 2 + 120, 70, 0x222, () => { if (!spinning) { const ls = [1,5,9,15,20]; lines = ls[(ls.indexOf(lines) + 1) % ls.length]; lineBtn.t.text = `${lines}L`; updateHUD(); sfx(523,0.08); }});

  // Touch tap-to-spin anywhere on reel area
  reelBg.interactive=true;reelBg.cursor='pointer';reelBg.on('pointerdown',()=>spin());

  // ═══ BONUS WHEEL (animated, hidden until triggered) ═══
  const bwCont=new PIXI.Container();bwCont.x=W()/2;bwCont.y=H()/2;bwCont.visible=false;bwCont.zIndex=800;app.stage.addChild(bwCont);
  function drawBonusWheel(){
    const c=document.createElement('canvas');c.width=440;c.height=440;const x=c.getContext('2d');
    const slices=['x2','x5','x10','x25','x50','JP','x3','x8'],colors=['#d4af37','#ff4444','#00c8ff','#44ff44','#ffaa00','#ff00ff','#9944ff','#00ffcc'];
    x.translate(220,220);for(let i=0;i<slices.length;i++){const a0=i*Math.PI*2/slices.length,a1=(i+1)*Math.PI*2/slices.length;x.fillStyle=colors[i];x.beginPath();x.moveTo(0,0);x.arc(0,0,200,a0,a1);x.closePath();x.fill();x.strokeStyle='#fff';x.lineWidth=2;x.stroke();x.save();x.rotate(a0+(a1-a0)/2);x.fillStyle='#000';x.font='bold 26px monospace';x.textAlign='center';x.textBaseline='middle';x.fillText(slices[i],130,0);x.restore();}
    // Center hub
    x.fillStyle='#1a0a1a';x.beginPath();x.arc(0,0,35,0,Math.PI*2);x.fill();x.strokeStyle='#ffd966';x.lineWidth=3;x.stroke();
    return {tex:PIXI.Texture.from(c),slices};
  }
  const _bw=drawBonusWheel();
  const bwSprite=new PIXI.Sprite(_bw.tex);bwSprite.anchor.set(0.5);bwCont.addChild(bwSprite);
  const bwPointer=new PIXI.Graphics();bwPointer.beginFill(0xffd966).moveTo(0,-230).lineTo(-14,-200).lineTo(14,-200).closePath().endFill();bwCont.addChild(bwPointer);
  const bwTitle=new PIXI.Text('BONUS WHEEL',{fontSize:22,fill:0xffd966,fontFamily:'monospace',fontWeight:'bold',letterSpacing:6,stroke:0x000,strokeThickness:4});bwTitle.anchor.set(0.5);bwTitle.y=-270;bwCont.addChild(bwTitle);
  async function spinBonusWheel(){
    return new Promise(res=>{
      bwCont.visible=true;bwSprite.rotation=0;
      const slots=_bw.slices.length,winSlot=Math.floor(Math.random()*slots);
      const winAngle=-(winSlot*Math.PI*2/slots+Math.PI*2/slots/2)+Math.PI*2*6;
      let el=0;const dur=3200;
      const tk=d=>{el+=app.ticker.deltaMS;const p=Math.min(el/dur,1);const ease=1-Math.pow(1-p,3);bwSprite.rotation=ease*winAngle;if(p>=1){app.ticker.remove(tk);sfxJp();setTimeout(()=>{bwCont.visible=false;res(_bw.slices[winSlot]);},900);}};
      app.ticker.add(tk);
    });
  }

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
      if(frame%3===0)sfx(220+frame*8,0.05,'square',0.06);
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
        if (bn >= 3) { const bpr=await spinBonusWheel(); const prizes={'x2':2,'x3':3,'x5':5,'x8':8,'x10':10,'x25':25,'x50':50,'JP':100}; totalPay += (prizes[bpr]||10) * bet * lines; winText.text = `BONUS ${bpr}!`; animateWin(); }
        if (co >= 6) { let coinVal = 0; for (let r = 0; r < REELS; r++) for (let row = 0; row < ROWS; row++) if (ALL[grid[r][row]].special === 'coin') coinVal += [10,25,50,100,250][Math.floor(Math.random()*5)] * bet; totalPay += coinVal; winText.text = 'HOLD & SPIN!'; sfxJp(); await delay(1000); }
        // Jackpot
        Object.entries(JP).forEach(([n, j]) => { if (Math.random() < (n === 'GRAND' ? 0.0001 : n === 'MAJOR' ? 0.001 : n === 'MINOR' ? 0.005 : 0.02) * cascadeCount) { totalPay += Math.floor(j.pool); winText.text = `${n} JACKPOT! +${Math.floor(j.pool).toLocaleString()}`; j.pool *= 0.1; sfxJp(); animateWin(); } });
        if (wins.length > 0) { wins.forEach(pos => { const [r, row] = pos.split('-').map(Number); grid[r][row] = -1; });
          await delay(300);
          for (let r = 0; r < REELS; r++) { const col = grid[r].filter(s => s !== -1); while (col.length < ROWS) col.unshift(rng()); grid[r] = col; }
          renderGrid(); await delay(200);
        } else { cascading = false; }
      } else { cascading = false; }
    }
    if (totalPay > 0) { credits += totalPay; totalWins += totalPay; winText.text = `WIN: ${totalPay.toLocaleString()}${cascadeCount > 1 ? ` (x${cascadeCount} CASCADE)` : ''}`; winText.style.fill = totalPay >= bet * lines * 20 ? 0xff0000 : totalPay >= bet * lines * 5 ? 0xd4af37 : 0x44ff44; animateWin(); sfxWin(); }
    updateHUD(); spinning = false;
  }

  function animateWin(){
    winText.scale.set(0.1);winText.alpha=0;let t=0;const tk=d=>{t+=app.ticker.deltaMS;const p=Math.min(t/500,1);const ease=1-Math.pow(1-p,3);winText.scale.set(0.1+ease*1.15);winText.alpha=ease;if(p>=1){winText.scale.set(1.15);app.ticker.remove(tk);}};app.ticker.add(tk);
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
  // Swipe down to spin
  let _ty=null;document.addEventListener('touchstart',e=>{_ty=e.touches[0].clientY;},{passive:true});
  document.addEventListener('touchend',e=>{if(_ty!==null&&e.changedTouches[0]){const dy=e.changedTouches[0].clientY-_ty;if(dy>80)spin();_ty=null;}},{passive:true});
  // Resize
  window.addEventListener('resize',()=>{app.renderer.resize(window.innerWidth,window.innerHeight);});
  renderGrid(); updateHUD();
})();
