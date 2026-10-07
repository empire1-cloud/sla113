import React, { useCallback, useEffect, useRef, useState } from 'react';
import ArcadeChrome, { useCacao } from './ArcadeChrome';
import { addCacao, spendCacao } from './arcadeWallet';
import { sfx } from './arcadeSfx';
import {
  SYMBOLS, STRIPS, PAYLINES, PAYTABLE, SCATTER_PAYS, WILD, SCATTER,
  spinReels, evaluateGrid, gridFromStops,
} from './slotMath';

const BETS = [10, 20, 50, 100];
const FIRST_STOP_MS = 650;
const STOP_STAGGER_MS = 260;

const CSS = `
.pds-cab{border-radius:22px;padding:14px;background:linear-gradient(180deg,#3b2410,#1b0f07);border:2px solid #f2b63288;box-shadow:0 0 60px #e4007c22,inset 0 0 30px #000}
.pds-marquee{text-align:center;padding:10px 0 14px}
.pds-marquee h1{margin:0;font-size:clamp(26px,5vw,44px);font-weight:900;letter-spacing:4px;background:linear-gradient(180deg,#fff2b8,#f2b632 50%,#a8620f);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 30px #f2b63233}
.pds-marquee p{margin:4px 0 0;font-size:11px;letter-spacing:4px;color:#1fb5a3;text-transform:uppercase}
.pds-window{position:relative;display:grid;grid-template-columns:repeat(5,1fr);gap:8px;padding:12px;border-radius:14px;background:#0b0806;border:3px solid;border-image:repeating-linear-gradient(90deg,#1fb5a3 0 14px,#f2b632 14px 28px,#d7263d 28px 42px) 3}
.pds-reel{position:relative;height:calc(3 * var(--cell));overflow:hidden;border-radius:10px;background:linear-gradient(180deg,#2a1730,#160c1c 50%,#2a1730)}
.pds-cell{height:var(--cell);display:flex;align-items:center;justify-content:center;font-size:calc(var(--cell) * .55);position:relative}
.pds-cell.win{animation:pdsPulse .7s ease-in-out infinite alternate}
.pds-cell.win:after{content:"";position:absolute;inset:4px;border-radius:10px;border:2px solid #ffd86b;box-shadow:0 0 18px #ffd86b,inset 0 0 14px #ffd86b55}
.pds-cell.wild{text-shadow:0 0 18px #ffd86b}
.pds-strip{animation:pdsSpin .22s linear infinite;filter:blur(2px)}
.pds-land{animation:pdsLand .28s cubic-bezier(.3,1.6,.6,1)}
@keyframes pdsSpin{from{transform:translateY(calc(-6 * var(--cell)))}to{transform:translateY(0)}}
@keyframes pdsLand{from{transform:translateY(-18px)}to{transform:translateY(0)}}
@keyframes pdsPulse{from{transform:scale(1)}to{transform:scale(1.08)}}
.pds-bar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:14px}
.pds-readout{display:flex;gap:8px;flex-wrap:wrap}
.pds-led{min-width:110px;background:#0b0806;border:1px solid #f2b63244;border-radius:10px;padding:8px 12px}
.pds-led small{display:block;font-size:9px;letter-spacing:2px;color:#8a7d66}
.pds-led b{font-size:20px;color:#ffd86b;font-variant-numeric:tabular-nums}
.pds-bets{display:flex;gap:6px}
.pds-bets .az-btn{min-width:52px;justify-content:center}
.pds-bets .az-btn.on{border-color:#1fb5a3;color:#1fb5a3;box-shadow:0 0 12px #1fb5a344}
.pds-spin{min-width:150px;justify-content:center;font-size:16px!important;padding:14px 22px!important}
.pds-msg{text-align:center;min-height:26px;margin-top:12px;font-weight:800;letter-spacing:2px;color:#ffd86b}
.pds-msg.big{font-size:22px;color:#ff7aa5;text-shadow:0 0 16px #e4007c}
.pds-pay{margin-top:16px;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px}
.pds-pay div{display:flex;align-items:center;gap:10px;background:#0b0806aa;border:1px solid #ffffff14;border-radius:10px;padding:8px 10px;font-size:12px}
.pds-pay span{font-size:26px}
.pds-pay em{font-style:normal;color:#8a7d66;font-size:10px;display:block;letter-spacing:1px}
@media(max-width:640px){.pds-window{gap:4px;padding:6px}.pds-led{min-width:84px}.pds-spin{width:100%}}
`;

const randomColumn = (reel) => Array.from({ length: 9 }, (_, i) => STRIPS[reel][(i * 5 + reel * 3) % STRIPS[reel].length]);

