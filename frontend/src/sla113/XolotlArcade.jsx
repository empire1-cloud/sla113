import React, { useEffect, useRef, useState } from 'react';

const TARGET_TYPES = [
  { id: 'spirit', label: 'SPIRIT', hp: 1, reward: 3, radius: 18, speed: 52, glyph: '✦', weight: 46 },
  { id: 'jaguar', label: 'JAGUAR', hp: 4, reward: 12, radius: 24, speed: 42, glyph: '◆', weight: 30 },
  { id: 'warrior', label: 'WARRIOR', hp: 10, reward: 35, radius: 30, speed: 30, glyph: '♜', weight: 17 },
  { id: 'guardian', label: 'GUARDIAN', hp: 24, reward: 100, radius: 38, speed: 22, glyph: '☼', weight: 6 },
  { id: 'xolotl', label: 'XOLOTL', hp: 80, reward: 500, radius: 52, speed: 16, glyph: '🐺', weight: 1 },
];

const rand = (min, max) => Math.random() * (max - min) + min;

function pickTarget() {
  const total = TARGET_TYPES.reduce((sum, t) => sum + t.weight, 0);
  let roll = Math.random() * total;
  for (const type of TARGET_TYPES) {
    roll -= type.weight;
    if (roll <= 0) return type;
  }
  return TARGET_TYPES[0];
}

