import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Users, Plus, Play, XCircle, Crosshair } from 'lucide-react';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

const FishMultiplayerPanel = () => {
  const [lobbies, setLobbies] = useState([]);
  const [lobbyName, setLobbyName] = useState('');
  const [activeLobby, setActiveLobby] = useState(null);
  const [playerName, setPlayerName] = useState('');
  const [gameState, setGameState] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const [chat, setChat] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const canvasRef = useRef(null);
  const fishRef = useRef([]);
  const playersRef = useRef([]);

  useEffect(() => {
    fetchLobbies();
    return () => { if (wsRef.current) wsRef.current.close(); };
  }, []);

  const fetchLobbies = async () => {
    try {
      const res = await axios.get(`${API_BASE}/fish/lobbies`);
      setLobbies(res.data.lobbies || []);
    } catch {}
  };

  const createLobby = async () => {
    if (!lobbyName) return;
    await axios.post(`${API_BASE}/fish/lobbies?name=${encodeURIComponent(lobbyName)}`);
    setLobbyName('');
    fetchLobbies();
  };

  const joinLobby = (lobbyId) => {
    const name = playerName || `Player_${Math.random().toString(36).slice(2,6)}`;
    const wsUrl = `${process.env.REACT_APP_BACKEND_URL.replace('https://','wss://').replace('http://','ws://')}/api/sla113/fish/play/${lobbyId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ name }));
      setConnected(true);
      setActiveLobby(lobbyId);
    };

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'init') {
        setPlayerId(data.player_id);
        fishRef.current = data.fish || [];
        playersRef.current = data.players || [];
      } else if (data.type === 'state') {
        fishRef.current = data.fish || [];
        playersRef.current = data.players || [];
      } else if (data.type === 'fish_spawn') {
        fishRef.current = [...fishRef.current, data.fish];
      } else if (data.type === 'kill') {
        fishRef.current = fishRef.current.filter(f => f.id !== data.fish_id);
        playersRef.current = playersRef.current.map(p =>
          p.id === data.player_id ? { ...p, credits: data.player_credits, kills: data.player_kills } : p
        );
        setChat(prev => [...prev.slice(-30), { player: data.player_name, text: `killed a fish! +${data.value}`, color: '#d4af37', system: true }]);
      } else if (data.type === 'hit') {
        fishRef.current = fishRef.current.map(f =>
          f.id === data.fish_id ? { ...f, hp: data.fish_hp } : f
        );
      } else if (data.type === 'player_joined') {
        playersRef.current = data.players || [];
        setChat(prev => [...prev.slice(-30), { player: data.player.name, text: 'joined the arena', color: data.player.color, system: true }]);
      } else if (data.type === 'player_left') {
        playersRef.current = playersRef.current.filter(p => p.id !== data.player_id);
        setChat(prev => [...prev.slice(-30), { player: data.name, text: 'left', color: '#666', system: true }]);
      } else if (data.type === 'chat') {
        setChat(prev => [...prev.slice(-30), data.message]);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setActiveLobby(null);
      setPlayerId(null);
    };
  };

  const shootFish = (fishId) => {
    if (wsRef.current && wsRef.current.readyState === 1) {
      wsRef.current.send(JSON.stringify({ action: 'shoot', fish_id: fishId }));
    }
  };

  const sendChat = () => {
    if (!chatInput.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({ action: 'chat', message: chatInput }));
    setChatInput('');
  };

  const leaveLobby = () => {
    if (wsRef.current) wsRef.current.close();
    setActiveLobby(null);
    setConnected(false);
    fetchLobbies();
  };

  const myPlayer = playersRef.current.find(p => p.id === playerId);

  // ─── In-Game View ───
  if (activeLobby && connected) {
    return (
      <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-4" data-testid="fish-game-active">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-cyan-400 text-[10px] font-bold uppercase tracking-[3px]">Live Arena — {activeLobby}</span>
            <span className="text-zinc-500 text-[9px]">{playersRef.current.length} players</span>
          </div>
          <button onClick={leaveLobby} className="px-4 py-1.5 border border-red-500/30 text-red-400 text-[9px] uppercase tracking-widest hover:bg-red-500/10 transition-all" data-testid="leave-lobby-btn">Leave</button>
        </div>

        <div className="grid grid-cols-12 gap-4">
          {/* Game Canvas */}
          <div className="col-span-9 border border-cyan-500/20 bg-[#001020] relative overflow-hidden" style={{ height: 450 }} data-testid="fish-arena">
            {/* Fish */}
            {fishRef.current.map(f => f.alive && (
              <div
                key={f.id}
                onClick={() => shootFish(f.id)}
                className="absolute cursor-crosshair transition-all duration-75 hover:scale-110"
                style={{ left: `${(f.x / 1200) * 100}%`, top: `${(f.y / 700) * 100}%`, transform: `translate(-50%,-50%) scaleX(${f.x > 600 ? -1 : 1})` }}
                data-testid={`fish-${f.id}`}
              >
                <div className="relative">
                  <svg width={20 + f.tier * 6} height={14 + f.tier * 4} viewBox="0 0 40 28">
                    <polygon points="38,14 2,2 8,14 2,26" fill={f.color} opacity="0.9"/>
                    <circle cx="32" cy="11" r="2.5" fill="white"/>
                    <circle cx="33" cy="11" r="1.2" fill="black"/>
                  </svg>
                  {/* HP bar */}
                  {f.hp < f.max_hp && (
                    <div className="absolute -top-2 left-0 right-0 h-1 bg-black/50 overflow-hidden">
                      <div className="h-full bg-red-500 transition-all" style={{ width: `${(f.hp / f.max_hp) * 100}%` }}/>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {/* Player cursors */}
            {playersRef.current.filter(p => p.id !== playerId).map(p => (
              <div key={p.id} className="absolute pointer-events-none" style={{ left: '50%', top: '50%' }}>
                <Crosshair size={16} style={{ color: p.color }} />
                <span className="text-[7px] ml-2" style={{ color: p.color }}>{p.name}</span>
              </div>
            ))}
          </div>

          {/* Sidebar */}
          <div className="col-span-3 space-y-3">
            {/* Scoreboard */}
            <div className="border border-cyan-500/20 bg-black/50 p-4 space-y-2">
              <h4 className="text-cyan-400 text-[9px] font-bold uppercase tracking-[3px] border-b border-cyan-500/20 pb-2">Scoreboard</h4>
              {playersRef.current.sort((a, b) => b.credits - a.credits).map(p => (
                <div key={p.id} className={`flex justify-between text-[10px] py-1 ${p.id === playerId ? 'text-white font-bold' : 'text-zinc-400'}`}>
                  <span style={{ color: p.color }}>{p.name}</span>
                  <span>{p.credits?.toLocaleString()}</span>
                </div>
              ))}
            </div>

            {/* My Stats */}
            {myPlayer && (
              <div className="border border-cyan-500/20 bg-black/50 p-4 space-y-2">
                <h4 className="text-[#D4AF37] text-[9px] font-bold uppercase tracking-[3px]">Your Stats</h4>
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="bg-black border border-zinc-800 p-2">
                    <div className="text-[#D4AF37] text-sm font-bold">{myPlayer.credits?.toLocaleString()}</div>
                    <div className="text-[7px] text-zinc-500 uppercase">Credits</div>
                  </div>
                  <div className="bg-black border border-zinc-800 p-2">
                    <div className="text-cyan-400 text-sm font-bold">{myPlayer.kills}</div>
                    <div className="text-[7px] text-zinc-500 uppercase">Kills</div>
                  </div>
                  <div className="bg-black border border-zinc-800 p-2 col-span-2">
                    <div className="text-emerald-400 text-sm font-bold">{myPlayer.ammo}/100</div>
                    <div className="text-[7px] text-zinc-500 uppercase">Ammo</div>
                  </div>
                </div>
              </div>
            )}

            {/* Chat */}
            <div className="border border-cyan-500/20 bg-black/50 p-3 space-y-2 flex flex-col" style={{ height: 180 }}>
              <h4 className="text-zinc-500 text-[8px] font-bold uppercase tracking-widest">Chat</h4>
              <div className="flex-1 overflow-y-auto space-y-1 custom-scrollbar">
                {chat.map((m, i) => (
                  <div key={i} className="text-[9px]">
                    <span style={{ color: m.color }} className="font-bold">{m.player}: </span>
                    <span className={m.system ? 'text-zinc-600 italic' : 'text-zinc-400'}>{m.text}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-1">
                <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendChat()}
                  className="flex-1 bg-black border border-zinc-800 px-2 py-1 text-[9px] text-zinc-300 focus:outline-none focus:border-cyan-500"
                  placeholder="Type..." data-testid="fish-chat-input"
                />
                <button onClick={sendChat} className="px-2 border border-cyan-500/30 text-cyan-400 text-[9px] hover:bg-cyan-500/10">Send</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ─── Lobby Browser ───
  return (
    <div className="animate-in fade-in max-w-5xl mx-auto w-full space-y-6" data-testid="fish-lobby-browser">
      <div className="flex items-center justify-between">
        <span className="text-cyan-400 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Crosshair size={14}/> Multiplayer Fish Arena</span>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Create / Join */}
        <div className="col-span-5 space-y-4">
          <div className="glass-panel border-cyan-500/20 p-6 space-y-4">
            <h3 className="text-cyan-400 text-xs font-bold uppercase tracking-widest border-b border-cyan-500/20 pb-3">Your Identity</h3>
            <input value={playerName} onChange={e => setPlayerName(e.target.value)} placeholder="Enter your name..." className="input-dark focus:border-cyan-500 uppercase" data-testid="fish-player-name" />
          </div>
          <div className="glass-panel border-cyan-500/20 p-6 space-y-4">
            <h3 className="text-cyan-400 text-xs font-bold uppercase tracking-widest border-b border-cyan-500/20 pb-3">Create Lobby</h3>
            <input value={lobbyName} onChange={e => setLobbyName(e.target.value)} placeholder="Arena name..." className="input-dark focus:border-cyan-500 uppercase" data-testid="fish-lobby-name" />
            <button onClick={createLobby} disabled={!lobbyName} className="w-full py-3 border border-cyan-500 text-black bg-cyan-500 hover:bg-cyan-300 font-bold uppercase text-[10px] tracking-[2px] transition-all disabled:opacity-30" data-testid="create-lobby-btn">
              <Plus size={14} className="inline mr-2"/>Create Arena
            </button>
          </div>
        </div>

        {/* Lobby List */}
        <div className="col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[9px] text-zinc-500 uppercase tracking-widest">Active Arenas ({lobbies.length})</span>
            <button onClick={fetchLobbies} className="text-[8px] text-cyan-400 border border-cyan-500/20 px-2 py-1 hover:bg-cyan-500/10 transition-all uppercase tracking-widest">Refresh</button>
          </div>
          {lobbies.length === 0 && (
            <div className="glass-panel border-cyan-500/10 p-12 text-center text-zinc-600 text-[10px] uppercase tracking-widest">No active arenas. Create one to start hunting.</div>
          )}
          {lobbies.map(l => (
            <div key={l.id} className="glass-panel border-cyan-500/20 p-5 flex items-center justify-between group hover:border-cyan-500/40 transition-all" data-testid={`lobby-${l.id}`}>
              <div>
                <span className="text-zinc-200 text-xs font-bold">{l.name}</span>
                <div className="flex gap-4 mt-1 text-[9px] text-zinc-500">
                  <span><Users size={10} className="inline mr-1"/>{l.players} players</span>
                  <span>{l.fish} fish</span>
                  <span className="text-zinc-700">{l.id}</span>
                </div>
              </div>
              <button onClick={() => joinLobby(l.id)} className="px-6 py-2 border border-cyan-500 bg-cyan-500/10 text-cyan-400 text-[9px] font-bold uppercase tracking-widest hover:bg-cyan-500 hover:text-black transition-all" data-testid={`join-lobby-${l.id}`}>
                <Play size={12} className="inline mr-1"/>Join
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FishMultiplayerPanel;
