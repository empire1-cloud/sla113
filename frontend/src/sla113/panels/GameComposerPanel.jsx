import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  Rocket, Play, ExternalLink, Plus, Trash2, Edit2, Swords, Skull,
  Layers, Palette, Crown, Flame, RefreshCw, Save, X
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

const spriteKey = (name) => (name || '').toLowerCase().replace(/[\s,]+/g, '_');

const TIER_STYLE = {
  MINI: { color: '#44ff44', label: 'MINI' },
  MINOR: { color: '#00c8ff', label: 'MINOR' },
  MAJOR: { color: '#d4af37', label: 'MAJOR' },
  GRAND: { color: '#ff2244', label: 'GRAND' },
};

const Badge = ({ children, color = '#d4af37' }) => (
  <span className="px-1.5 py-0.5 text-[8px] uppercase tracking-widest border font-bold"
    style={{ borderColor: `${color}55`, color, background: `${color}14` }}>{children}</span>
);

export default function GameComposerPanel() {
  const [lobbies, setLobbies] = useState([]);
  const [sprites, setSprites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deploying, setDeploying] = useState({});
  const [lastDeploy, setLastDeploy] = useState(null);
  const [editing, setEditing] = useState(null); // lobby being edited / created
  const [saving, setSaving] = useState(false);

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

  useEffect(() => { load(); }, [load]);

  const spritesByType = sprites.reduce((acc, s) => {
    (acc[s.entity_type] = acc[s.entity_type] || []).push(s);
    return acc;
  }, {});

  const bosses = spritesByType.boss || [];
  const backgrounds = spritesByType.background || [];
  const fish = spritesByType.fish || [];

  const handleDeploy = async (lobby) => {
    setDeploying(d => ({ ...d, [lobby.id]: true }));
    try {
      const res = await axios.post(`${API}/lobbies/${lobby.id}/deploy`);
      const url = `${process.env.REACT_APP_BACKEND_URL}${res.data.preview_url}`;
      setLastDeploy({ lobby_name: lobby.name, preview_url: url });
    } catch (e) {
      alert(`Deploy failed: ${e?.response?.data?.detail || e.message}`);
    }
    setDeploying(d => ({ ...d, [lobby.id]: false }));
  };

  const handleDelete = async (lobby) => {
    if (!window.confirm(`Delete lobby "${lobby.name}"?`)) return;
    try { await axios.delete(`${API}/lobbies/${lobby.id}`); load(); } catch (e) { alert(e.message); }
  };

  const handleSave = async () => {
    if (!editing) return;
    setSaving(true);
    try {
      if (editing.id) {
        await axios.patch(`${API}/lobbies/${editing.id}`, editing);
      } else {
        await axios.post(`${API}/lobbies`, editing);
      }
      setEditing(null);
      load();
    } catch (e) {
      alert(`Save failed: ${e?.response?.data?.detail || e.message}`);
    }
    setSaving(false);
  };

  const newLobby = () => setEditing({
    name: '', slug: '', game_type: 'fish_shooting',
    main_boss_sprite: '', partner_boss_sprite: '',
    background_sprite: '', theme_color: '#d4af37',
    description: '', jackpot_tier: 'MAJOR', base_bet: 0.10,
    fish_sprite: '', extra_bosses: [],
  });

  return (
    <div className="animate-in fade-in max-w-7xl mx-auto w-full space-y-6" data-testid="game-composer-panel">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-red-500 text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2">
            <Layers size={14}/> Game OS Composer
          </span>
          <span className="text-[8px] text-zinc-600 uppercase tracking-widest">Pick · Mix · Deploy</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={load} className="px-3 py-1.5 text-[9px] uppercase tracking-widest border border-zinc-800 text-zinc-400 hover:border-zinc-600 hover:text-zinc-200 transition-all flex items-center gap-2" data-testid="composer-refresh-btn">
            <RefreshCw size={11}/> Refresh
          </button>
          <button onClick={newLobby} className="px-3 py-1.5 text-[9px] uppercase tracking-widest border border-red-500/40 text-red-400 hover:bg-red-500/10 transition-all flex items-center gap-2" data-testid="composer-new-lobby-btn">
            <Plus size={11}/> New Lobby
          </button>
        </div>
      </div>

      {lastDeploy && (
        <div className="glass-panel border-emerald-500/30 p-4 flex items-center justify-between" data-testid="composer-last-deploy">
          <div>
            <div className="text-[9px] text-emerald-500 uppercase tracking-widest">Last Deploy → Live</div>
            <div className="text-zinc-200 text-sm font-bold">{lastDeploy.lobby_name}</div>
            <div className="text-[10px] text-zinc-500 font-mono truncate max-w-xl">{lastDeploy.preview_url}</div>
          </div>
          <a href={lastDeploy.preview_url} target="_blank" rel="noopener noreferrer"
             className="px-4 py-2 text-[10px] uppercase tracking-widest border border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10 flex items-center gap-2"
             data-testid="composer-open-preview-btn">
            Open Live <ExternalLink size={12}/>
          </a>
        </div>
      )}

      {loading ? (
        <div className="text-zinc-600 text-xs p-6">Loading lobbies…</div>
      ) : lobbies.length === 0 ? (
        <div className="glass-panel border-zinc-800 p-10 text-center">
          <div className="text-zinc-500 text-xs uppercase tracking-widest">No lobbies yet</div>
          <button onClick={newLobby} className="mt-4 px-4 py-2 text-[10px] uppercase tracking-widest border border-red-500/40 text-red-400 hover:bg-red-500/10 inline-flex items-center gap-2">
            <Plus size={12}/> Create First Lobby
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="composer-lobby-grid">
          {lobbies.map(l => {
            const mainBoss = bosses.find(b => spriteKey(b.name) === l.main_boss_sprite);
            const partnerBoss = bosses.find(b => spriteKey(b.name) === l.partner_boss_sprite);
            const bg = backgrounds.find(b => spriteKey(b.name) === l.background_sprite);
            const tier = TIER_STYLE[l.jackpot_tier] || TIER_STYLE.MAJOR;
            const bgUrl = bg ? (bg.sprite_url.includes('customer-assets') ? `${process.env.REACT_APP_BACKEND_URL}/api/sla113/sprites/proxy?url=${bg.sprite_url}` : bg.sprite_url) : null;
            return (
              <div key={l.id} className="glass-panel relative overflow-hidden group hover:scale-[1.015] transition-all"
                   style={{ borderColor: `${l.theme_color}44` }} data-testid={`lobby-card-${l.id}`}>
                {/* Background preview */}
                <div className="relative h-40 overflow-hidden" style={{ background: '#000' }}>
                  {bgUrl && <img src={bgUrl} alt={l.name} className="absolute inset-0 w-full h-full object-cover opacity-55 group-hover:opacity-80 transition-opacity" />}
                  <div className="absolute inset-0" style={{ background: `linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.55) 60%, rgba(0,0,0,0.95) 100%)` }}/>
                  <div className="absolute top-2 left-2 flex gap-1">
                    <Badge color={tier.color}>{tier.label}</Badge>
                    <Badge color={l.theme_color}>${l.base_bet?.toFixed(2)}</Badge>
                  </div>
                  <div className="absolute bottom-2 left-3 right-3">
                    <h3 className="text-white font-bold text-sm tracking-wider uppercase drop-shadow-lg">{l.name}</h3>
                    <div className="flex items-center gap-1.5 mt-1">
                      {mainBoss && <span className="text-[9px] text-zinc-300 flex items-center gap-1"><Skull size={9}/> {mainBoss.name}</span>}
                      {partnerBoss && <span className="text-[9px] text-zinc-400 flex items-center gap-1">+ <Skull size={9}/> {partnerBoss.name}</span>}
                    </div>
                  </div>
                </div>

                <div className="p-3 space-y-3">
                  <p className="text-[10px] text-zinc-500 line-clamp-2 leading-relaxed">{l.description || 'No description'}</p>
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex gap-1">
                      <button onClick={() => setEditing(l)} className="p-1.5 border border-zinc-800 text-zinc-500 hover:text-zinc-200 hover:border-zinc-600 transition-all" title="Edit" data-testid={`edit-lobby-${l.id}`}>
                        <Edit2 size={11}/>
                      </button>
                      <button onClick={() => handleDelete(l)} className="p-1.5 border border-zinc-800 text-zinc-500 hover:text-red-400 hover:border-red-500/50 transition-all" title="Delete" data-testid={`delete-lobby-${l.id}`}>
                        <Trash2 size={11}/>
                      </button>
                    </div>
                    <button
                      onClick={() => handleDeploy(l)}
                      disabled={deploying[l.id]}
                      className="flex-1 px-3 py-2 text-[10px] uppercase tracking-widest border font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                      style={{ borderColor: `${l.theme_color}aa`, color: l.theme_color, background: `${l.theme_color}10` }}
                      data-testid={`deploy-lobby-${l.id}`}>
                      {deploying[l.id] ? <><RefreshCw size={11} className="animate-spin"/> Deploying…</> : <><Rocket size={11}/> Build & Deploy</>}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {editing && (
        <LobbyEditor
          lobby={editing}
          bosses={bosses}
          backgrounds={backgrounds}
          fish={fish}
          onChange={setEditing}
          onSave={handleSave}
          onClose={() => setEditing(null)}
          saving={saving}
        />
      )}
    </div>
  );
}

const FIELD_LABEL = "text-[9px] text-zinc-500 uppercase tracking-widest block mb-1";
const FIELD_INPUT = "w-full bg-black/50 border border-zinc-800 px-3 py-2 text-zinc-200 text-xs font-mono focus:border-red-500/50 focus:outline-none transition-all";

function LobbyEditor({ lobby, bosses, backgrounds, fish, onChange, onSave, onClose, saving }) {
  const set = (k, v) => onChange({ ...lobby, [k]: v });
  return (
    <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-6 animate-in fade-in" data-testid="composer-editor-modal">
      <div className="glass-panel border-red-500/30 max-w-3xl w-full max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between p-4 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <Layers size={14} className="text-red-500"/>
            <span className="text-zinc-200 text-xs font-bold uppercase tracking-widest">{lobby.id ? 'Edit Lobby' : 'New Lobby'}</span>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-200" data-testid="composer-editor-close"><X size={16}/></button>
        </div>
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={FIELD_LABEL}>Name</label>
              <input className={FIELD_INPUT} value={lobby.name} onChange={e => set('name', e.target.value)} data-testid="composer-field-name"/>
            </div>
            <div>
              <label className={FIELD_LABEL}>Slug</label>
              <input className={FIELD_INPUT} value={lobby.slug} onChange={e => set('slug', e.target.value.toLowerCase().replace(/\s+/g, '_'))} data-testid="composer-field-slug"/>
            </div>
          </div>

          <div>
            <label className={FIELD_LABEL}>Description</label>
            <textarea className={FIELD_INPUT} rows={2} value={lobby.description || ''} onChange={e => set('description', e.target.value)} data-testid="composer-field-desc"/>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={FIELD_LABEL}><Swords size={10} className="inline mr-1"/>Main Boss *</label>
              <select className={FIELD_INPUT} value={lobby.main_boss_sprite || ''} onChange={e => set('main_boss_sprite', e.target.value)} data-testid="composer-field-main-boss">
                <option value="">— select —</option>
                {bosses.map(b => <option key={b.id} value={spriteKey(b.name)}>{b.name}</option>)}
              </select>
            </div>
            <div>
              <label className={FIELD_LABEL}><Skull size={10} className="inline mr-1"/>Partner Boss (optional)</label>
              <select className={FIELD_INPUT} value={lobby.partner_boss_sprite || ''} onChange={e => set('partner_boss_sprite', e.target.value || null)} data-testid="composer-field-partner-boss">
                <option value="">— solo —</option>
                {bosses.map(b => <option key={b.id} value={spriteKey(b.name)}>{b.name}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={FIELD_LABEL}><Palette size={10} className="inline mr-1"/>Background</label>
              <select className={FIELD_INPUT} value={lobby.background_sprite || ''} onChange={e => set('background_sprite', e.target.value || null)} data-testid="composer-field-bg">
                <option value="">— auto (newest) —</option>
                {backgrounds.map(b => <option key={b.id} value={spriteKey(b.name)}>{b.name}</option>)}
              </select>
            </div>
            <div>
              <label className={FIELD_LABEL}>Fish Sprite (optional)</label>
              <select className={FIELD_INPUT} value={lobby.fish_sprite || ''} onChange={e => set('fish_sprite', e.target.value || null)} data-testid="composer-field-fish">
                <option value="">— default —</option>
                {fish.map(b => <option key={b.id} value={spriteKey(b.name)}>{b.name}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className={FIELD_LABEL}><Crown size={10} className="inline mr-1"/>Jackpot Tier</label>
              <select className={FIELD_INPUT} value={lobby.jackpot_tier || 'MAJOR'} onChange={e => set('jackpot_tier', e.target.value)} data-testid="composer-field-tier">
                {Object.keys(TIER_STYLE).map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className={FIELD_LABEL}><Flame size={10} className="inline mr-1"/>Base Bet ($)</label>
              <input type="number" step="0.05" className={FIELD_INPUT} value={lobby.base_bet || 0.10} onChange={e => set('base_bet', parseFloat(e.target.value) || 0.10)} data-testid="composer-field-bet"/>
            </div>
            <div>
              <label className={FIELD_LABEL}>Theme Color</label>
              <div className="flex gap-2 items-center">
                <input type="color" value={lobby.theme_color || '#d4af37'} onChange={e => set('theme_color', e.target.value)} className="w-10 h-9 bg-black border border-zinc-800 cursor-pointer" data-testid="composer-field-color"/>
                <input className={FIELD_INPUT + " flex-1 text-[10px]"} value={lobby.theme_color || ''} onChange={e => set('theme_color', e.target.value)}/>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-4 border-t border-zinc-800">
          <button onClick={onClose} className="px-4 py-2 text-[10px] uppercase tracking-widest border border-zinc-800 text-zinc-500 hover:text-zinc-300" data-testid="composer-editor-cancel">Cancel</button>
          <button onClick={onSave} disabled={saving || !lobby.name || !lobby.main_boss_sprite} className="px-5 py-2 text-[10px] uppercase tracking-widest border border-red-500/50 text-red-400 hover:bg-red-500/10 disabled:opacity-40 flex items-center gap-2" data-testid="composer-editor-save">
            {saving ? <><RefreshCw size={11} className="animate-spin"/> Saving…</> : <><Save size={11}/> Save</>}
          </button>
        </div>
      </div>
    </div>
  );
}
