import React, { useEffect, useRef, useState } from "react";

const GAME = {
  width: 1280,
  height: 720,
  shotCost: 1,
  comboWindow: 3000,
  bossWave: 10,
};

const CREATURES = [
  { id: "delta_minnow", name: "Delta Minnow", hp: 1, value: 1, speed: 125, radius: 16, tier: 1, glyph: "◇" },
  { id: "sunscale", name: "Sunscale", hp: 2, value: 2, speed: 105, radius: 20, tier: 1, glyph: "◆" },
  { id: "blue_gar", name: "Blue Gar", hp: 3, value: 3, speed: 88, radius: 24, tier: 1, glyph: "◈" },
  { id: "cypress_ray", name: "Cypress Ray", hp: 4, value: 4, speed: 76, radius: 28, tier: 1, glyph: "◒" },
  { id: "obsidian_catfish", name: "Obsidian Catfish", hp: 6, value: 7, speed: 68, radius: 31, tier: 2, glyph: "◉" },
  { id: "golden_carp", name: "Golden Carp", hp: 8, value: 9, speed: 61, radius: 34, tier: 2, glyph: "✦" },
  { id: "jaguar_gar", name: "Jaguar Gar", hp: 10, value: 12, speed: 82, radius: 36, tier: 2, glyph: "✧" },
  { id: "feather_eel", name: "Feather Eel", hp: 12, value: 15, speed: 94, radius: 38, tier: 2, glyph: "≋" },
  { id: "sun_serpent", name: "Sun Serpent", hp: 25, value: 30, speed: 45, radius: 48, tier: 3, glyph: "☼" },
  { id: "storm_turtle", name: "Storm Turtle", hp: 35, value: 45, speed: 38, radius: 52, tier: 3, glyph: "◉" },
  { id: "celestial_ray", name: "Celestial Ray", hp: 45, value: 60, speed: 52, radius: 56, tier: 3, glyph: "☽" },
];

const WEAPONS = [
  { name: "CANNON I", damage: 1, cost: 1 },
  { name: "CANNON II", damage: 2, cost: 2 },
  { name: "CANNON III", damage: 3, cost: 3 },
  { name: "CANNON IV", damage: 5, cost: 5 },
  { name: "GOLDEN CANNON", damage: 10, cost: 10 },
];

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

