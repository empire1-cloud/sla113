/**
 * SLA113App.standalone.jsx — Standalone SLA113 Operator OS
 * EVOLVED from SLA113App.jsx — routes from root instead of /sla113
 * For deployment to sla113.southernlifestyle.org
 * NO LOGIN GATE — Sovereign operator mode only (login gate removed)
 */
import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import SLA113Page from './SLA113Page';

const TITLE_IMAGE = "https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/v9jg01gi_titleScreen.jpg";

function TitleScreen({ onComplete }) {
  const [phase, setPhase] = useState('enter'); // enter -> hold -> exit
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Progress bar fills over 3.5s
    const start = Date.now();
    const duration = 3500;
    const tick = () => {
      const elapsed = Date.now() - start;
      const pct = Math.min((elapsed / duration) * 100, 100);
      setProgress(pct);
      if (pct < 100) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);

    const t1 = setTimeout(() => setPhase('hold'), 400);
    const t2 = setTimeout(() => setPhase('exit'), 3500);
    const t3 = setTimeout(() => onComplete(), 4200);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [onComplete]);

  return (
    <div
      className={`fixed inset-0 z-[9999] bg-black flex flex-col items-center justify-center overflow-hidden transition-opacity duration-700 ${
        phase === 'exit' ? 'opacity-0' : 'opacity-100'
      }`}
      data-testid="title-screen"
    >
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#D4AF37]/5 rounded-full blur-[120px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-[#8B0000]/8 rounded-full blur-[80px]" />
      </div>

      {/* Scan lines */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03]" style={{
        backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.03) 2px, rgba(255,255,255,0.03) 4px)',
      }} />

      {/* Medallion Image */}
      <div
        className={`relative transition-all duration-1000 ${
          phase === 'enter' ? 'scale-110 opacity-0' : 'scale-100 opacity-100'
        }`}
      >
        {/* Outer ring glow */}
        <div className="absolute -inset-4 rounded-full bg-[#D4AF37]/10 blur-xl animate-pulse" />

        <img
          src={TITLE_IMAGE}
          alt="Southern Lyfestyle"
          className="w-72 h-72 md:w-80 md:h-80 object-cover rounded-full relative z-10 drop-shadow-[0_0_40px_rgba(212,175,55,0.3)] border-2 border-[#D4AF37]/20"
          style={{ filter: 'contrast(1.05) brightness(1.02)' }}
          data-testid="title-medallion"
        />
      </div>

      {/* Brand text */}
      <div className={`mt-8 text-center transition-all duration-700 delay-300 ${
        phase === 'enter' ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'
      }`}>
        <h1 className="text-[#D4AF37] text-[11px] font-bold tracking-[12px] uppercase">SLA113</h1>
        <p className="text-zinc-600 text-[8px] tracking-[6px] uppercase mt-2">Operator OS // Sovereign Architecture</p>
      </div>

      {/* Loading bar */}
      <div className={`mt-10 w-64 transition-all duration-500 delay-500 ${
        phase === 'enter' ? 'opacity-0' : 'opacity-100'
      }`}>
        <div className="h-[2px] bg-zinc-900 w-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#D4AF37] to-[#F3E5AB] transition-none"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-[7px] text-zinc-700 tracking-[3px] uppercase font-mono">Initializing</span>
          <span className="text-[7px] text-[#D4AF37]/50 font-mono">{Math.round(progress)}%</span>
        </div>
      </div>

      {/* Bottom text */}
      <div className={`absolute bottom-6 text-center transition-all duration-500 delay-700 ${
        phase === 'enter' ? 'opacity-0' : 'opacity-100'
      }`}>
        <p className="text-zinc-800 text-[7px] tracking-[4px] uppercase">El Monte // SGV // Since Day One</p>
      </div>
    </div>
  );
}


const BACKEND = process.env.REACT_APP_BACKEND_URL || '';

function SLA113LoginGate({ children }) {
  const [token, setToken] = React.useState(() => localStorage.getItem('sla113_op_token'));
  const [handle, setHandle] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const r = await fetch(`${BACKEND}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle, password }),
      });
      const data = await r.json();
      if (data.token) {
        localStorage.setItem('sla113_op_token', data.token);
        setToken(data.token);
      } else {
        setError(data.detail || 'Invalid credentials');
      }
    } catch {
      setError('Connection error — try again');
    }
    setLoading(false);
  };

  if (token) return children;

  return (
    <div style={{ minHeight: '100vh', background: '#050505', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'ui-monospace, monospace' }}>
      <div style={{ width: 360, background: '#0a0a0a', border: '1px solid #1a1a1a', borderRadius: 16, padding: 40 }}>
        <div style={{ marginBottom: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 10, color: '#D4AF37', letterSpacing: '0.4em', textTransform: 'uppercase', marginBottom: 8 }}>SLA-113</div>
          <div style={{ fontSize: 22, fontWeight: 900, color: '#fff', letterSpacing: '-0.02em' }}>OPERATOR OS</div>
          <div style={{ fontSize: 9, color: '#333', marginTop: 4, letterSpacing: '0.3em', textTransform: 'uppercase' }}>Sovereign Access Required</div>
        </div>
        <form onSubmit={login}>
          <div style={{ marginBottom: 12 }}>
            <input type="text" placeholder="Handle" value={handle} onChange={e => setHandle(e.target.value)} required
              style={{ width: '100%', background: '#000', border: '1px solid #1a1a1a', color: '#fff', padding: '12px 14px', borderRadius: 8, fontSize: 13, boxSizing: 'border-box', outline: 'none' }} />
          </div>
          <div style={{ marginBottom: 20 }}>
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required
              style={{ width: '100%', background: '#000', border: '1px solid #1a1a1a', color: '#fff', padding: '12px 14px', borderRadius: 8, fontSize: 13, boxSizing: 'border-box', outline: 'none' }} />
          </div>
          {error && <div style={{ color: '#ef4444', fontSize: 12, marginBottom: 14, textAlign: 'center' }}>{error}</div>}
          <button type="submit" disabled={loading}
            style={{ width: '100%', background: '#D4AF37', color: '#000', border: 'none', borderRadius: 8, padding: '13px 0', fontWeight: 900, fontSize: 12, letterSpacing: '0.2em', textTransform: 'uppercase', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.7 : 1 }}>
            {loading ? 'Authenticating...' : 'Enter OS'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function SLA113App() {
  const [showTitle, setShowTitle] = useState(true);

  return (
    <div id="sla113-root">
      {showTitle && <TitleScreen onComplete={() => setShowTitle(false)} />}
      <Routes>
        <Route path="/" element={<SLA113Page />} />
        <Route path="/*" element={<SLA113Page />} />
      </Routes>
    </div>
  );
}