export default function XolotlArcade() {
  const canvasRef = useRef(null);
  const wrapRef = useRef(null);
  const rafRef = useRef(null);
  const stateRef = useRef({
    width: 900,
    height: 600,
    dpr: 1,
    last: 0,
    spawn: 0,
    shots: [],
    targets: [],
    bursts: [],
    texts: [],
    pointer: { x: 450, y: 430 },
    credits: 1250,
    score: 0,
    combo: 0,
    multiplier: 1,
    shotCost: 1,
    boss: false,
    bossSpawned: false,
    running: true,
    auto: false,
    autoTimer: 0,
  });

  const [hud, setHud] = useState({
    credits: 1250,
    score: 0,
    combo: 0,
    multiplier: 1,
    shotCost: 1,
    auto: false,
    message: 'READY // FIRE',
  });

  const setMessage = (message) => setHud((h) => ({ ...h, message }));

  const syncHud = () => {
    const s = stateRef.current;
    setHud({
      credits: Math.max(0, Math.floor(s.credits)),
      score: Math.floor(s.score),
      combo: s.combo,
      multiplier: s.multiplier,
      shotCost: s.shotCost,
      auto: s.auto,
      message: s.credits < s.shotCost ? 'INSERT CREDITS' : hMessageRef.current,
    });
  };

  const hMessageRef = useRef('READY // FIRE');

  const pulseMessage = (message) => {
    hMessageRef.current = message;
    setHud((h) => ({ ...h, message }));
  };

  const resize = () => {
    const canvas = canvasRef.current;
    const wrap = wrapRef.current;
    if (!canvas || !wrap) return;
    const rect = wrap.getBoundingClientRect();
    const s = stateRef.current;
    s.width = Math.max(320, rect.width);
    s.height = Math.max(420, Math.min(rect.width * 0.67, window.innerHeight * 0.74));
    s.dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(s.width * s.dpr);
    canvas.height = Math.floor(s.height * s.dpr);
    canvas.style.width = '100%';
    canvas.style.height = s.height + 'px';
  };

  useEffect(() => {
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  const fire = (x = stateRef.current.pointer.x, y = stateRef.current.pointer.y) => {
    const s = stateRef.current;
    if (!s.running || s.credits < s.shotCost) {
      pulseMessage('INSERT CREDITS');
      return;
    }
    s.credits -= s.shotCost;
    s.shots.push({
      x: s.width / 2,
      y: s.height - 42,
      tx: x,
      ty: y,
      life: 0,
      maxLife: 0.28,
      cost: s.shotCost,
    });
    pulseMessage('HIT THE SPIRITS');
    syncHud();
  };

  const reset = () => {
    const s = stateRef.current;
    s.credits = 1250;
    s.score = 0;
    s.combo = 0;
    s.multiplier = 1;
    s.shots = [];
    s.targets = [];
    s.bursts = [];
    s.texts = [];
    s.spawn = 0;
    s.bossSpawned = false;
    s.running = true;
    pulseMessage('ROUND RESET // READY');
    syncHud();
  };

  const addCredits = (amount) => {
    const s = stateRef.current;
    s.credits += amount;
    pulseMessage('CREDIT + ' + amount);
    syncHud();
  };

  const changeShotCost = (delta) => {
    const s = stateRef.current;
    s.shotCost = Math.max(1, Math.min(10, s.shotCost + delta));
    syncHud();
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onPointerMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const s = stateRef.current;
      s.pointer.x = (e.clientX - rect.left) * (s.width / rect.width);
      s.pointer.y = (e.clientY - rect.top) * (s.height / rect.height);
    };
    const onPointerDown = (e) => {
      if (e.button !== undefined && e.button !== 0) return;
      const rect = canvas.getBoundingClientRect();
      const s = stateRef.current;
      const x = (e.clientX - rect.left) * (s.width / rect.width);
      const y = (e.clientY - rect.top) * (s.height / rect.height);
      s.pointer.x = x;
      s.pointer.y = y;
      fire(x, y);
    };
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerdown', onPointerDown);
    return () => {
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerdown', onPointerDown);
    };
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const s = stateRef.current;

    const spawnTarget = () => {
      const type = pickTarget();
      if (type.id === 'xolotl' && s.bossSpawned) return;
      const fromLeft = Math.random() > 0.5;
      s.targets.push({
        type,
        x: fromLeft ? -type.radius - 10 : s.width + type.radius + 10,
        y: rand(90, Math.max(120, s.height - 150)),
        vx: fromLeft ? type.speed : -type.speed,
        hp: type.hp,
        maxHp: type.hp,
        phase: rand(0, Math.PI * 2),
        age: 0,
        id: Math.random(),
      });
      if (type.id === 'xolotl') {
        s.bossSpawned = true;
        s.boss = true;
        pulseMessage('XOLOTL AWAKENS');
      }
    };

    const drawTemple = () => {
      const w = s.width, h = s.height;
      const g = ctx.createLinearGradient(0, 0, 0, h);
      g.addColorStop(0, '#07101a');
      g.addColorStop(0.55, '#101018');
      g.addColorStop(1, '#030303');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);

      ctx.globalAlpha = 0.32;
      ctx.fillStyle = '#d4af37';
      ctx.beginPath();
      ctx.arc(w * 0.78, h * 0.17, Math.min(w, h) * 0.09, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1;

      // Moon
      ctx.fillStyle = '#e9e3c5';
      ctx.beginPath();
      ctx.arc(w * 0.78, h * 0.16, Math.min(w, h) * 0.045, 0, Math.PI * 2);
      ctx.fill();

      // Temple silhouette
      const baseY = h * 0.63;
      ctx.fillStyle = '#151515';
      ctx.fillRect(w * 0.19, baseY, w * 0.62, h * 0.28);
      for (let i = 0; i < 7; i++) {
        const inset = i * w * 0.018;
        ctx.beginPath();
        ctx.moveTo(w * 0.23 + inset, baseY - i * 18);
        ctx.lineTo(w * 0.77 - inset, baseY - i * 18);
        ctx.lineTo(w * 0.70 - inset, baseY - i * 18 - 16);
        ctx.lineTo(w * 0.30 + inset, baseY - i * 18 - 16);
        ctx.closePath();
        ctx.fill();
      }

      ctx.strokeStyle = 'rgba(212,175,55,0.16)';
      ctx.lineWidth = 1;
      for (let x = 0; x < w; x += 46) {
        ctx.beginPath();
        ctx.moveTo(x, h * 0.2);
        ctx.lineTo(x + 24, h);
        ctx.stroke();
      }

      // Arena floor
      ctx.fillStyle = '#090909';
      ctx.fillRect(0, h * 0.77, w, h * 0.23);
      ctx.strokeStyle = 'rgba(212,175,55,0.22)';
      for (let x = 0; x < w; x += 54) {
        ctx.beginPath();
        ctx.moveTo(x, h);
        ctx.lineTo(w / 2 + (x - w / 2) * 0.25, h * 0.77);
        ctx.stroke();
      }
    };

    const drawTarget = (t) => {
      const bob = Math.sin(t.age * 4 + t.phase) * 4;
      const y = t.y + bob;
      const r = t.type.radius;
      ctx.save();
      ctx.translate(t.x, y);
      ctx.shadowBlur = t.type.id === 'xolotl' ? 28 : 16;
      ctx.shadowColor = t.type.id === 'spirit' ? '#60a5fa' : '#d4af37';
      ctx.strokeStyle = t.type.id === 'spirit' ? '#60a5fa' : '#d4af37';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.globalAlpha = 0.22;
      ctx.fillStyle = t.type.id === 'spirit' ? '#60a5fa' : '#d4af37';
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.font = `${Math.max(16, r)}px serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#f4d675';
      ctx.fillText(t.type.glyph, 0, 1);
      ctx.font = '700 8px ui-monospace, monospace';
      ctx.fillStyle = '#fff4bf';
      ctx.fillText(t.type.label, 0, r + 13);

      const barW = r * 1.7;
      ctx.fillStyle = '#220909';
      ctx.fillRect(-barW / 2, -r - 10, barW, 4);
      ctx.fillStyle = '#d4af37';
      ctx.fillRect(-barW / 2, -r - 10, barW * (t.hp / t.maxHp), 4);
      ctx.restore();
    };

    const drawCannon = () => {
      const x = s.width / 2, y = s.height - 42;
      const dx = s.pointer.x - x, dy = s.pointer.y - y;
      const angle = Math.atan2(dy, dx);
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.shadowBlur = 20;
      ctx.shadowColor = '#d4af37';
      ctx.fillStyle = '#111';
      ctx.strokeStyle = '#d4af37';
      ctx.lineWidth = 3;
      ctx.fillRect(0, -13, 70, 26);
      ctx.strokeRect(0, -13, 70, 26);
      ctx.fillStyle = '#1d1d1d';
      ctx.fillRect(12, -18, 28, 36);
      ctx.strokeRect(12, -18, 28, 36);
      ctx.restore();

      ctx.fillStyle = '#d4af37';
      ctx.beginPath();
      ctx.arc(x, y, 16, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#080808';
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fill();
    };

    const drawReticle = () => {
      const { x, y } = s.pointer;
      ctx.save();
      ctx.strokeStyle = '#f5d76e';
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.arc(x, y, 16, 0, Math.PI * 2);
      ctx.moveTo(x - 24, y); ctx.lineTo(x - 8, y);
      ctx.moveTo(x + 8, y); ctx.lineTo(x + 24, y);
      ctx.moveTo(x, y - 24); ctx.lineTo(x, y - 8);
      ctx.moveTo(x, y + 8); ctx.lineTo(x, y + 24);
      ctx.stroke();
      ctx.restore();
    };

    const tick = (now) => {
      const dt = Math.min((now - s.last) / 1000 || 0, 0.033);
      s.last = now;
      if (!s.running) return;

      s.spawn -= dt;
      if (s.spawn <= 0) {
        spawnTarget();
        s.spawn = s.boss && !s.targets.some(t => t.type.id === 'xolotl') ? 0.75 : rand(0.55, 1.15);
      }

      if (s.auto) {
        s.autoTimer -= dt;
        if (s.autoTimer <= 0) {
          fire(s.pointer.x, s.pointer.y);
          s.autoTimer = 0.13;
        }
      }

      for (const shot of s.shots) {
        shot.life += dt;
        const p = Math.min(shot.life / shot.maxLife, 1);
        shot.x = s.width / 2 + (shot.tx - s.width / 2) * p;
        shot.y = s.height - 42 + (shot.ty - (s.height - 42)) * p;
      }
      s.shots = s.shots.filter((shot) => shot.life < shot.maxLife);

      for (const t of s.targets) {
        t.age += dt;
        t.x += t.vx * dt;
        if (t.x < -100 || t.x > s.width + 100) t.dead = true;
      }

      for (const shot of s.shots) {
        if (shot.hit) continue;
        for (const t of s.targets) {
          if (t.dead) continue;
          const d = Math.hypot(shot.x - t.x, shot.y - t.y);
          if (d <= t.type.radius + 8) {
            shot.hit = true;
            t.hp -= Math.max(1, shot.cost);
            s.bursts.push({ x: t.x, y: t.y, life: 0, text: 'HIT' });
            s.texts.push({ x: t.x, y: t.y - t.type.radius, life: 0, value: '−' + shot.cost, kind: 'damage' });
            if (t.hp <= 0) {
              t.dead = true;
              const payout = t.type.reward * s.multiplier;
              s.credits += payout;
              s.score += payout * 10;
              s.combo += 1;
              s.multiplier = Math.min(10, 1 + Math.floor(s.combo / 5));
              s.texts.push({ x: t.x, y: t.y - t.type.radius - 20, life: 0, value: '+' + payout, kind: 'reward' });
              s.bursts.push({ x: t.x, y: t.y, life: 0, text: 'KILL' });
              pulseMessage(t.type.id === 'xolotl' ? 'XOLOTL DEFEATED // BONUS PAID' : 'TARGET DOWN // CREDIT PAID');
            }
            break;
          }
        }
      }

      // Near misses break the combo softly.
      for (const shot of s.shots) {
        if (shot.life >= shot.maxLife && !shot.hit) {
          s.combo = Math.max(0, s.combo - 1);
          s.multiplier = Math.max(1, 1 + Math.floor(s.combo / 5));
        }
      }

      s.targets = s.targets.filter(t => !t.dead);
      s.bursts = s.bursts.filter(b => (b.life += dt) < 0.45);
      s.texts = s.texts.filter(t => (t.life += dt) < 0.8);

      if (s.credits < s.shotCost && s.targets.length === 0) {
        s.running = false;
        pulseMessage('ROUND PAUSED // ADD CREDITS');
      }

      ctx.setTransform(s.dpr, 0, 0, s.dpr, 0, 0);
      drawTemple();

      // Projectiles
      for (const shot of s.shots) {
        ctx.fillStyle = '#f8d96b';
        ctx.shadowBlur = 14;
        ctx.shadowColor = '#f8d96b';
        ctx.beginPath();
        ctx.arc(shot.x, shot.y, 5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;

      s.targets.forEach(drawTarget);

      for (const b of s.bursts) {
        const p = b.life / 0.45;
        ctx.save();
        ctx.globalAlpha = 1 - p;
        ctx.strokeStyle = '#f8d96b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(b.x, b.y, 8 + p * 34, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      for (const t of s.texts) {
        const p = t.life / 0.8;
        ctx.save();
        ctx.globalAlpha = 1 - p;
        ctx.font = `900 ${t.kind === 'reward' ? 18 : 12}px ui-monospace, monospace`;
        ctx.textAlign = 'center';
        ctx.fillStyle = t.kind === 'reward' ? '#f8d96b' : '#fff';
        ctx.fillText(t.value, t.x, t.y - p * 35);
        ctx.restore();
      }

      drawCannon();
      drawReticle();

      if (s.boss) {
        const bossTarget = s.targets.find(t => t.type.id === 'xolotl');
        if (bossTarget) {
          ctx.fillStyle = 'rgba(0,0,0,0.75)';
          ctx.fillRect(s.width * 0.18, 16, s.width * 0.64, 30);
          ctx.strokeStyle = '#d4af37';
          ctx.strokeRect(s.width * 0.18, 16, s.width * 0.64, 30);
          ctx.fillStyle = '#d4af37';
          ctx.fillRect(s.width * 0.185, 37, s.width * 0.63 * (bossTarget.hp / bossTarget.maxHp), 4);
          ctx.fillStyle = '#fff4bf';
          ctx.font = '900 10px ui-monospace, monospace';
          ctx.textAlign = 'center';
          ctx.fillText('XOLOTL // UNDERWORLD GUARDIAN', s.width / 2, 29);
        }
      }

      if (!s.running) {
        ctx.fillStyle = 'rgba(0,0,0,0.72)';
        ctx.fillRect(0, 0, s.width, s.height);
        ctx.fillStyle = '#f8d96b';
        ctx.font = '900 22px ui-monospace, monospace';
        ctx.textAlign = 'center';
        ctx.fillText('ADD CREDITS TO CONTINUE', s.width / 2, s.height / 2);
      }

      if (now % 100 < 35) syncHud();
      rafRef.current = requestAnimationFrame(tick);
    };

    resize();
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  return (
    <div className="xolotl-arcade">
      <style>{`
        .xolotl-arcade{min-height:100vh;background:#020304;color:#f8f1d0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto}
        .xolotl-shell{width:min(1180px,100%);margin:0 auto;padding:14px}
        .xolotl-top{display:flex;align-items:center;justify-content:space-between;gap:12px;border:1px solid #3a2b10;background:linear-gradient(180deg,#100e08,#050505);padding:12px 16px;box-shadow:0 0 30px #000}
        .xolotl-brand{font-size:12px;font-weight:900;letter-spacing:4px;color:#d4af37}.xolotl-sub{font-size:8px;color:#756b4a;letter-spacing:2px;margin-top:4px}
        .xolotl-stats{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.xstat{min-width:92px;border:1px solid #2b2518;background:#070707;padding:7px 9px}.xstat b{display:block;font-size:15px;color:#f8d96b}.xstat span{font-size:7px;color:#6e6755;letter-spacing:2px}
        .xolotl-stage{margin-top:10px;border:1px solid #4a3612;background:#030404;position:relative;box-shadow:inset 0 0 50px #000,0 0 25px #000}.xolotl-stage:before{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0,transparent 3px,rgba(255,255,255,.018) 4px);z-index:2}
        .xolotl-canvas-wrap{position:relative}.xolotl-canvas{display:block;width:100%;cursor:crosshair;touch-action:none}
        .xolotl-controls{display:flex;gap:8px;align-items:center;justify-content:space-between;flex-wrap:wrap;border-top:1px solid #2b2518;background:#070707;padding:10px}
        .xbtn{border:1px solid #4a3b1c;background:#0b0b0b;color:#d8c98f;padding:9px 12px;font:800 9px ui-monospace;letter-spacing:2px;text-transform:uppercase;cursor:pointer}.xbtn:hover{border-color:#d4af37;color:#f8d96b}.xbtn.primary{background:#d4af37;color:#080706;border-color:#f8d96b}.xbtn.primary:hover{background:#f8d96b}.xbtn:disabled{opacity:.4;cursor:not-allowed}
        .xolotl-help{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:9px 2px;color:#5f5949;font-size:8px;letter-spacing:1.4px;text-transform:uppercase}
        @media(max-width:700px){.xolotl-shell{padding:6px}.xolotl-top{align-items:flex-start;flex-direction:column}.xolotl-stats{justify-content:flex-start}.xstat{min-width:74px}.xolotl-help{font-size:7px}}
      `}</style>
      <div className="xolotl-shell">
        <div className="xolotl-top">
          <div>
            <div className="xolotl-brand">SLA113 // XOLOTL</div>
            <div className="xolotl-sub">THE GOLDEN GUARDIAN // UNDERWORLD ARCADE</div>
          </div>
          <div className="xolotl-stats">
            <div className="xstat"><b>{hud.credits.toLocaleString()}</b><span>CREDIT</span></div>
            <div className="xstat"><b>{hud.score.toLocaleString()}</b><span>SCORE</span></div>
            <div className="xstat"><b>x{hud.multiplier}</b><span>MULTIPLIER</span></div>
            <div className="xstat"><b>{hud.combo}</b><span>COMBO</span></div>
          </div>
        </div>

        <div className="xolotl-stage">
          <div ref={wrapRef} className="xolotl-canvas-wrap">
            <canvas ref={canvasRef} className="xolotl-canvas" aria-label="SLA113 Xolotl arcade shooter" />
          </div>
          <div className="xolotl-controls">
            <div style={{display:'flex',gap:6,alignItems:'center',flexWrap:'wrap'}}>
              <button className="xbtn" onClick={() => changeShotCost(-1)}>− COST</button>
              <button className="xbtn primary" onClick={() => fire()}>FIRE // {hud.shotCost}</button>
              <button className="xbtn" onClick={() => changeShotCost(1)}>+ COST</button>
              <button className={`xbtn ${hud.auto ? 'primary' : ''}`} onClick={() => { stateRef.current.auto = !stateRef.current.auto; stateRef.current.running = true; syncHud(); }}>{hud.auto ? 'AUTO ON' : 'AUTO FIRE'}</button>
            </div>
            <div style={{display:'flex',gap:6,alignItems:'center',flexWrap:'wrap'}}>
              <button className="xbtn" onClick={() => addCredits(500)}>+500 CREDIT</button>
              <button className="xbtn" onClick={() => addCredits(2500)}>+2500 CREDIT</button>
              <button className="xbtn" onClick={reset}>RESET ROUND</button>
            </div>
          </div>
        </div>

        <div className="xolotl-help">
          <span>{hud.message}</span>
          <span>MOVE RETICLE • CLICK / TAP TO FIRE • VIRTUAL CREDITS ONLY</span>
          <span>SHOT COST {hud.shotCost}</span>
        </div>
      </div>
    </div>
  );
}