function mulberry32(seed) {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeCreature(rng, wave, id) {
  const maxTier = wave >= 8 ? 3 : wave >= 4 ? 2 : 1;
  const pool = CREATURES.filter((c) => c.tier <= maxTier);
  const base = pool[Math.floor(rng() * pool.length)];
  const side = rng() > 0.5 ? 1 : -1;
  const y = 110 + rng() * 470;
  return {
    ...base,
    instanceId: id,
    x: side === 1 ? -base.radius * 2 : GAME.width + base.radius * 2,
    y,
    dir: side,
    phase: rng() * Math.PI * 2,
    phaseSpeed: 0.7 + rng() * 1.1,
    hp: base.hp + Math.floor(Math.max(0, wave - 5) / 4),
    maxHp: base.hp + Math.floor(Math.max(0, wave - 5) / 4),
    speed: base.speed * (1 + Math.min(0.35, wave * 0.018)),
    age: 0,
  };
}

function makeBoss() {
  return {
    instanceId: "golden_xolotl",
    name: "GOLDEN XOLOTL",
    x: GAME.width + 180,
    y: GAME.height * 0.48,
    dir: -1,
    hp: 5000,
    maxHp: 5000,
    radius: 100,
    speed: 46,
    phase: 0,
    phaseIndex: 1,
    age: 0,
    invuln: 0,
  };
}

export default function GoldenXolotlGame({ onExit }) {
  const canvasRef = useRef(null);
  const frameRef = useRef(0);
  const stateRef = useRef(null);
  const [hud, setHud] = useState({
    score: 0, wave: 1, combo: 0, credits: 2500, fury: 0, cannon: 1, boss: false, bossHp: 5000,
  });
  const [paused, setPaused] = useState(false);
  const pausedRef = useRef(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const rng = mulberry32(0x584f4c4f);
    const s = {
      running: true,
      last: performance.now(),
      elapsed: 0,
      wave: 1,
      score: 0,
      credits: 2500,
      combo: 0,
      comboUntil: 0,
      fury: 0,
      cannon: 1,
      aim: { x: GAME.width * 0.5, y: GAME.height * 0.5 },
      creatures: [],
      shots: [],
      particles: [],
      floats: [],
      boss: null,
      waveKills: 0,
      hudClock: 0,
      totalKills: 0,
      spawnClock: 0,
      shotClock: 0,
      shake: 0,
      event: "",
      eventUntil: 0,
      rng,
      nextId: 1,
    };
    stateRef.current = s;

    const fit = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = GAME.width * dpr;
      canvas.height = GAME.height * dpr;
      canvas.style.aspectRatio = `${GAME.width}/${GAME.height}`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      s.display = { width: rect.width, height: rect.height };
    };
    fit();
    window.addEventListener("resize", fit);

    const pointer = (e) => {
      const rect = canvas.getBoundingClientRect();
      s.aim.x = clamp(((e.clientX - rect.left) / rect.width) * GAME.width, 0, GAME.width);
      s.aim.y = clamp(((e.clientY - rect.top) / rect.height) * GAME.height, 70, GAME.height - 55);
    };
    const touch = (e) => {
      const t = e.touches[0];
      if (!t) return;
      pointer({ clientX: t.clientX, clientY: t.clientY });
    };
    const shoot = (e) => {
      if (e.button !== undefined && e.button !== 0) return;
      fire();
    };
    const fire = () => {
      if (!s.running || pausedRef.current) return;
      const weapon = WEAPONS[s.cannon - 1];
      if (s.credits < weapon.cost) return;
      s.credits -= weapon.cost;
      s.shotClock = 90;
      const angle = Math.atan2(s.aim.y - (GAME.height - 44), s.aim.x - GAME.width / 2);
      s.shots.push({
        x: GAME.width / 2,
        y: GAME.height - 44,
        vx: Math.cos(angle) * 780,
        vy: Math.sin(angle) * 780,
        damage: weapon.damage,
        age: 0,
      });
    };

    canvas.addEventListener("mousemove", pointer);
    canvas.addEventListener("mousedown", shoot);
    canvas.addEventListener("touchmove", touch, { passive: true });
    canvas.addEventListener("touchstart", (e) => { touch(e); fire(); }, { passive: true });

    const spawn = () => {
      if (s.boss) return;
      const count = s.wave >= 7 ? 2 : 1;
      for (let i = 0; i < count; i++) s.creatures.push(makeCreature(s.rng, s.wave, s.nextId++));
    };

    const burst = (x, y, glyph, amount = 16) => {
      for (let i = 0; i < amount; i++) {
        const a = s.rng() * Math.PI * 2;
        const speed = 40 + s.rng() * 180;
        s.particles.push({
          x, y, vx: Math.cos(a) * speed, vy: Math.sin(a) * speed,
          life: 0.55 + s.rng() * 0.55, max: 1.1, size: 2 + s.rng() * 4, glyph,
        });
      }
      s.shake = Math.min(10, s.shake + 2.5);
    };

    const defeat = (c) => {
      const comboMult = s.combo >= 25 ? 1.75 : s.combo >= 15 ? 1.5 : s.combo >= 10 ? 1.35 : s.combo >= 6 ? 1.2 : s.combo >= 3 ? 1.1 : 1;
      const waveMult = 1 + Math.min(0.5, s.wave * 0.02);
      const reward = Math.floor(c.value * comboMult * waveMult);
      s.credits += reward;
      s.score += reward;
      s.combo += 1;
      s.comboUntil = s.elapsed + 3;
      s.fury = clamp(s.fury + Math.min(9, 2 + c.tier * 1.2), 0, 100);
      s.waveKills += 1;
      s.totalKills += 1;
      s.floats.push({ x: c.x, y: c.y, text: `+${reward}`, life: 1, max: 1, big: c.tier === 3 });
      burst(c.x, c.y, c.glyph, c.tier === 3 ? 28 : 16);
      if (s.waveKills >= 8 + s.wave * 2) {
        s.wave += 1;
        s.waveKills = 0;
        s.event = s.wave === GAME.bossWave ? "THE GOLDEN XOLOTL AWAKENS" : `WAVE ${s.wave}`;
        s.eventUntil = s.elapsed + 2.6;
        if (s.wave === GAME.bossWave) {
          s.boss = makeBoss();
          s.event = "THE GOLDEN XOLOTL AWAKENS";
        }
      }
    };

    const updateHud = () => setHud({
      score: s.score, wave: s.wave, combo: s.combo, credits: s.credits, fury: Math.floor(s.fury),
      cannon: s.cannon, boss: !!s.boss, bossHp: s.boss?.hp || 0,
    });

    const update = (dt) => {
      if (!s.running || paused) return;
      s.elapsed += dt;
      s.hudClock += dt;
      s.shotClock = Math.max(0, s.shotClock - dt * 1000);
      s.shake *= Math.pow(0.04, dt);
      if (s.combo && s.elapsed > s.comboUntil) s.combo = 0;

      if (!s.boss) {
        s.spawnClock -= dt;
        const interval = Math.max(0.42, 1.15 - s.wave * 0.045);
        if (s.spawnClock <= 0) { spawn(); s.spawnClock = interval; }
      }

      for (const c of s.creatures) {
        c.age += dt;
        c.x += c.dir * c.speed * dt;
        c.y += Math.sin(c.age * c.phaseSpeed + c.phase) * 18 * dt;
      }
      s.creatures = s.creatures.filter((c) => c.x > -160 && c.x < GAME.width + 160);

      for (const p of s.shots) {
        p.age += dt;
        p.x += p.vx * dt;
        p.y += p.vy * dt;
      }
      s.shots = s.shots.filter((p) => p.age < 2.2 && p.x > -50 && p.x < GAME.width + 50 && p.y > 40 && p.y < GAME.height + 30);

      for (const p of s.shots) {
        if (p.hit) continue;
        if (s.boss) {
          const dx = p.x - s.boss.x, dy = p.y - s.boss.y;
          if (Math.hypot(dx, dy) < s.boss.radius + 10 && s.boss.invuln <= 0) {
            p.hit = true;
            s.boss.hp = Math.max(0, s.boss.hp - p.damage);
            s.boss.invuln = 0.07;
            s.fury = clamp(s.fury + 0.7, 0, 100);
            burst(p.x, p.y, "✦", 7);
            if (s.boss.hp <= 0) {
              const reward = 1250 + s.wave * 100;
              s.credits += reward;
              s.score += reward;
              s.fury = 100;
              s.event = "XOLOTL DEFEATED";
              s.eventUntil = s.elapsed + 4;
              burst(s.boss.x, s.boss.y, "☼", 70);
              s.boss = null;
              s.wave += 1;
              s.waveKills = 0;
            }
          }
        } else {
          for (const c of s.creatures) {
            if (c.dead) continue;
            const dx = p.x - c.x, dy = p.y - c.y;
            if (Math.hypot(dx, dy) < c.radius + 8) {
              p.hit = true;
              c.hp -= p.damage;
              burst(p.x, p.y, "✦", 4);
              if (c.hp <= 0) { c.dead = true; defeat(c); }
              break;
            }
          }
        }
      }
      s.creatures = s.creatures.filter((c) => !c.dead);

      if (s.boss) {
        s.boss.age += dt;
        s.boss.phase += dt * 1.4;
        s.boss.invuln = Math.max(0, s.boss.invuln - dt);
        const targetX = GAME.width * 0.66 + Math.sin(s.boss.age * 0.8) * 260;
        const targetY = GAME.height * 0.45 + Math.sin(s.boss.age * 1.4) * 150;
        s.boss.x += (targetX - s.boss.x) * dt * 0.9;
        s.boss.y += (targetY - s.boss.y) * dt * 0.9;
      }

      for (const p of s.particles) {
        p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vx *= 0.97; p.vy *= 0.97;
      }
      s.particles = s.particles.filter((p) => p.life > 0);
      for (const f of s.floats) { f.life -= dt; f.y -= 35 * dt; }
      s.floats = s.floats.filter((f) => f.life > 0);
      if (s.hudClock >= 0.1) { s.hudClock = 0; updateHud(); }
    };

    const drawBackground = () => {
      const g = ctx.createLinearGradient(0, 0, 0, GAME.height);
      g.addColorStop(0, "#071522"); g.addColorStop(0.48, "#073646"); g.addColorStop(1, "#02070a");
      ctx.fillStyle = g; ctx.fillRect(0, 0, GAME.width, GAME.height);
      ctx.fillStyle = "rgba(212,175,55,.08)";
      for (let i = 0; i < 18; i++) {
        const x = (i * 83 + Math.sin(s.elapsed * 0.2 + i) * 20) % GAME.width;
        const y = 130 + ((i * 47) % 450);
        ctx.beginPath(); ctx.arc(x, y, 2 + (i % 3), 0, Math.PI * 2); ctx.fill();
      }
      ctx.strokeStyle = "rgba(212,175,55,.09)"; ctx.lineWidth = 2;
      for (let x = 0; x < GAME.width; x += 160) {
        ctx.beginPath(); ctx.moveTo(x, 70); ctx.lineTo(x + 80, 720); ctx.stroke();
      }
      ctx.fillStyle = "rgba(0,0,0,.25)";
      for (let i = 0; i < 7; i++) {
        const x = i * 220 - 40;
        ctx.beginPath(); ctx.moveTo(x, 110); ctx.lineTo(x + 55, 35); ctx.lineTo(x + 105, 110); ctx.closePath(); ctx.fill();
      }
      ctx.fillStyle = "#d4af37"; ctx.font = "700 12px monospace"; ctx.textAlign = "center";
      ctx.globalAlpha = 0.45;
      ctx.fillText("A Z T L Á N   D E L T A", GAME.width / 2, 94);
      ctx.globalAlpha = 1;
    };

    const drawCreature = (c) => {
      ctx.save(); ctx.translate(c.x, c.y); ctx.scale(c.dir, 1);
      const hue = c.tier === 3 ? "#e9c46a" : c.tier === 2 ? "#00d1b2" : "#73c7d8";
      ctx.shadowBlur = 16; ctx.shadowColor = hue; ctx.fillStyle = hue;
      ctx.beginPath(); ctx.ellipse(0, 0, c.radius * 1.2, c.radius * 0.66, Math.sin(c.age) * 0.08, 0, Math.PI * 2); ctx.fill();
      ctx.shadowBlur = 0; ctx.fillStyle = "#041016";
      ctx.beginPath(); ctx.arc(c.radius * 0.55, -c.radius * 0.1, 3.5, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = hue; ctx.globalAlpha = 0.7;
      ctx.beginPath(); ctx.moveTo(-c.radius, 0); ctx.lineTo(-c.radius * 1.7, -c.radius * 0.75); ctx.lineTo(-c.radius * 1.55, c.radius * 0.75); ctx.closePath(); ctx.fill();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = "rgba(255,255,255,.45)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.arc(0, 0, c.radius + 6, 0, Math.PI * 2); ctx.stroke();
      ctx.restore();
      if (c.tier >= 2) {
        ctx.fillStyle = "rgba(0,0,0,.55)"; ctx.fillRect(c.x - 28, c.y - c.radius - 13, 56, 4);
        ctx.fillStyle = c.tier === 3 ? "#d4af37" : "#00c8ff";
        ctx.fillRect(c.x - 28, c.y - c.radius - 13, 56 * clamp(c.hp / c.maxHp, 0, 1), 4);
      }
    };

    const drawBoss = () => {
      const b = s.boss;
      if (!b) return;
      ctx.save(); ctx.translate(b.x, b.y);
      const pulse = 1 + Math.sin(b.phase) * 0.05;
      ctx.scale(pulse, pulse);
      ctx.shadowBlur = 45; ctx.shadowColor = "#d4af37";
      ctx.fillStyle = "#d4af37";
      ctx.beginPath(); ctx.arc(0, 0, b.radius, 0, Math.PI * 2); ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = "#07090b";
      ctx.beginPath(); ctx.arc(-22, -8, 10, 0, Math.PI * 2); ctx.arc(22, -8, 10, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#fff0a8";
      ctx.beginPath(); ctx.arc(-22, -8, 4, 0, Math.PI * 2); ctx.arc(22, -8, 4, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = "#071522"; ctx.lineWidth = 8;
      ctx.beginPath(); ctx.arc(0, 8, 42, 0.2, Math.PI - 0.2); ctx.stroke();
      ctx.strokeStyle = "rgba(255,240,168,.65)"; ctx.lineWidth = 3;
      for (let i = 0; i < 8; i++) {
        const a = (Math.PI * 2 * i) / 8 + b.phase * 0.2;
        ctx.beginPath(); ctx.moveTo(Math.cos(a) * 110, Math.sin(a) * 110); ctx.lineTo(Math.cos(a) * 145, Math.sin(a) * 145); ctx.stroke();
      }
      ctx.restore();
      ctx.fillStyle = "rgba(0,0,0,.72)"; ctx.fillRect(280, 22, 720, 30);
      ctx.fillStyle = "#d4af37"; ctx.font = "900 16px monospace"; ctx.textAlign = "center";
      ctx.fillText("GOLDEN XOLOTL", GAME.width / 2, 44);
      ctx.fillStyle = "#190f04"; ctx.fillRect(400, 58, 480, 10);
      ctx.fillStyle = "#d4af37"; ctx.fillRect(400, 58, 480 * clamp(b.hp / b.maxHp, 0, 1), 10);
    };

    const drawCannon = () => {
      ctx.save();
      ctx.translate(GAME.width / 2, GAME.height - 44);
      const angle = Math.atan2(s.aim.y - (GAME.height - 44), s.aim.x - GAME.width / 2);
      ctx.rotate(angle);
      ctx.fillStyle = "#111820"; ctx.strokeStyle = "#d4af37"; ctx.lineWidth = 3;
      ctx.shadowBlur = 18; ctx.shadowColor = "#d4af37";
      ctx.fillRect(0, -12, 95, 24); ctx.strokeRect(0, -12, 95, 24);
      ctx.fillStyle = "#d4af37"; ctx.fillRect(74, -7, 30, 14);
      ctx.restore();
      ctx.fillStyle = "#d4af37"; ctx.font = "900 11px monospace"; ctx.textAlign = "center";
      ctx.fillText(WEAPONS[s.cannon - 1].name, GAME.width / 2, GAME.height - 10);
      ctx.strokeStyle = "rgba(212,175,55,.35)"; ctx.beginPath(); ctx.arc(s.aim.x, s.aim.y, 18, 0, Math.PI * 2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(s.aim.x - 28, s.aim.y); ctx.lineTo(s.aim.x - 8, s.aim.y); ctx.moveTo(s.aim.x + 8, s.aim.y); ctx.lineTo(s.aim.x + 28, s.aim.y); ctx.moveTo(s.aim.x, s.aim.y - 28); ctx.lineTo(s.aim.x, s.aim.y - 8); ctx.moveTo(s.aim.x, s.aim.y + 8); ctx.lineTo(s.aim.x, s.aim.y + 28); ctx.stroke();
    };

    const draw = () => {
      drawBackground();
      const shake = s.shake;
      ctx.save(); ctx.translate((rng() - 0.5) * shake, (rng() - 0.5) * shake);
      for (const c of s.creatures) drawCreature(c);
      drawBoss();
      for (const p of s.shots) {
        ctx.fillStyle = "#ffe9a0"; ctx.shadowBlur = 14; ctx.shadowColor = "#d4af37";
        ctx.beginPath(); ctx.arc(p.x, p.y, 5, 0, Math.PI * 2); ctx.fill();
      }
      ctx.shadowBlur = 0;
      for (const p of s.particles) {
        ctx.globalAlpha = clamp(p.life / p.max, 0, 1);
        ctx.fillStyle = "#d4af37"; ctx.font = `${10 + p.size}px serif`; ctx.textAlign = "center"; ctx.fillText(p.glyph, p.x, p.y);
      }
      for (const f of s.floats) {
        ctx.globalAlpha = clamp(f.life / f.max, 0, 1);
        ctx.fillStyle = f.big ? "#ffe9a0" : "#d4af37"; ctx.font = `${f.big ? 24 : 15}px monospace`; ctx.textAlign = "center"; ctx.fillText(f.text, f.x, f.y);
      }
      ctx.globalAlpha = 1;
      ctx.restore();
      drawCannon();

      if (s.event && s.elapsed < s.eventUntil) {
        ctx.fillStyle = "rgba(0,0,0,.45)"; ctx.fillRect(0, 250, GAME.width, 110);
        ctx.fillStyle = "#ffe9a0"; ctx.font = "900 34px monospace"; ctx.textAlign = "center";
        ctx.shadowBlur = 25; ctx.shadowColor = "#d4af37"; ctx.fillText(s.event, GAME.width / 2, 315); ctx.shadowBlur = 0;
      }
    };

    const loop = (now) => {
      if (!s.running) return;
      const dt = Math.min(0.033, (now - s.last) / 1000);
      s.last = now;
      update(dt);
      draw();
      frameRef.current = requestAnimationFrame(loop);
    };
    frameRef.current = requestAnimationFrame(loop);
    updateHud();

    return () => {
      s.running = false;
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", fit);
      canvas.removeEventListener("mousemove", pointer);
      canvas.removeEventListener("mousedown", shoot);
      canvas.removeEventListener("touchmove", touch);
    };
  }, []);

  const upgrade = () => {
    const s = stateRef.current;
    if (!s || s.cannon >= 5) return;
    const next = WEAPONS[s.cannon];
    if (s.credits >= next.cost * 12) {
      s.credits -= next.cost * 12;
      s.cannon += 1;
      setHud((h) => ({ ...h, credits: s.credits, cannon: s.cannon }));
    }
  };

  const togglePause = () => {
    pausedRef.current = !pausedRef.current;
    setPaused(pausedRef.current);
  };

  const fury = () => {
    const s = stateRef.current;
    if (!s || s.fury < 100 || paused) return;
    s.fury = 0;
    for (const c of s.creatures) c.hp = Math.max(0, c.hp - 12);
    if (s.boss) s.boss.hp = Math.max(1, s.boss.hp - 150);
    s.event = "XOLOTL FURY";
    s.eventUntil = s.elapsed + 1.8;
  };

  return (
    <div className="relative w-full h-full bg-black overflow-hidden select-none">
      <button onClick={onExit} className="absolute top-3 left-3 z-30 px-3 py-2 bg-black/80 border border-zinc-700 text-zinc-300 hover:border-[#d4af37] hover:text-[#d4af37] text-[9px] uppercase tracking-widest">
        ← Lobby
      </button>
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full object-contain cursor-crosshair touch-none"
        aria-label="Golden Xolotl fish shooting arcade"
      />
      <div className="absolute top-0 inset-x-0 p-3 md:p-5 pointer-events-none flex justify-between items-start">
        <div className="flex gap-2 md:gap-3">
          <div className="px-3 py-2 bg-black/75 border border-[#d4af37]/40 backdrop-blur text-[#ffe9a0]">
            <div className="text-[8px] uppercase tracking-[3px] text-zinc-500">Score</div>
            <div className="font-black font-mono text-lg">{hud.score.toLocaleString()}</div>
          </div>
          <div className="px-3 py-2 bg-black/75 border border-[#d4af37]/40 backdrop-blur">
            <div className="text-[8px] uppercase tracking-[3px] text-zinc-500">Wave</div>
            <div className="font-black font-mono text-lg text-[#d4af37]">{hud.wave}</div>
          </div>
          {hud.combo > 1 && <div className="px-3 py-2 bg-black/75 border border-[#00c8ff]/50 backdrop-blur">
            <div className="text-[8px] uppercase tracking-[3px] text-zinc-500">Combo</div>
            <div className="font-black font-mono text-lg text-[#00c8ff]">x{hud.combo}</div>
          </div>}
        </div>
        <div className="text-right">
          <div className="px-3 py-2 bg-black/75 border border-[#d4af37]/40 backdrop-blur">
            <div className="text-[8px] uppercase tracking-[3px] text-zinc-500">Arcade Credits</div>
            <div className="font-black font-mono text-lg text-[#ffe9a0]">{hud.credits.toLocaleString()}</div>
          </div>
        </div>
      </div>
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-[min(94%,760px)] pointer-events-none">
        <div className="flex items-center gap-2">
          <div className="flex-1 h-3 bg-black/80 border border-[#d4af37]/30 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-[#8b6508] to-[#ffe9a0] transition-all" style={{ width: `${hud.fury}%` }} />
          </div>
          <span className="text-[8px] tracking-[2px] text-[#d4af37] font-bold">FURY</span>
        </div>
      </div>
      <div className="absolute bottom-3 right-3 flex gap-2">
        <button onClick={togglePause} className="px-3 py-2 text-[9px] uppercase tracking-widest bg-black/80 border border-zinc-700 text-zinc-300 hover:border-[#d4af37]"> {paused ? "Resume" : "Pause"} </button>
        <button onClick={upgrade} disabled={hud.cannon >= 5} className="px-3 py-2 text-[9px] uppercase tracking-widest bg-black/80 border border-[#d4af37]/50 text-[#d4af37] disabled:opacity-40">Upgrade</button>
        <button onClick={fury} disabled={hud.fury < 100} className="px-3 py-2 text-[9px] uppercase tracking-widest bg-[#d4af37]/10 border border-[#d4af37] text-[#ffe9a0] disabled:opacity-35">Xolotl Fury</button>
      </div>
      <div className="absolute top-3 right-3 text-right pointer-events-none">
        <div className="text-[8px] uppercase tracking-[2px] text-zinc-600">DEMO ECONOMY</div>
        <div className="text-[7px] uppercase tracking-[2px] text-zinc-700">Virtual credits only</div>
      </div>
      <div className="absolute top-3 left-1/2 -translate-x-1/2 text-center pointer-events-none">
        <div className="text-[9px] uppercase tracking-[5px] text-[#d4af37]">SLA113 · SOUTHERN HUNT</div>
        <div className="text-[7px] uppercase tracking-[3px] text-zinc-600 mt-1">Virtual arcade credits · original game rules</div>
      </div>
    </div>
  );
}
