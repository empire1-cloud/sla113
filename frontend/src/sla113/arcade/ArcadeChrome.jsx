import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getCacao, subscribeCacao, refillCacao, REFILL_FLOOR } from './arcadeWallet';
import { isMuted, setMuted } from './arcadeSfx';

/** Shared Southern Lifestyle Arcade palette: obsidian, jade, gold, chile red, rosa mexicano. */
export const ARCADE_CSS = `
.aztlan{--obsidian:#0b0806;--night:#140d1f;--jade:#1fb5a3;--gold:#f2b632;--gold-hi:#ffd86b;--chile:#d7263d;--rosa:#e4007c;--marigold:#ff9f1c;--bone:#f6ead0;--dim:#8a7d66;
  min-height:100vh;background:radial-gradient(ellipse at 50% -10%,#3a1430 0%,#140d1f 45%,#0b0806 100%);color:var(--bone);
  font-family:ui-rounded,'Trebuchet MS',system-ui,sans-serif;overflow-x:hidden}
.aztlan *{box-sizing:border-box}
.az-shell{width:min(1180px,100%);margin:0 auto;padding:0 16px 32px}
.az-picado{height:34px;display:flex;overflow:hidden;filter:drop-shadow(0 4px 6px #0008)}
.az-picado span{flex:1;min-width:46px;clip-path:polygon(0 0,100% 0,100% 70%,85% 100%,70% 70%,50% 100%,30% 70%,15% 100%,0 70%);
  -webkit-mask:radial-gradient(circle at 50% 38%,transparent 5px,#000 6px);mask:radial-gradient(circle at 50% 38%,transparent 5px,#000 6px);margin:0 2px}
.az-top{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 0;flex-wrap:wrap}
.az-brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit}
.az-brand b{font-size:20px;font-weight:900;letter-spacing:3px;background:linear-gradient(180deg,var(--gold-hi),var(--gold) 55%,#b9771b);-webkit-background-clip:text;background-clip:text;color:transparent}
.az-brand small{display:block;font-size:10px;letter-spacing:3px;color:var(--dim);text-transform:uppercase}
.az-wallet{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.az-cacao{display:flex;align-items:center;gap:8px;border:1px solid #f2b63255;background:#0b0806cc;border-radius:999px;padding:6px 14px 6px 8px}
.az-cacao i{font-style:normal;font-size:20px}.az-cacao b{font-size:18px;color:var(--gold-hi);font-variant-numeric:tabular-nums}
.az-cacao small{font-size:9px;letter-spacing:2px;color:var(--dim)}
.az-btn{border:1px solid #f2b63266;background:#1a1222;color:var(--bone);border-radius:10px;padding:10px 14px;font:800 12px/1 inherit;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:6px;min-height:40px}
.az-btn:hover{border-color:var(--gold);color:var(--gold-hi)}
.az-btn.primary{background:linear-gradient(180deg,var(--gold-hi),var(--gold));color:#2a1405;border-color:var(--gold-hi);box-shadow:0 0 20px #f2b63244}
.az-btn.hot{background:linear-gradient(180deg,#ff3d6e,var(--rosa));color:#fff;border-color:#ff7aa5}
.az-btn:disabled{opacity:.45;cursor:not-allowed}
.az-note{font-size:10px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;text-align:center;margin-top:18px}
@media(max-width:640px){.az-shell{padding:0 10px 24px}.az-brand b{font-size:16px}}
`;

const PICADO = ['#e4007c', '#ff9f1c', '#1fb5a3', '#f2b632', '#d7263d', '#7b2cbf'];

export function PapelPicado({ count = 18 }) {
  return (
    <div className="az-picado" aria-hidden="true">
      {Array.from({ length: count }, (_, i) => <span key={i} style={{ background: PICADO[i % PICADO.length] }} />)}
    </div>
  );
}

export function useCacao() {
  const [cacao, setCacao] = useState(getCacao());
  useEffect(() => subscribeCacao(setCacao), []);
  return cacao;
}

export default function ArcadeChrome({ title, subtitle, children }) {
  const cacao = useCacao();
  const [muted, setMute] = useState(isMuted());
  return (
    <div className="aztlan">
      <style>{ARCADE_CSS}</style>
      <PapelPicado />
      <div className="az-shell">
        <div className="az-top">
          <Link to="/sla113/arcade" className="az-brand">
            <span style={{ fontSize: 30 }}>☀️</span>
            <span><b>{title || 'SOUTHERN LIFESTYLE ARCADE'}</b><small>{subtitle || 'Fish · Spin · Ride'}</small></span>
          </Link>
          <div className="az-wallet">
            <div className="az-cacao" title="Cacao — virtual play credits, no cash value">
              <i>🫘</i><b>{cacao.toLocaleString()}</b><small>CACAO</small>
            </div>
            {cacao < REFILL_FLOOR && <button className="az-btn hot" onClick={refillCacao}>Refill</button>}
            <button className="az-btn" onClick={() => { setMuted(!muted); setMute(!muted); }} aria-label="Toggle sound">{muted ? '🔇' : '🔊'}</button>
            {title && <Link className="az-btn" to="/sla113/arcade">← Lobby</Link>}
          </div>
        </div>
        {children}
        <div className="az-note">Cacao are virtual play credits · no purchase · no cash value · no prizes</div>
      </div>
    </div>
  );
}
