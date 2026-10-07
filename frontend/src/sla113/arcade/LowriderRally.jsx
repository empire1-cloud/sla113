import React, { useEffect, useRef, useState } from 'react';
import ArcadeChrome from './ArcadeChrome';
import { addCacao, spendCacao } from './arcadeWallet';
import { sfx } from './arcadeSfx';

/**
 * Lowrider Rally: Calzada del Sol — pseudo-3D kart racer (Canvas2D).
 * Signature move: hydraulics HOP clears rival cars and grabs high cacao.
 */

const ENTRY = 50;
const LAPS = 3;
const PRIZES = [ENTRY * 5, ENTRY * 2.5, ENTRY * 1.5]; // 1st, 2nd, 3rd

const SEG = 200;            // segment length (world units)
const ROAD = 2000;          // road half-width
const RUMBLE = 3;           // segments per rumble stripe
const DRAW = 220;           // segments drawn ahead
const CAM_H = 1000;
const CAM_DEPTH = 1 / Math.tan((100 / 2) * Math.PI / 180);
const PLAYER_Z = CAM_H * CAM_DEPTH;
const MAX_SPEED = SEG * 60;
const ACCEL = MAX_SPEED / 5;
const BRAKE = -MAX_SPEED;
const DECEL = -MAX_SPEED / 5;
const OFFROAD_DECEL = -MAX_SPEED / 2;
const OFFROAD_LIMIT = MAX_SPEED / 4;
const CENTRIFUGAL = 0.3;
const HOP_TIME = 0.7;
const HOP_COOLDOWN = 1.6;
const CAR_W = 520;
const CAR_H = 300;

const CANDY = ['#e4007c', '#1fb5a3', '#7b2cbf', '#ff9f1c', '#2f6fde'];
const RIVAL_NAMES = ['La Rosa', 'El Jade', 'Morado', 'Cempasúchil', 'Azul Real'];

// Track: [enter, hold, leave, curve]
const COURSE = [
  [20, 40, 20, 0], [30, 60, 30, 4], [20, 40, 20, 0], [30, 50, 30, -5],
  [25, 25, 25, 2], [25, 25, 25, -2], [30, 70, 30, 6], [20, 60, 20, 0],
  [30, 40, 30, -4], [40, 50, 40, 3], [20, 40, 20, 0],
];

const ease = (a, b, p) => a + (b - a) * ((-Math.cos(p * Math.PI) / 2) + 0.5);

function buildTrack() {
  const segs = [];
  const add = (curve) => {
    const i = segs.length;
    segs.push({ index: i, curve, sprites: [], gate: false, dark: Math.floor(i / RUMBLE) % 2 === 1 });
  };
  for (const [enter, hold, leave, curve] of COURSE) {
    for (let n = 0; n < enter; n++) add(ease(0, curve, n / enter));
    for (let n = 0; n < hold; n++) add(curve);
    for (let n = 0; n < leave; n++) add(ease(curve, 0, n / leave));
  }
  const kinds = ['nopal', 'piramide', 'palma', 'nopal', 'farol'];
  segs.forEach((s, i) => {
    if (i % 7 === 0 && i > 10) {
      s.sprites.push({ kind: kinds[(i / 7) % kinds.length | 0], offset: -1.5 - (i % 3) * 0.35 });
      s.sprites.push({ kind: kinds[((i / 7) + 2) % kinds.length | 0], offset: 1.5 + (i % 4) * 0.3 });
    }
    if (i % 90 === 0) s.gate = true;
  });
  const pickups = [];
  for (let i = 40; i < segs.length - 10; i += 18) {
    const high = i % 72 === 40; // floating cacao — hop to grab
    pickups.push({ seg: i, offset: Math.sin(i * 0.37) * 0.6, high, value: high ? 15 : 3 });
  }
  return { segs, length: segs.length * SEG, pickups };
}

/* ---------- drawing helpers ---------- */

function poly(ctx, x1, y1, x2, y2, x3, y3, x4, y4, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineTo(x3, y3); ctx.lineTo(x4, y4);
  ctx.closePath();
  ctx.fill();
}