export default function PiedraDelSolSlots() {
  const cacao = useCacao();
  const [bet, setBet] = useState(BETS[0]);
  const [grid, setGrid] = useState(() => gridFromStops([0, 7, 14, 3, 10]));
  const [spinning, setSpinning] = useState([false, false, false, false, false]);
  const [result, setResult] = useState(null);
  const [lastWin, setLastWin] = useState(0);
  const [showPay, setShowPay] = useState(false);
  const [cell, setCell] = useState(96);
  const timers = useRef([]);
  const pending = useRef(0);
  const busy = spinning.some(Boolean);

  useEffect(() => {
    const fit = () => setCell(Math.max(54, Math.min(110, Math.floor((Math.min(window.innerWidth, 1180) - 120) / 5 / 1.05))));
    fit();
    window.addEventListener('resize', fit);
    return () => {
      window.removeEventListener('resize', fit);
      timers.current.forEach(clearTimeout);
      // Leaving mid-spin still pays out the already-decided result.
      if (pending.current > 0) addCacao(pending.current);
    };
  }, []);

  const spin = useCallback(() => {
    if (busy) return;
    if (!spendCacao(bet)) { setResult({ message: 'Not enough cacao — hit Refill' }); return; }
    sfx.click();
    const next = spinReels();
    const outcome = evaluateGrid(next.grid, bet);
    pending.current = outcome.total;
    setResult(null);
    setLastWin(0);
    setSpinning([true, true, true, true, true]);
    timers.current.forEach(clearTimeout);
    timers.current = [0, 1, 2, 3, 4].map((reel) => setTimeout(() => {
      sfx.reelStop(reel);
      setGrid((g) => g.map((col, i) => (i === reel ? next.grid[reel] : col)));
      setSpinning((s) => s.map((v, i) => (i === reel ? false : v)));
      if (reel === 4) {
        pending.current = 0;
        if (outcome.total > 0) {
          addCacao(outcome.total);
          sfx.win(outcome.total >= bet * 10);
        }
        setLastWin(outcome.total);
        setResult(outcome);
      }
    }, FIRST_STOP_MS + reel * STOP_STAGGER_MS));
  }, [bet, busy]);

  useEffect(() => {
    const onKey = (e) => { if (e.code === 'Space') { e.preventDefault(); spin(); } };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [spin]);

  const winCells = new Set();
  if (result && result.wins) {
    result.wins.forEach((w) => {
      for (let reel = 0; reel < w.count; reel++) winCells.add(`${reel}:${PAYLINES[w.line][reel]}`);
    });
    if (result.scatterPay > 0) grid.forEach((col, r) => col.forEach((s, row) => s === SCATTER && winCells.add(`${r}:${row}`)));
  }

  let message = busy ? '¡Gira, gira!' : 'Space or SPIN · 10 lines · wild ☀️ pays everything but 🛕';
  if (result && result.message) message = result.message;
  else if (result && result.total >= bet * 10) message = `¡TONALLI! +${result.total.toLocaleString()} CACAO`;
  else if (result && result.total > 0) {
    const top = [...result.wins].sort((a, b) => b.amount - a.amount)[0];
    message = top
      ? `+${result.total} · Line ${top.line + 1} · ${SYMBOLS[top.symbol].glyph} ×${top.count}${result.scatterPay ? ' · TEMPLO bonus' : ''}`
      : `+${result.total} · TEMPLO bonus`;
  } else if (result) message = 'Otra vez — spin again';

  return (
    <ArcadeChrome title="PIEDRA DEL SOL" subtitle="Aztlán Arcade · Reels">
      <style>{CSS}</style>
      <div className="pds-cab" style={{ '--cell': `${cell}px` }}>
        <div className="pds-marquee">
          <h1>PIEDRA DEL SOL</h1>
          <p>Five reels · ten lines · wild sun stone</p>
        </div>

        <div className="pds-window" role="img" aria-label="Slot reels">
          {grid.map((col, reel) => (
            <div className="pds-reel" key={reel}>
              {spinning[reel] ? (
                <div className="pds-strip">
                  {[...randomColumn(reel), ...randomColumn(reel)].map((s, i) => (
                    <div className="pds-cell" key={i}>{SYMBOLS[s].glyph}</div>
                  ))}
                </div>
              ) : (
                <div className="pds-land">
                  {col.map((s, row) => (
                    <div key={row} className={`pds-cell ${winCells.has(`${reel}:${row}`) ? 'win' : ''} ${s === WILD ? 'wild' : ''}`}>
                      {SYMBOLS[s].glyph}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className={`pds-msg ${result && result.total >= bet * 10 ? 'big' : ''}`}>{message}</div>

        <div className="pds-bar">
          <div className="pds-readout">
            <div className="pds-led"><small>BET</small><b>{bet}</b></div>
            <div className="pds-led"><small>WIN</small><b>{lastWin.toLocaleString()}</b></div>
          </div>
          <div className="pds-bets">
            {BETS.map((b) => (
              <button key={b} className={`az-btn ${b === bet ? 'on' : ''}`} disabled={busy} onClick={() => { sfx.click(); setBet(b); }}>{b}</button>
            ))}
          </div>
          <button className="az-btn primary pds-spin" disabled={busy || cacao < bet} onClick={spin}>
            {busy ? '…' : 'SPIN'}
          </button>
        </div>

        <div style={{ textAlign: 'center', marginTop: 12 }}>
          <button className="az-btn" onClick={() => setShowPay((v) => !v)}>{showPay ? 'Hide paytable' : 'Paytable'}</button>
        </div>
        {showPay && (
          <div className="pds-pay">
            {Object.entries(PAYTABLE).map(([sym, pays]) => (
              <div key={sym}>
                <span>{SYMBOLS[sym].glyph}</span>
                <p style={{ margin: 0 }}>{SYMBOLS[sym].name}{sym === WILD && ' · WILD'}<em>3× {pays[0]} · 4× {pays[1]} · 5× {pays[2]} (line bet)</em></p>
              </div>
            ))}
            <div>
              <span>{SYMBOLS[SCATTER].glyph}</span>
              <p style={{ margin: 0 }}>{SYMBOLS[SCATTER].name} · SCATTER<em>3× {SCATTER_PAYS[3]} · 4× {SCATTER_PAYS[4]} · 5× {SCATTER_PAYS[5]} (total bet)</em></p>
            </div>
          </div>
        )}
      </div>
    </ArcadeChrome>
  );
}
