import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, XCircle, Palette, SlidersHorizontal } from 'lucide-react';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

const SlotSymbolsPanel = () => {
  const [symbolSets, setSymbolSets] = useState([]);
  const [activeSet, setActiveSet] = useState(null);
  const [newSetName, setNewSetName] = useState('');
  const [editSymbols, setEditSymbols] = useState([]);
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => { fetchSets(); }, []);

  const fetchSets = async () => {
    try {
      const res = await axios.get(`${API_BASE}/slots/symbols`);
      setSymbolSets(res.data.sets || []);
    } catch {}
  };

  const addBlankSymbol = () => {
    if (editSymbols.length >= 15) return;
    setEditSymbols(prev => [...prev, { name: '', color: '#d4af37', weight: 5, payout: 5 }]);
  };

  const updateSymbol = (idx, field, value) => {
    setEditSymbols(prev => prev.map((s, i) => i === idx ? { ...s, [field]: value } : s));
  };

  const removeSymbol = (idx) => {
    setEditSymbols(prev => prev.filter((_, i) => i !== idx));
  };

  const createSet = async () => {
    if (!newSetName || editSymbols.length < 5) return;
    const valid = editSymbols.filter(s => s.name.trim());
    if (valid.length < 5) return;
    try {
      await axios.post(`${API_BASE}/slots/symbols`, { name: newSetName, symbols: valid });
      setNewSetName(''); setEditSymbols([]); setShowCreate(false);
      fetchSets();
    } catch (e) { console.error(e); }
  };

  const deleteSet = async (id) => {
    if (id === 'DEFAULT') return;
    await axios.delete(`${API_BASE}/slots/symbols/${id}`);
    if (activeSet?.id === id) setActiveSet(null);
    fetchSets();
  };

  return (
    <div className="animate-in fade-in max-w-6xl mx-auto w-full space-y-6" data-testid="slot-symbols-panel">
      <div className="flex items-center justify-between">
        <span className="text-[#D4AF37] text-[10px] font-bold uppercase tracking-[3px] flex items-center gap-2"><Palette size={14}/> Custom Reel Symbols</span>
        <button onClick={() => { setShowCreate(!showCreate); if (!showCreate && editSymbols.length === 0) { for (let i = 0; i < 7; i++) addBlankSymbol(); } }}
          className={`px-4 py-1.5 border text-[9px] uppercase tracking-widest font-bold transition-all ${showCreate ? 'border-red-500/30 text-red-400 hover:bg-red-500/10' : 'border-[#D4AF37]/30 text-[#D4AF37] hover:bg-[#D4AF37]/10'}`}
          data-testid="toggle-create-symbols"
        >
          {showCreate ? 'Cancel' : 'New Symbol Set'}
        </button>
      </div>

      {/* Create New Set */}
      {showCreate && (
        <div className="glass-panel border-[#D4AF37]/20 p-6 space-y-4">
          <input value={newSetName} onChange={e => setNewSetName(e.target.value)} placeholder="Theme name (e.g., Southern Lifestyle)..." className="input-dark focus:border-[#D4AF37] uppercase text-sm" data-testid="symbol-set-name" />
          <div className="space-y-2">
            <div className="grid grid-cols-12 gap-2 text-[8px] text-zinc-500 uppercase tracking-widest px-1">
              <span className="col-span-3">Symbol Name</span>
              <span className="col-span-2">Color</span>
              <span className="col-span-2">Weight (1-30)</span>
              <span className="col-span-2">Payout (1-100)</span>
              <span className="col-span-2">Preview</span>
              <span className="col-span-1"></span>
            </div>
            {editSymbols.map((s, i) => (
              <div key={i} className="grid grid-cols-12 gap-2 items-center" data-testid={`edit-symbol-${i}`}>
                <input value={s.name} onChange={e => updateSymbol(i, 'name', e.target.value.toUpperCase())} placeholder="LOWRIDER" className="col-span-3 bg-black border border-zinc-800 px-2 py-1.5 text-[10px] text-zinc-200 focus:outline-none focus:border-[#D4AF37] uppercase font-mono" />
                <div className="col-span-2 flex items-center gap-1">
                  <input type="color" value={s.color} onChange={e => updateSymbol(i, 'color', e.target.value)} className="w-8 h-8 bg-transparent border-0 cursor-pointer" />
                  <span className="text-[8px] text-zinc-500 font-mono">{s.color}</span>
                </div>
                <input type="number" min="1" max="30" value={s.weight} onChange={e => updateSymbol(i, 'weight', parseInt(e.target.value) || 1)} className="col-span-2 bg-black border border-zinc-800 px-2 py-1.5 text-[10px] text-zinc-200 focus:outline-none focus:border-[#D4AF37] text-center font-mono" />
                <input type="number" min="1" max="100" value={s.payout} onChange={e => updateSymbol(i, 'payout', parseInt(e.target.value) || 1)} className="col-span-2 bg-black border border-zinc-800 px-2 py-1.5 text-[10px] text-zinc-200 focus:outline-none focus:border-[#D4AF37] text-center font-mono" />
                <div className="col-span-2 flex items-center gap-2">
                  <span className="text-xs font-bold font-mono" style={{ color: s.color }}>{s.name || '?'}</span>
                  <span className="text-[7px] text-zinc-600">x{s.payout}</span>
                </div>
                <button onClick={() => removeSymbol(i)} className="col-span-1 text-zinc-600 hover:text-red-500"><XCircle size={14}/></button>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <button onClick={addBlankSymbol} disabled={editSymbols.length >= 15} className="px-4 py-2 border border-zinc-700 text-zinc-400 text-[9px] uppercase tracking-widest hover:bg-zinc-800 transition-all disabled:opacity-30">
              <Plus size={12} className="inline mr-1"/>Add Symbol
            </button>
            <button onClick={createSet} disabled={!newSetName || editSymbols.filter(s => s.name).length < 5}
              className="flex-1 py-2 border border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37] font-bold uppercase text-[10px] tracking-[2px] hover:bg-[#D4AF37] hover:text-black transition-all disabled:opacity-30"
              data-testid="save-symbol-set"
            >
              Save Symbol Set ({editSymbols.filter(s => s.name).length}/5 min)
            </button>
          </div>
        </div>
      )}

      {/* Symbol Sets */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {symbolSets.map(set => (
          <div key={set.id} onClick={() => setActiveSet(activeSet?.id === set.id ? null : set)}
            className={`glass-panel p-5 space-y-3 cursor-pointer transition-all ${activeSet?.id === set.id ? 'border-[#D4AF37]/50 bg-[#D4AF37]/5' : 'border-[#D4AF37]/20 hover:border-[#D4AF37]/30'}`}
            data-testid={`symbol-set-${set.id}`}
          >
            <div className="flex justify-between items-start">
              <div>
                <h4 className="text-zinc-200 text-xs font-bold tracking-wider">{set.name}</h4>
                <span className="text-[8px] text-zinc-500">{set.total_symbols} symbols / {set.id}</span>
              </div>
              {set.id !== 'DEFAULT' && (
                <button onClick={(e) => { e.stopPropagation(); deleteSet(set.id); }} className="text-zinc-700 hover:text-red-500"><XCircle size={12}/></button>
              )}
            </div>
            <div className="flex flex-wrap gap-1">
              {(set.symbols || []).slice(0, 8).map((s, i) => (
                <span key={i} className="px-1.5 py-0.5 text-[8px] font-bold font-mono border border-zinc-800 bg-black/50" style={{ color: s.color }}>
                  {s.name}
                </span>
              ))}
              {set.total_symbols > 8 && <span className="text-[8px] text-zinc-600">+{set.total_symbols - 8}</span>}
            </div>
          </div>
        ))}
      </div>

      {/* Active Set Detail */}
      {activeSet && (
        <div className="glass-panel border-[#D4AF37]/20 p-6 space-y-4">
          <h4 className="text-[#D4AF37] text-xs font-bold uppercase tracking-widest">{activeSet.name} — Paytable</h4>
          <div className="grid grid-cols-1 gap-1.5">
            {(activeSet.symbols || []).map((s, i) => (
              <div key={i} className="flex items-center justify-between bg-black/50 border border-zinc-800 p-3 hover:bg-white/5 transition-all">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 flex items-center justify-center border font-bold text-[10px] font-mono" style={{ color: s.color, borderColor: s.color + '40', backgroundColor: s.color + '10' }}>
                    {s.name?.substring(0, 3)}
                  </span>
                  <span className="text-zinc-200 text-xs font-bold font-mono">{s.name}</span>
                </div>
                <div className="flex items-center gap-6 text-[9px] text-zinc-400">
                  <span>Weight: <b className="text-zinc-200">{s.weight}</b></span>
                  <span>3x = <b className="text-[#D4AF37]">{s.payout}x</b> bet</span>
                  <span>5x = <b className="text-red-400">{s.payout * 5}x</b> bet</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SlotSymbolsPanel;