function drawSegment(ctx, w, p1, p2, dark, isStart) {
  const r1 = p1.sw / 8; const r2 = p2.sw / 8;
  ctx.fillStyle = dark ? '#7a4a2a' : '#8a5634'; // adobe dirt
  ctx.fillRect(0, p2.sy, w, p1.sy - p2.sy);
  // Rumble: flag colors
  poly(ctx, p1.sx - p1.sw - r1, p1.sy, p1.sx - p1.sw, p1.sy, p2.sx - p2.sw, p2.sy, p2.sx - p2.sw - r2, p2.sy, dark ? '#d7263d' : '#f6ead0');
  poly(ctx, p1.sx + p1.sw + r1, p1.sy, p1.sx + p1.sw, p1.sy, p2.sx + p2.sw, p2.sy, p2.sx + p2.sw + r2, p2.sy, dark ? '#1a8f4a' : '#f6ead0');
  poly(ctx, p1.sx - p1.sw, p1.sy, p1.sx + p1.sw, p1.sy, p2.sx + p2.sw, p2.sy, p2.sx - p2.sw, p2.sy, isStart ? '#f6ead0' : (dark ? '#3a3440' : '#423b48'));
  if (!dark && !isStart) {
    const l1 = p1.sw / 40; const l2 = p2.sw / 40;
    for (const lane of [-1 / 3, 1 / 3]) {
      const x1 = p1.sx + p1.sw * lane * 2; const x2 = p2.sx + p2.sw * lane * 2;
      poly(ctx, x1 - l1, p1.sy, x1 + l1, p1.sy, x2 + l2, p2.sy, x2 - l2, p2.sy, '#f2b632');
    }
  }
}

function drawLowrider(ctx, x, y, width, color, opts = {}) {
  const h = width * (CAR_H / CAR_W);
  const lift = opts.lift || 0;
  // shadow
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.beginPath();
  ctx.ellipse(x, y, width * 0.55, h * 0.12, 0, 0, Math.PI * 2);
  ctx.fill();
  const by = y - lift;
  // wheels (gold spokes)
  ctx.fillStyle = '#111';
  ctx.fillRect(x - width * 0.48, by - h * 0.28, width * 0.16, h * 0.28);
  ctx.fillRect(x + width * 0.32, by - h * 0.28, width * 0.16, h * 0.28);
  ctx.fillStyle = '#f2b632';
  ctx.fillRect(x - width * 0.44, by - h * 0.2, width * 0.08, h * 0.12);
  ctx.fillRect(x + width * 0.36, by - h * 0.2, width * 0.08, h * 0.12);
  // body
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x - width * 0.5, by - h * 0.22);
  ctx.lineTo(x + width * 0.5, by - h * 0.22);
  ctx.lineTo(x + width * 0.5, by - h * 0.6);
  ctx.lineTo(x + width * 0.32, by - h * 0.66);
  ctx.lineTo(x + width * 0.24, by - h * 0.98);
  ctx.lineTo(x - width * 0.24, by - h * 0.98);
  ctx.lineTo(x - width * 0.32, by - h * 0.66);
  ctx.lineTo(x - width * 0.5, by - h * 0.6);
  ctx.closePath();
  ctx.fill();
  // rear window + pinstripe
  ctx.fillStyle = 'rgba(20,10,30,0.85)';
  ctx.fillRect(x - width * 0.2, by - h * 0.92, width * 0.4, h * 0.22);
  ctx.strokeStyle = 'rgba(255,240,200,0.7)';
  ctx.lineWidth = Math.max(1, width / 160);
  ctx.beginPath();
  ctx.moveTo(x - width * 0.46, by - h * 0.5);
  ctx.quadraticCurveTo(x, by - h * 0.42, x + width * 0.46, by - h * 0.5);
  ctx.stroke();
  // chrome bumper + tail lights
  ctx.fillStyle = '#d9d9e3';
  ctx.fillRect(x - width * 0.52, by - h * 0.3, width * 1.04, h * 0.08);
  ctx.fillStyle = opts.braking ? '#ff3030' : '#a3121f';
  ctx.fillRect(x - width * 0.47, by - h * 0.52, width * 0.14, h * 0.1);
  ctx.fillRect(x + width * 0.33, by - h * 0.52, width * 0.14, h * 0.1);
  if (opts.label) {
    ctx.fillStyle = '#fff';
    ctx.font = `800 ${Math.max(9, width / 9)}px system-ui`;
    ctx.textAlign = 'center';
    ctx.fillText(opts.label, x, by - h * 1.1);
  }
}

