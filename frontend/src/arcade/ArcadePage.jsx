import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { Play, ExternalLink, Maximize, Minimize, Wallet, Users, Crown, Zap, Gamepad2, Home, X } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;
const LS_BAL_KEY = 'sla_arcade_balance';
const LS_ANL_KEY = 'sla_arcade_analytics';

const TIER_STYLE = {
  MINI:  { color: '#44ff44' },
  MINOR: { color: '#00c8ff' },
  MAJOR: { color: '#d4af37' },
  GRAND: { color: '#ff2244' },
};

const logEvent = (type, meta = {}) => {
  try {
    const arr = JSON.parse(localStorage.getItem(LS_ANL_KEY) || '[]');
    arr.push({ type, meta, ts: Date.now() });
    if (arr.length > 500) arr.splice(0, arr.length - 500);
    localStorage.setItem(LS_ANL_KEY, JSON.stringify(arr));
  } catch (_) {}
};

const useBalance = () => {
  const [bal, setBal] = useState(() => parseInt(localStorage.getItem(LS_BAL_KEY) || '2500'));
  useEffect(() => { localStorage.setItem(LS_BAL_KEY, String(bal)); }, [bal]);
  return [bal, setBal];
};

export default function ArcadePage() {
  const [lobbies, setLobbies] = useState([]);
  const [sprites, setSprites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState(null);
  const [deploying, setDeploying] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [balance, setBalance] = useBalance();
  const iframeRef = useRef(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [lRes, sRes] = await Promise.all([
        axios.get(`${API}/lobbies`),
        axios.get(`${API}/sprites`),
      ]);
      setLobbies(lRes.data.lobbies || []);
      setSprites(sRes.data.sprites || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); logEvent('arcade_view'); }, [load]);

  const spriteKey = (name) => (name || '').toLowerCase().replace(/[\s,]+/g, '_');
  const bgFor = (l) => {
    const bg = sprites.find(s => spriteKey(s.name) === l.background_sprite);
    if (!bg) return null;
    return bg.sprite_url.includes('customer-assets')
      ? `${process.env.REACT_APP_BACKEND_URL}/api/sla113/sprites/proxy?url=${bg.sprite_url}`
      : bg.sprite_url;
  };

  const handlePlay = async (lobby) => {
    setDeploying(true);
    logEvent('game_open', { lobby: lobby.name });
    try {
      const res = await axios.post(`${API}/lobbies/${lobby.id}/deploy`);
      const url = `${process.env.REACT_APP_BACKEND_URL}${res.data.preview_url}`;
      setActive({ ...lobby, url });
      setBalance(b => Math.max(0, b - 5));
    } catch (e) { alert('Could not launch: ' + (e?.response?.data?.detail || e.message)); }
    setDeploying(false);
  };

  const toggleFS = async () => {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
        setFullscreen(true);
      } else {
        await document.exitFullscreen();
        setFullscreen(false);
      }
    } catch (_) {}
  };

  useEffect(() => {
    const h = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', h);
    return () => document.removeEventListener('fullscreenchange', h);
  }, []);

  if (active) return <GameView game={active} onExit={() => { setActive(null); setBalance(b => b + 50); logEvent('game_exit', { lobby: active.name }); }} fullscreen={fullscreen} onToggleFS={toggleFS} iframeRef={iframeRef} balance={balance}/>;

  return (
    <div className="min-h-screen bg-[#050008] text-white" style={{ fontFamily: "'Rajdhani','Orbitron',monospace" }} data-testid="arcade-page">
      <header className="sticky top-0 z-40 bg-gradient-to-b from-[#050008] via-[#050008f0] to-transparent border-b border-[#d4af3722] px-4 md:px-8 py-4 flex items-center justify-between gap-4 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#d4af37] to-[#8a6a1e] flex items-center justify-center shadow-[0_0_20px_rgba(212,175,55,0.4)]"><Gamepad2 size={18} className="text-black"/></div>
          <div>
            <div className="text-[9px] uppercase tracking-[3px] text-[#d4af37]">SouthernLifestyle</div>
            <div className="font-black text-lg tracking-wider">ARCADE</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 border border-[#d4af3744] bg-[#d4af3710]" data-testid="arcade-balance">
            <Wallet size={13} className="text-[#d4af37]"/>
            <span className="text-[10px] uppercase text-zinc-400">balance</span>
            <span className="font-bold text-[#d4af37] font-mono">${balance.toLocaleString()}</span>
          </div>
          <button onClick={toggleFS} className="p-2 border border-zinc-800 hover:border-[#d4af37]/50 transition-all" data-testid="arcade-fs-btn">
            {fullscreen ? <Minimize size={14}/> : <Maximize size={14}/>}
          </button>
        </div>
      </header>

      <div className="px-4 md:px-8 py-6 max-w-7xl mx-auto">
        <div className="mb-8 flex items-center gap-2 flex-wrap">
          <span className="text-[10px] uppercase tracking-[4px] text-zinc-500">GAME LIBRARY</span>
          <span className="text-[10px] text-zinc-700">·</span>
          <span className="text-[10px] uppercase tracking-[2px] text-zinc-400">{lobbies.length} Lobbies</span>
        </div>

        {loading ? (
          <div className="text-zinc-600 p-8 text-sm">Loading library…</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="arcade-lobby-grid">
            {lobbies.map(l => {
              const tier = TIER_STYLE[l.jackpot_tier] || TIER_STYLE.MAJOR;
              const bg = bgFor(l);
              const mainBoss = sprites.find(s => spriteKey(s.name) === l.main_boss_sprite);
              const partner = sprites.find(s => spriteKey(s.name) === l.partner_boss_sprite);
              return (
                <button
                  key={l.id}
                  onClick={() => handlePlay(l)}
                  disabled={deploying}
                  className="group relative overflow-hidden border border-zinc-800 hover:border-[#d4af37]/60 transition-all text-left disabled:opacity-60"
                  style={{ background: '#080008' }}
                  data-testid={`arcade-lobby-${l.id}`}
                >
                  <div className="relative h-48 overflow-hidden">
                    {bg && <img src={bg} alt={l.name} className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-85 group-hover:scale-105 transition-all duration-500"/>}
                    <div className="absolute inset-0" style={{ background: `linear-gradient(180deg, transparent 30%, rgba(0,0,0,0.6) 70%, rgba(0,0,0,0.95) 100%), radial-gradient(circle at 80% 20%, ${l.theme_color}22 0%, transparent 60%)` }}/>
                    <div className="absolute top-3 left-3 flex gap-1.5">
                      <span className="px-2 py-0.5 text-[9px] uppercase tracking-widest font-bold border bg-black/60" style={{ borderColor: tier.color, color: tier.color }}>{l.jackpot_tier}</span>
                      <span className="px-2 py-0.5 text-[9px] uppercase tracking-widest font-bold border bg-black/60" style={{ borderColor: l.theme_color, color: l.theme_color }}>${l.base_bet?.toFixed(2)}</span>
                    </div>
                    <div className="absolute bottom-3 left-4 right-4">
                      <h3 className="font-black text-xl uppercase tracking-wider drop-shadow-[0_2px_10px_rgba(0,0,0,0.9)]">{l.name}</h3>
                      <div className="text-[10px] text-zinc-300 mt-0.5 flex items-center gap-2">
                        <Crown size={10} style={{ color: l.theme_color }}/>
                        {mainBoss?.name || l.main_boss_sprite}
                        {partner && <span className="text-zinc-500">+ {partner.name}</span>}
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-3 flex items-center justify-between border-t border-zinc-900">
                    <span className="text-[10px] text-zinc-500 line-clamp-1">{l.description}</span>
                    <span className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest group-hover:text-[#d4af37] text-zinc-400 transition-colors">
                      <Play size={11}/> Play
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        )}

        <footer className="mt-12 py-6 border-t border-zinc-900 text-[10px] text-zinc-600 uppercase tracking-widest text-center flex flex-col md:flex-row items-center justify-between gap-2">
          <span>SLA113 · Arcade OS</span>
          <span>{`Session: ${(JSON.parse(localStorage.getItem(LS_ANL_KEY)||'[]')).length} events`}</span>
        </footer>
      </div>
    </div>
  );
}

function GameView({ game, onExit, fullscreen, onToggleFS, iframeRef, balance }) {
  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col" data-testid="arcade-game-view">
      <header className="shrink-0 flex items-center justify-between px-3 md:px-5 py-2 bg-black border-b border-[#d4af3744]" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
        <button onClick={onExit} className="flex items-center gap-2 px-3 py-1.5 border border-zinc-800 hover:border-red-500/50 hover:text-red-400 transition-all text-[10px] uppercase tracking-widest" data-testid="arcade-back-btn">
          <Home size={12}/> Library
        </button>
        <div className="flex items-center gap-2 text-[10px] uppercase tracking-widest">
          <span className="text-zinc-500 hidden sm:inline">Now Playing</span>
          <span className="font-bold" style={{ color: game.theme_color }}>{game.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 border border-[#d4af3744] text-[10px] font-mono">
            <Wallet size={11} className="text-[#d4af37]"/>
            <span className="text-[#d4af37]">${balance.toLocaleString()}</span>
          </div>
          <button onClick={onToggleFS} className="p-1.5 border border-zinc-800 hover:border-[#d4af37]/50" data-testid="arcade-game-fs">
            {fullscreen ? <Minimize size={13}/> : <Maximize size={13}/>}
          </button>
        </div>
      </header>
      <iframe
        ref={iframeRef}
        src={game.url}
        title={game.name}
        className="flex-1 w-full border-0"
        allow="autoplay; fullscreen; gamepad"
        data-testid="arcade-game-iframe"
      />
    </div>
  );
}
