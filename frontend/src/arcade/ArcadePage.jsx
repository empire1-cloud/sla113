import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Play, Maximize, Minimize, Wallet, Crown, Gamepad2, Home, Volume2, VolumeX } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;
const PROXY = (u) => u?.includes('customer-assets') || u?.includes('emergentagent')
  ? `${process.env.REACT_APP_BACKEND_URL}/api/sla113/sprites/proxy?url=${u}` : u;

const LS_BAL = 'sla_arcade_balance';
const LS_ANL = 'sla_arcade_analytics';

const LOBBY_BG_URL = 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/d6oehyc3_image.png';
const LOADER_URL  = 'https://customer-assets.emergentagent.com/job_3653cf8a-8710-488d-846f-2f0428b714dd/artifacts/pi354pey_image.jpeg';

const TIER = { MINI:{c:'#44ff44'}, MINOR:{c:'#00c8ff'}, MAJOR:{c:'#d4af37'}, GRAND:{c:'#ff2244'} };

const logEvent = (type, meta = {}) => {
  try {
    const arr = JSON.parse(localStorage.getItem(LS_ANL) || '[]');
    arr.push({ type, meta, ts: Date.now() });
    if (arr.length > 500) arr.splice(0, arr.length - 500);
    localStorage.setItem(LS_ANL, JSON.stringify(arr));
  } catch (_) {}
};

const useBalance = () => {
  const [bal, setBal] = useState(() => parseInt(localStorage.getItem(LS_BAL) || '2500'));
  useEffect(() => { localStorage.setItem(LS_BAL, String(bal)); }, [bal]);
  return [bal, setBal];
};