function drawScenery(ctx, kind, x, y, scale, w) {
  const u = scale * w / 2; // pixels per world unit
  if (kind === 'nopal') {
    const s = 900 * u;
    ctx.fillStyle = '#2f8f4e';
    ctx.beginPath(); ctx.ellipse(x, y - s * 0.45, s * 0.22, s * 0.45, 0, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x - s * 0.28, y - s * 0.75, s * 0.15, s * 0.28, -0.4, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x + s * 0.26, y - s * 0.8, s * 0.14, s * 0.26, 0.4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#e4007c';
    ctx.beginPath(); ctx.arc(x + s * 0.3, y - s * 1.05, s * 0.06, 0, Math.PI * 2); ctx.fill();
  } else if (kind === 'piramide') {
    const s = 2600 * u;
    const tiers = 4;
    for (let t = 0; t < tiers; t++) {
      const tw = s * (1 - t * 0.2); const th = s * 0.16;
      ctx.fillStyle = t % 2 ? '#a0703c' : '#b9844a';
      ctx.fillRect(x - tw / 2, y - th * (t + 1), tw, th);
    }
    ctx.fillStyle = '#d7263d';
    ctx.fillRect(x - s * 0.12, y - s * 0.16 * tiers - s * 0.14, s * 0.24, s * 0.14);
  } else if (kind === 'palma') {
    const s = 1800 * u;
    ctx.strokeStyle = '#6b4423'; ctx.lineWidth = Math.max(1, s * 0.05);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.quadraticCurveTo(x + s * 0.1, y - s * 0.5, x, y - s); ctx.stroke();
    ctx.strokeStyle = '#1a8f4a'; ctx.lineWidth = Math.max(1, s * 0.04);
    for (let a = 0; a < 6; a++) {
      const ang = Math.PI + (a / 5) * Math.PI;
      ctx.beginPath(); ctx.moveTo(x, y - s);
      ctx.quadraticCurveTo(x + Math.cos(ang) * s * 0.3, y - s - s * 0.12, x + Math.cos(ang) * s * 0.42, y - s + Math.abs(Math.sin(ang)) * s * 0.1 + s * 0.1);
      ctx.stroke();
    }
  } else if (kind === 'farol') {
    const s = 1400 * u;
    ctx.fillStyle = '#2a2230'; ctx.fillRect(x - s * 0.03, y - s, s * 0.06, s);
    ctx.fillStyle = '#ffd86b'; ctx.shadowColor = '#ffd86b'; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.arc(x, y - s, s * 0.08, 0, Math.PI * 2); ctx.fill();
    ctx.shadowBlur = 0;
  }
}

function drawGate(ctx, p, t) {
  const h = p.sw * 0.9;
  const top = p.sy - h;
  ctx.fillStyle = '#2a2230';
  ctx.fillRect(p.sx - p.sw * 1.1, top, p.sw * 0.04, h);
  ctx.fillRect(p.sx + p.sw * 1.06, top, p.sw * 0.04, h);
  const colors = ['#e4007c', '#ff9f1c', '#1fb5a3', '#f2b632', '#d7263d', '#7b2cbf'];
  const n = 12; const fw = (p.sw * 2.2) / n;
  for (let i = 0; i < n; i++) {
    const fx = p.sx - p.sw * 1.1 + i * fw;
    const sway = Math.sin(t * 3 + i) * fw * 0.06;
    ctx.fillStyle = colors[i % colors.length];
    ctx.beginPath();
    ctx.moveTo(fx + 1, top);
    ctx.lineTo(fx + fw - 1, top);
    ctx.lineTo(fx + fw - 1 + sway, top + fw * 1.1);
    ctx.lineTo(fx + fw / 2 + sway, top + fw * 1.35);
    ctx.lineTo(fx + 1 + sway, top + fw * 1.1);
    ctx.closePath();
    ctx.fill();
  }
}

function drawSky(ctx, w, h, skyOffset) {
  const horizon = h / 2;
  const g = ctx.createLinearGradient(0, 0, 0, horizon);
  g.addColorStop(0, '#2b0f3a'); g.addColorStop(0.55, '#c2185b'); g.addColorStop(1, '#ff9f1c');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, horizon + 2);
  // Sun stone rising over the calzada
  const sx = w / 2 - skyOffset * 0.15 % w; const sr = Math.min(w, h) * 0.16;
  ctx.fillStyle = '#ffd86b';
  ctx.beginPath(); ctx.arc(sx, horizon - sr * 0.15, sr, Math.PI, 0); ctx.fill();
  ctx.strokeStyle = '#c2185b'; ctx.lineWidth = 2;
  for (let r = 0.35; r < 1; r += 0.22) { ctx.beginPath(); ctx.arc(sx, horizon - sr * 0.15, sr * r, Math.PI, 0); ctx.stroke(); }
  for (let a = 0; a < 16; a++) {
    const ang = Math.PI + (a / 16) * Math.PI;
    ctx.beginPath();
    ctx.moveTo(sx + Math.cos(ang) * sr * 1.05, horizon - sr * 0.15 + Math.sin(ang) * sr * 1.05);
    ctx.lineTo(sx + Math.cos(ang) * sr * 1.22, horizon - sr * 0.15 + Math.sin(ang) * sr * 1.22);
    ctx.strokeStyle = '#ffd86b'; ctx.stroke();
  }
  // Parallax skyline: volcanoes + temple silhouettes
  const off = (skyOffset * 0.5) % w;
  ctx.fillStyle = '#4a1942';
  for (let k = -1; k < 2; k++) {
    const bx = k * w - off;
    ctx.beginPath();
    ctx.moveTo(bx, horizon);
    ctx.lineTo(bx + w * 0.12, horizon - h * 0.12); ctx.lineTo(bx + w * 0.16, horizon - h * 0.11);
    ctx.lineTo(bx + w * 0.3, horizon - h * 0.02);
    ctx.lineTo(bx + w * 0.62, horizon - h * 0.02);
    ctx.lineTo(bx + w * 0.76, horizon - h * 0.16); ctx.lineTo(bx + w * 0.8, horizon - h * 0.15);
    ctx.lineTo(bx + w, horizon);
    ctx.closePath();
    ctx.fill();
  }
  const off2 = (skyOffset) % w;
  ctx.fillStyle = '#2b0f3a';
  for (let k = -1; k < 2; k++) {
    const bx = k * w - off2;
    for (const [px, pw] of [[0.4, 0.09], [0.52, 0.05], [0.9, 0.07]]) {
      for (let t = 0; t < 3; t++) {
        const tw = w * pw * (1 - t * 0.25);
        ctx.fillRect(bx + w * px - tw / 2, horizon - h * 0.025 * (t + 1), tw, h * 0.026);
      }
    }
  }
}