export default function ArcadePage() {
  const [lobbies, setLobbies] = useState([]);
  const [sprites, setSprites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState(null);
  const [deploying, setDeploying] = useState(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [muted, setMuted] = useState(false);
  const [balance, setBalance] = useBalance();
  const [hovered, setHovered] = useState(null);

  const load = useCallback(async () => {
    try {
      const [lRes, sRes] = await Promise.all([axios.get(`${API}/lobbies`), axios.get(`${API}/sprites`)]);
      setLobbies(lRes.data.lobbies || []);
      setSprites(sRes.data.sprites || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, []);
  useEffect(() => { load(); logEvent('arcade_view'); }, [load]);

  const sKey = (n) => (n || '').toLowerCase().replace(/[\s,]+/g, '_');
  const handlePlay = async (lobby) => {
    setDeploying(lobby.id);
    logEvent('game_open', { lobby: lobby.name });
    try {
      const res = await axios.post(`${API}/lobbies/${lobby.id}/deploy`);
      const url = `${process.env.REACT_APP_BACKEND_URL}${res.data.preview_url}`;
      setActive({ ...lobby, url });
      setBalance(b => Math.max(0, b - 5));
    } catch (e) { alert('Launch failed: ' + (e?.response?.data?.detail || e.message)); }
    setDeploying(null);
  };

  const toggleFS = async () => {
    try {
      if (!document.fullscreenElement) { await document.documentElement.requestFullscreen(); setFullscreen(true); }
      else { await document.exitFullscreen(); setFullscreen(false); }
    } catch (_) {}
  };
  useEffect(() => {
    const h = () => setFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', h);
    return () => document.removeEventListener('fullscreenchange', h);
  }, []);

  if (active) return <GameView game={active} onExit={() => { setActive(null); setBalance(b => b + 50); logEvent('game_exit', { lobby: active.name }); }} fullscreen={fullscreen} onToggleFS={toggleFS} balance={balance}/>;

  if (loading) return <LoadingScreen/>;

  return (
    <div className="fixed inset-0 overflow-hidden bg-black text-white select-none" style={{ fontFamily: "'Rajdhani','Orbitron',monospace" }} data-testid="arcade-page">
      {/* Hero lobby mural */}
      <img src={PROXY(LOBBY_BG_URL)} alt="" className="absolute inset-0 w-full h-full object-cover"/>
      <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 0%, rgba(0,0,0,0.55) 60%, rgba(0,0,0,0.92) 100%)' }}/>

      {/* Top HUD */}
      <header className="absolute top-0 inset-x-0 z-20 flex items-center justify-between px-4 md:px-8 py-4" style={{ paddingTop: 'max(env(safe-area-inset-top), 16px)' }}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#d4af37] via-[#a57a17] to-[#3a2800] flex items-center justify-center shadow-[0_0_25px_rgba(212,175,55,0.6)] border border-[#ffd966]">
            <Gamepad2 size={18} className="text-black"/>
          </div>
          <div>
            <div className="text-[9px] uppercase tracking-[4px] text-[#d4af37] drop-shadow">IELA · Barrio</div>
            <div className="font-black text-lg tracking-[3px] italic" style={{ fontFamily: '"Dancing Script", cursive' }}>Southern Lyfestyle</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden md:flex items-center gap-2 px-4 py-2 border border-[#d4af3755] bg-black/70 backdrop-blur-sm" data-testid="arcade-balance">
            <Wallet size={13} className="text-[#d4af37]"/>
            <span className="text-[9px] uppercase text-zinc-500 tracking-widest">balance</span>
            <span className="font-bold text-[#ffd966] font-mono text-sm">${balance.toLocaleString()}</span>
          </div>
          <button onClick={() => setMuted(m => !m)} className="p-2 border border-[#d4af3744] bg-black/70 text-[#d4af37] hover:bg-[#d4af3722] backdrop-blur-sm" data-testid="arcade-mute-btn">
            {muted ? <VolumeX size={14}/> : <Volume2 size={14}/>}
          </button>
          <button onClick={toggleFS} className="p-2 border border-[#d4af3744] bg-black/70 text-[#d4af37] hover:bg-[#d4af3722] backdrop-blur-sm" data-testid="arcade-fs-btn">
            {fullscreen ? <Minimize size={14}/> : <Maximize size={14}/>}
          </button>
        </div>
      </header>

      {/* Tagline */}
      <div className="absolute top-24 inset-x-0 z-10 text-center pointer-events-none">
        <p className="text-[11px] uppercase tracking-[8px] text-[#d4af37] drop-shadow-[0_0_10px_rgba(212,175,55,0.6)]">Members · Roll In · Pick Your Ride</p>
      </div>

      {/* Game carousel — integrated into scene */}
      <div className="absolute bottom-0 inset-x-0 z-20 pb-6 md:pb-10 px-3 md:px-8" style={{ paddingBottom: 'max(env(safe-area-inset-bottom), 24px)' }}>
        <div className="flex items-end justify-between mb-3 md:mb-5 px-2">
          <div>
            <div className="text-[9px] uppercase tracking-[5px] text-[#d4af37]/70">Choose Your Table</div>
            <div className="text-xl md:text-3xl font-black italic" style={{ fontFamily: '"Dancing Script", cursive', color: '#ffd966', textShadow: '0 0 20px rgba(212,175,55,0.5)' }}>
              {hovered ? hovered.name : 'The House'}
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <div className="text-[9px] uppercase tracking-[3px] text-zinc-500">Lobbies</div>
            <div className="text-xl font-bold text-[#d4af37] font-mono">{String(lobbies.length).padStart(2,'0')}</div>
          </div>
        </div>

        <div className="flex gap-3 md:gap-4 overflow-x-auto pb-2 snap-x snap-mandatory" style={{ scrollbarWidth: 'none' }} data-testid="arcade-lobby-row">
          <style>{`.snap-x::-webkit-scrollbar{display:none}`}</style>
          {lobbies.map(l => {
            const tier = TIER[l.jackpot_tier] || TIER.MAJOR;
            const bg = sprites.find(s => sKey(s.name) === l.background_sprite);
            const mainBoss = sprites.find(s => sKey(s.name) === l.main_boss_sprite);
            const partner = sprites.find(s => sKey(s.name) === l.partner_boss_sprite);
            const isDeploying = deploying === l.id;
            return (
              <button
                key={l.id}
                onClick={() => handlePlay(l)}
                onMouseEnter={() => setHovered(l)}
                onMouseLeave={() => setHovered(null)}
                disabled={isDeploying}
                className="relative shrink-0 w-60 md:w-72 aspect-[4/5] overflow-hidden snap-center group transition-all duration-300 hover:scale-[1.04] disabled:opacity-60"
                style={{ background: '#0a0008', boxShadow: `0 0 0 2px ${l.theme_color}55, 0 12px 40px rgba(0,0,0,0.7), 0 0 30px ${l.theme_color}30` }}
                data-testid={`arcade-lobby-${l.id}`}>

                {bg && <img src={PROXY(bg.sprite_url)} alt="" className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:opacity-90 transition-opacity"/>}
                <div className="absolute inset-0" style={{ background: `linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.7) 65%, rgba(0,0,0,0.97) 100%), radial-gradient(circle at 50% 30%, ${l.theme_color}30 0%, transparent 60%)` }}/>

                {/* Neon frame animation */}
                <div className="absolute inset-[6px] border group-hover:border-[3px] transition-all duration-300 pointer-events-none" style={{ borderColor: l.theme_color, boxShadow: `inset 0 0 20px ${l.theme_color}66` }}/>

                {/* Tier chip */}
                <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 bg-black/80 backdrop-blur-sm border" style={{ borderColor: tier.c }}>
                  <span className="w-1.5 h-1.5 rounded-full" style={{ background: tier.c, boxShadow: `0 0 8px ${tier.c}` }}/>
                  <span className="text-[9px] font-bold uppercase tracking-widest" style={{ color: tier.c }}>{l.jackpot_tier}</span>
                </div>
                <div className="absolute top-3 right-3 px-2 py-0.5 bg-black/80 border text-[9px] font-bold font-mono" style={{ borderColor: l.theme_color, color: l.theme_color }}>
                  ${l.base_bet?.toFixed(2)}
                </div>

                {/* Boss reveal on hover */}
                {mainBoss && (
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-80 transition-opacity duration-500 pointer-events-none">
                    <img src={PROXY(mainBoss.sprite_url)} alt="" className="max-h-[60%] max-w-[80%] object-contain drop-shadow-[0_0_30px_rgba(0,0,0,0.9)]"/>
                  </div>
                )}

                {/* Title + action */}
                <div className="absolute bottom-0 inset-x-0 p-4 flex flex-col gap-1.5">
                  <h3 className="font-black text-lg md:text-xl uppercase leading-tight tracking-wider drop-shadow-[0_2px_10px_rgba(0,0,0,0.95)]" style={{ textShadow: `0 0 20px ${l.theme_color}99` }}>{l.name}</h3>
                  <div className="text-[10px] text-zinc-300 flex items-center gap-1.5 drop-shadow">
                    <Crown size={10} style={{ color: l.theme_color }}/>
                    {mainBoss?.name || l.main_boss_sprite}
                    {partner && <span className="text-zinc-500 text-[9px]">· +{partner.name}</span>}
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-2">
                    <span className="flex-1 py-2 text-center text-[10px] uppercase tracking-[3px] font-black transition-all" style={{ border: `1.5px solid ${l.theme_color}`, color: l.theme_color, background: isDeploying ? `${l.theme_color}22` : 'transparent' }}>
                      {isDeploying ? 'LAUNCHING…' : <><Play size={10} className="inline mr-1"/> ROLL IN</>}
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="absolute bottom-2 right-4 z-10 text-[9px] text-zinc-600 uppercase tracking-widest pointer-events-none hidden md:block">
        SLA113 · IELA · {(JSON.parse(localStorage.getItem(LS_ANL)||'[]')).length} events
      </div>
    </div>
  );
}

function LoadingScreen() {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50" data-testid="arcade-loading">
      <img src={PROXY(LOADER_URL)} alt="Loading" className="absolute inset-0 w-full h-full object-cover opacity-85"/>
      <div className="absolute inset-0 bg-black/35"/>
      <div className="relative flex flex-col items-center gap-6 px-6 text-center">
        <div className="w-48 md:w-64 h-[3px] bg-black/60 overflow-hidden">
          <div className="h-full w-1/2 bg-gradient-to-r from-transparent via-[#d4af37] to-transparent animate-[slide_1.4s_ease-in-out_infinite]"/>
        </div>
        <p className="text-[10px] uppercase tracking-[6px] text-[#ffd966]/80 italic" style={{ fontFamily: '"Dancing Script", cursive' }}>Loading the barrio…</p>
      </div>
      <style>{`@keyframes slide{0%{transform:translateX(-100%)}100%{transform:translateX(200%)}}`}</style>
    </div>
  );
}

function GameView({ game, onExit, fullscreen, onToggleFS, balance }) {
  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col" data-testid="arcade-game-view">
      <header className="shrink-0 flex items-center justify-between px-3 md:px-5 py-2 bg-black/90 border-b border-[#d4af3744]" style={{ paddingTop: 'env(safe-area-inset-top)' }}>
        <button onClick={onExit} className="flex items-center gap-2 px-3 py-1.5 border border-zinc-800 hover:border-[#d4af37]/50 hover:text-[#d4af37] transition-all text-[10px] uppercase tracking-widest" data-testid="arcade-back-btn">
          <Home size={12}/> Lobby
        </button>
        <div className="text-[10px] uppercase tracking-widest italic" style={{ color: game.theme_color, fontFamily: '"Dancing Script", cursive' }}>{game.name}</div>
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 px-2 py-1 border border-[#d4af3744] text-[10px] font-mono">
            <Wallet size={11} className="text-[#d4af37]"/>
            <span className="text-[#ffd966]">${balance.toLocaleString()}</span>
          </div>
          <button onClick={onToggleFS} className="p-1.5 border border-[#d4af3744] hover:border-[#d4af37]/70" data-testid="arcade-game-fs">
            {fullscreen ? <Minimize size={13}/> : <Maximize size={13}/>}
          </button>
        </div>
      </header>
      <iframe src={game.url} title={game.name} className="flex-1 w-full border-0" allow="autoplay; fullscreen; gamepad" data-testid="arcade-game-iframe"/>
    </div>
  );
}