/* ---------- game ---------- */

function newRace(track) {
  return {
    phase: 'grid', // grid -> countdown -> race -> done
    countdown: 3.5,
    dist: 0,
    x: 0,
    speed: 0,
    hop: 0,
    hopCd: 0,
    time: 0,
    skyOffset: 0,
    collected: 0,
    taken: new Set(),
    bumpFlash: 0,
    toast: null,
    rivals: RIVAL_NAMES.map((name, i) => ({
      name,
      color: CANDY[i],
      dist: (i + 1) * SEG * 6,
      x: [-0.5, 0.5, 0, -0.6, 0.6][i],
      speed: 0,
      target: MAX_SPEED * (0.9 + i * 0.02),
    })),
    finishedAt: null,
    place: null,
    prize: 0,
    track,
  };
}

export default function LowriderRally() {
  const canvasRef = useRef(null);
  const wrapRef = useRef(null);
  const trackRef = useRef(null);
  if (!trackRef.current) trackRef.current = buildTrack();
  const raceRef = useRef(newRace(trackRef.current));
  const keys = useRef({ left: false, right: false, gas: false, brake: false });
  const touchGas = useRef(false);
  const sizeRef = useRef({ w: 900, h: 520, dpr: 1 });
  const [hud, setHud] = useState({ phase: 'grid', lap: 1, place: 6, speed: 0, time: 0, collected: 0, hopReady: true });

  const start = () => {
    const r = raceRef.current;
    if (r.phase === 'countdown' || r.phase === 'race') return;
    if (!spendCacao(ENTRY)) { r.toast = { text: 'Need ' + ENTRY + ' cacao — hit Refill', t: 2.5 }; return; }
    raceRef.current = newRace(trackRef.current);
    raceRef.current.phase = 'countdown';
    sfx.countdown();
  };

  const hop = () => {
    const r = raceRef.current;
    if (r.phase !== 'race' || r.hop > 0 || r.hopCd > 0) return;
    r.hop = HOP_TIME;
    r.hopCd = HOP_COOLDOWN;
    sfx.hop();
  };

  useEffect(() => {
    const resize = () => {
      const wrap = wrapRef.current; const canvas = canvasRef.current;
      if (!wrap || !canvas) return;
      const w = Math.max(320, wrap.getBoundingClientRect().width);
      const h = Math.round(Math.min(w * 0.58, window.innerHeight * 0.68));
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      sizeRef.current = { w, h, dpr };
      canvas.width = Math.floor(w * dpr); canvas.height = Math.floor(h * dpr);
      canvas.style.height = h + 'px';
    };
    resize();
    window.addEventListener('resize', resize);
    const map = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'gas', KeyW: 'gas', ArrowDown: 'brake', KeyS: 'brake' };
    const down = (e) => {
      if (map[e.code]) { keys.current[map[e.code]] = true; e.preventDefault(); }
      if (e.code === 'Space') { e.preventDefault(); const r = raceRef.current; if (r.phase === 'race') hop(); else start(); }
      if (e.code === 'Enter') start();
    };
    const up = (e) => { if (map[e.code]) keys.current[map[e.code]] = false; };
    window.addEventListener('keydown', down);
    window.addEventListener('keyup', up);
    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('keydown', down);
      window.removeEventListener('keyup', up);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let raf; let last = performance.now(); let hudTimer = 0;

    const frame = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      const r = raceRef.current;
      const { segs, length, pickups } = r.track;
      const { w, h, dpr } = sizeRef.current;
      const k = keys.current;

      /* --- update --- */
      if (r.phase === 'countdown') {
        const before = Math.ceil(r.countdown);
        r.countdown -= dt;
        const after = Math.ceil(r.countdown);
        if (after !== before && after > 0) sfx.countdown();
        if (r.countdown <= 0) { r.phase = 'race'; sfx.countdown(true); r.toast = { text: '¡ÁNDALE!', t: 1 }; }
      }

      const racing = r.phase === 'race';
      const pos = r.dist % length;
      const playerSeg = segs[Math.floor((pos + PLAYER_Z) / SEG) % segs.length];
      const speedPct = r.speed / MAX_SPEED;

      if (racing) {
        r.time += dt;
        const steer = dt * 2 * speedPct;
        if (k.left) r.x -= steer;
        if (k.right) r.x += steer;
        r.x -= steer * speedPct * playerSeg.curve * CENTRIFUGAL;
        const gas = k.gas || touchGas.current;
        r.speed += (gas ? ACCEL : k.brake ? BRAKE : DECEL) * dt;
        if ((r.x < -1 || r.x > 1) && r.speed > OFFROAD_LIMIT && r.hop <= 0) r.speed += OFFROAD_DECEL * dt;
        r.x = Math.max(-2.2, Math.min(2.2, r.x));
        r.speed = Math.max(0, Math.min(MAX_SPEED, r.speed));
        r.hop = Math.max(0, r.hop - dt);
        r.hopCd = Math.max(0, r.hopCd - dt);

        // Rivals: cruise, drift back toward their lane, steer around the player.
        for (const c of r.rivals) {
          const cSeg = segs[Math.floor((c.dist % length) / SEG) % segs.length];
          const wobble = 0.92 + 0.08 * Math.sin(r.time * 0.7 + c.dist * 0.0003);
          const cruise = c.target * wobble * (1 - Math.abs(cSeg.curve) * 0.02);
          c.speed = Math.min(cruise, c.speed + ACCEL * 0.9 * dt);
          c.dist += c.speed * dt;
          const gap = c.dist - (r.dist + PLAYER_Z);
          if (gap > 0 && gap < SEG * 8 && Math.abs(c.x - r.x) < 0.4) c.x += (c.x >= r.x ? 1 : -1) * dt * 0.6;
          c.x = Math.max(-0.8, Math.min(0.8, c.x));
        }

        // Collisions with rivals (hop clears them).
        for (const c of r.rivals) {
          const gap = c.dist - (r.dist + PLAYER_Z);
          if (gap > -SEG * 0.3 && gap < SEG * 0.9 && Math.abs(c.x - r.x) < 0.32) {
            if (r.hop > 0) {
              if (!c.cleared) { c.cleared = true; addCacao(2); r.collected += 2; r.toast = { text: 'HOP! +2', t: 0.8 }; sfx.coin(); }
            } else if (r.speed > c.speed) {
              r.speed = c.speed * 0.7;
              r.dist = c.dist - PLAYER_Z - SEG;
              r.bumpFlash = 0.25;
              sfx.bump();
            }
          } else if (gap < -SEG) c.cleared = false;
        }

        // Cacao pickups (high ones need a hop).
        const lap = Math.floor(r.dist / length);
        const segIdx = Math.floor((pos + PLAYER_Z) / SEG) % segs.length;
        for (const p of pickups) {
          const key = lap + ':' + p.seg;
          if (r.taken.has(key)) continue;
          if (Math.abs(p.seg - segIdx) <= 1 && Math.abs(p.offset - r.x) < 0.3 && (!p.high || r.hop > 0)) {
            r.taken.add(key);
            addCacao(p.value);
            r.collected += p.value;
            r.toast = { text: '+' + p.value + ' 🫘', t: 0.7 };
            sfx.coin();
          }
        }

        r.dist += r.speed * dt;
        r.skyOffset += playerSeg.curve * speedPct * dt * 120;

        if (r.dist >= LAPS * length) {
          r.phase = 'done';
          const ahead = r.rivals.filter((c) => c.dist >= r.dist + PLAYER_Z).length;
          r.place = ahead + 1;
          r.prize = Math.floor(PRIZES[ahead] || 0);
          if (r.prize) addCacao(r.prize);
          sfx.win(r.place === 1);
        }
      } else if (r.phase === 'done') {
        r.speed = Math.max(0, r.speed + DECEL * dt);
        r.dist += r.speed * dt;
        for (const c of r.rivals) c.dist += c.speed * dt;
      }
      r.bumpFlash = Math.max(0, r.bumpFlash - dt);
      if (r.toast) { r.toast.t -= dt; if (r.toast.t <= 0) r.toast = null; }

      /* --- render --- */
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      drawSky(ctx, w, h, r.skyOffset);

      const camPos = r.dist % length;
      const base = Math.floor(camPos / SEG);
      const basePct = (camPos % SEG) / SEG;
      const camX = r.x * ROAD;
      let x = 0;
      let dx = -(segs[base].curve * basePct);
      let maxy = h;
      const drawn = [];

      for (let n = 0; n < DRAW; n++) {
        const seg = segs[(base + n) % segs.length];
        const looped = seg.index < base;
        const camZ = camPos - (looped ? length : 0);
        const z1 = seg.index * SEG - camZ; const z2 = z1 + SEG;
        seg.clip = maxy;
        if (z1 <= CAM_DEPTH) { x += dx; dx += seg.curve; continue; }
        const s1 = CAM_DEPTH / z1; const s2 = CAM_DEPTH / z2;
        const p1 = { scale: s1, sx: w / 2 + s1 * (x - camX) * w / 2, sy: h / 2 + s1 * CAM_H * h / 2, sw: s1 * ROAD * w / 2 };
        const p2 = { scale: s2, sx: w / 2 + s2 * (x + dx - camX) * w / 2, sy: h / 2 + s2 * CAM_H * h / 2, sw: s2 * ROAD * w / 2 };
        x += dx; dx += seg.curve;
        seg.p1 = p1; seg.p2 = p2;
        if (p2.sy >= maxy) continue;
        drawSegment(ctx, w, p1, p2, seg.dark, seg.index < 3);
        maxy = p2.sy;
        drawn.push({ seg, n, looped });
      }

      // Sprites, back to front, clipped behind hills/road edges.
      const rivalsBySeg = new Map();
      for (const c of r.rivals) {
        const idx = Math.floor((c.dist % length) / SEG) % segs.length;
        if (!rivalsBySeg.has(idx)) rivalsBySeg.set(idx, []);
        rivalsBySeg.get(idx).push(c);
      }
      const lapNow = Math.floor(r.dist / length);
      for (let i = drawn.length - 1; i >= 0; i--) {
        const { seg, looped } = drawn[i];
        const { p1 } = seg;
        ctx.save();
        ctx.beginPath(); ctx.rect(0, 0, w, seg.clip); ctx.clip();
        for (const sp of seg.sprites) drawScenery(ctx, sp.kind, p1.sx + p1.sw * sp.offset, p1.sy, p1.scale, w);
        if (seg.gate) drawGate(ctx, p1, r.time);
        for (const p of pickups) {
          if (p.seg !== seg.index) continue;
          const key = (lapNow + (looped ? 1 : 0)) + ':' + p.seg;
          if (r.taken.has(key)) continue;
          const px = p1.sx + p1.sw * p.offset;
          const size = Math.max(4, p1.scale * 220 * w / 2);
          const py = p1.sy - size * (p.high ? 3.2 : 0.8) + Math.sin(r.time * 4 + p.seg) * size * 0.15;
          ctx.font = `${size * 1.6}px system-ui`; ctx.textAlign = 'center';
          if (p.high) { ctx.shadowColor = '#ffd86b'; ctx.shadowBlur = 14; }
          ctx.fillText('🫘', px, py);
          ctx.shadowBlur = 0;
        }
        for (const c of rivalsBySeg.get(seg.index) || []) {
          const pct = ((c.dist % length) % SEG) / SEG;
          const { p2 } = seg;
          const sc = p1.scale + (p2.scale - p1.scale) * pct;
          const cx = p1.sx + (p2.sx - p1.sx) * pct + sc * c.x * ROAD * w / 2;
          const cy = p1.sy + (p2.sy - p1.sy) * pct;
          drawLowrider(ctx, cx, cy, CAR_W * sc * w / 2, c.color, { label: sc > 0.00025 ? c.name : null });
        }
        ctx.restore();
      }

      // Player
      const pw = Math.min(w * 0.24, 230);
      const hopLift = r.hop > 0 ? Math.sin((1 - r.hop / HOP_TIME) * Math.PI) * pw * 0.45 : 0;
      const bounce = racing ? Math.sin(r.time * 30) * speedPct * 1.5 : 0;
      const tilt = (k.left ? -1 : 0) + (k.right ? 1 : 0);
      ctx.save();
      ctx.translate(w / 2, h - 14 + bounce);
      ctx.rotate(tilt * 0.03 * speedPct);
      drawLowrider(ctx, 0, 0, pw, '#f2b632', { lift: hopLift, braking: k.brake });
      ctx.restore();

      if (r.bumpFlash > 0) { ctx.fillStyle = `rgba(215,38,61,${r.bumpFlash})`; ctx.fillRect(0, 0, w, h); }

      // Overlays
      ctx.textAlign = 'center';
      if (r.phase === 'grid') {
        ctx.fillStyle = 'rgba(11,8,6,0.6)'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = '#ffd86b'; ctx.font = `900 ${Math.min(44, w / 14)}px system-ui`;
        ctx.fillText('LOWRIDER RALLY', w / 2, h * 0.38);
        ctx.fillStyle = '#f6ead0'; ctx.font = `700 ${Math.min(16, w / 34)}px system-ui`;
        ctx.fillText(`Entry ${ENTRY} cacao · ${LAPS} laps · Top 3 get paid`, w / 2, h * 0.47);
        ctx.fillText('Press START (Enter) · Space = hydraulic HOP', w / 2, h * 0.54);
      } else if (r.phase === 'countdown') {
        const n = Math.ceil(r.countdown);
        ctx.fillStyle = '#ffd86b'; ctx.font = `900 ${Math.min(120, w / 6)}px system-ui`;
        ctx.fillText(n > 0 ? String(n) : '¡YA!', w / 2, h * 0.42);
      } else if (r.phase === 'done') {
        ctx.fillStyle = 'rgba(11,8,6,0.65)'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = r.place === 1 ? '#ffd86b' : '#f6ead0';
        ctx.font = `900 ${Math.min(50, w / 12)}px system-ui`;
        ctx.fillText(r.place === 1 ? '¡CAMPEÓN!' : `FINISHED P${r.place}`, w / 2, h * 0.38);
        ctx.font = `700 ${Math.min(18, w / 30)}px system-ui`;
        ctx.fillText(`${r.time.toFixed(2)}s · prize ${r.prize} · picked up ${r.collected} cacao`, w / 2, h * 0.48);
        ctx.fillText('START to race again', w / 2, h * 0.56);
      }
      if (r.toast) {
        ctx.globalAlpha = Math.min(1, r.toast.t * 3);
        ctx.fillStyle = '#ffd86b'; ctx.font = `900 ${Math.min(30, w / 20)}px system-ui`;
        ctx.fillText(r.toast.text, w / 2, h * 0.24);
        ctx.globalAlpha = 1;
      }

      hudTimer += dt;
      if (hudTimer > 0.1) {
        hudTimer = 0;
        const ahead = r.rivals.filter((c) => c.dist > r.dist + PLAYER_Z).length;
        setHud({
          phase: r.phase,
          lap: Math.min(LAPS, Math.floor(r.dist / length) + 1),
          place: r.phase === 'done' ? r.place : ahead + 1,
          speed: Math.round(speedPct * 120),
          time: r.time,
          collected: r.collected,
          hopReady: r.hopCd <= 0,
        });
      }
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(raf);
  }, []);

  const hold = (key) => ({
    onPointerDown: (e) => { e.preventDefault(); if (key === 'gas') touchGas.current = true; else keys.current[key] = true; },
    onPointerUp: () => { if (key === 'gas') touchGas.current = false; else keys.current[key] = false; },
    onPointerLeave: () => { if (key === 'gas') touchGas.current = false; else keys.current[key] = false; },
  });

  const canStart = hud.phase === 'grid' || hud.phase === 'done';

  return (
    <ArcadeChrome title="LOWRIDER RALLY" subtitle="Aztlán Arcade · Calzada del Sol">
      <style>{`
        .lr-hud{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
        .lr-hud div{flex:1;min-width:90px;background:#0b0806cc;border:1px solid #f2b63244;border-radius:10px;padding:8px 12px}
        .lr-hud small{display:block;font-size:9px;letter-spacing:2px;color:#8a7d66}
        .lr-hud b{font-size:20px;color:#ffd86b;font-variant-numeric:tabular-nums}
        .lr-stage{border-radius:18px;overflow:hidden;border:2px solid #f2b63288;box-shadow:0 0 50px #e4007c22;background:#0b0806}
        .lr-stage canvas{display:block;width:100%;touch-action:none}
        .lr-pad{display:flex;justify-content:space-between;gap:10px;margin-top:12px;flex-wrap:wrap}
        .lr-pad .az-btn{min-width:72px;min-height:56px;justify-content:center;font-size:16px;user-select:none;-webkit-user-select:none;touch-action:none}
        @media(max-width:640px){.lr-pad>.az-btn{order:-1;flex-basis:100%}.lr-pad .az-btn{min-width:64px}}
        .lr-help{font-size:11px;color:#8a7d66;letter-spacing:1px;text-align:center;margin-top:10px}
      `}</style>
      <div className="lr-hud">
        <div><small>LAP</small><b>{hud.lap}/{LAPS}</b></div>
        <div><small>POSITION</small><b>P{hud.place}/6</b></div>
        <div><small>SPEED</small><b>{hud.speed} mph</b></div>
        <div><small>TIME</small><b>{hud.time.toFixed(1)}s</b></div>
        <div><small>PICKED UP</small><b>{hud.collected} 🫘</b></div>
      </div>
      <div className="lr-stage" ref={wrapRef}>
        <canvas ref={canvasRef} aria-label="Lowrider Rally race track" />
      </div>
      <div className="lr-pad">
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="az-btn" {...hold('left')} aria-label="Steer left">◀</button>
          <button className="az-btn" {...hold('right')} aria-label="Steer right">▶</button>
        </div>
        {canStart ? (
          <button className="az-btn primary" onClick={start}>START · {ENTRY} 🫘</button>
        ) : (
          <button className={`az-btn ${hud.hopReady ? 'hot' : ''}`} onPointerDown={(e) => { e.preventDefault(); hop(); }}>HOP</button>
        )}
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="az-btn" {...hold('brake')} aria-label="Brake">■</button>
          <button className="az-btn primary" {...hold('gas')} aria-label="Gas">GAS</button>
        </div>
      </div>
      <div className="lr-help">← → steer · ↑ gas · ↓ brake · SPACE hop over cars and grab the floating cacao · stay off the dirt</div>
    </ArcadeChrome>
  );
}
