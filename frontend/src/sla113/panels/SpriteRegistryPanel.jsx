import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { CheckCircle2, Plus, Trash2 } from 'lucide-react';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api/sla113`;

const blankEntry = {
  id: '',
  name: '',
  role: 'Boss',
  status: 'registered',
  sheetUrl: '',
  frameWidth: 256,
  frameHeight: 256,
  frames: 16,
};

const SpriteRegistryPanel = () => {
  const [sprites, setSprites] = useState([]);
  const [draft, setDraft] = useState(blankEntry);
  const [loading, setLoading] = useState(false);

  const registeredCount = useMemo(
    () => sprites.filter((s) => s.status === 'registered').length,
    [sprites]
  );

  const fetchSprites = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/sprites`);
      const payload = Array.isArray(res.data?.sprites) ? res.data.sprites : [];
      setSprites(
        payload.map((sprite) => ({
          id: sprite.id,
          name: sprite.name,
          role: sprite.role || 'Boss',
          status: sprite.status || 'registered',
          sheetUrl: sprite.sheet_url || '',
          frameWidth: sprite.frame_width || 256,
          frameHeight: sprite.frame_height || 256,
          frames: sprite.frames || 16,
        }))
      );
    } catch (error) {
      console.error('Failed to load sprite registry', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSprites();
  }, []);

  const addSprite = async () => {
    if (!draft.id.trim() || !draft.name.trim()) return;
    const normalizedId = draft.id.trim().toUpperCase().replace(/[^A-Z0-9_]/g, '_');
    if (sprites.some((s) => s.id === normalizedId)) return;
    try {
      await axios.post(`${API_BASE}/sprites`, {
        id: normalizedId,
        name: draft.name.trim(),
        role: draft.role,
        status: draft.status,
        sheet_url: draft.sheetUrl.trim(),
        frame_width: draft.frameWidth,
        frame_height: draft.frameHeight,
        frames: draft.frames,
      });
      setDraft(blankEntry);
      fetchSprites();
    } catch (error) {
      console.error('Failed to create sprite entry', error);
    }
  };

  const removeSprite = async (id) => {
    try {
      await axios.delete(`${API_BASE}/sprites/${id}`);
      fetchSprites();
    } catch (error) {
      console.error('Failed to delete sprite entry', error);
    }
  };

  return (
    <div className="animate-in fade-in max-w-6xl mx-auto w-full space-y-6" data-testid="sprite-registry-panel">
      <div className="glass-panel border border-emerald-500/20 p-5 flex items-center justify-between">
        <div>
          <h3 className="text-emerald-300 text-xs font-bold uppercase tracking-[2px]">
            Sprite Registry
          </h3>
          <p className="text-zinc-500 text-[10px] mt-1 uppercase tracking-wider">
            Manage boss spritesheets visually
          </p>
        </div>
        <div className="text-right">
          <div className="text-emerald-300 text-lg font-bold">{loading ? '...' : registeredCount}</div>
          <div className="text-zinc-500 text-[9px] uppercase tracking-wider">Registered</div>
        </div>
      </div>

      <div className="glass-panel border border-zinc-800 p-4 space-y-3">
        <div className="text-zinc-400 text-[9px] uppercase tracking-wider">Add Sprite Entry</div>
        <div className="grid grid-cols-1 md:grid-cols-6 gap-2">
          <input
            className="input-dark md:col-span-1 text-[10px] uppercase"
            placeholder="ID (JAGUAR_WARRIOR)"
            value={draft.id}
            onChange={(e) => setDraft((d) => ({ ...d, id: e.target.value }))}
          />
          <input
            className="input-dark md:col-span-1 text-[10px]"
            placeholder="Display name"
            value={draft.name}
            onChange={(e) => setDraft((d) => ({ ...d, name: e.target.value }))}
          />
          <input
            className="input-dark md:col-span-2 text-[10px]"
            placeholder="Spritesheet URL"
            value={draft.sheetUrl}
            onChange={(e) => setDraft((d) => ({ ...d, sheetUrl: e.target.value }))}
          />
          <input
            type="number"
            min="1"
            className="input-dark md:col-span-1 text-[10px]"
            placeholder="Frames"
            value={draft.frames}
            onChange={(e) => setDraft((d) => ({ ...d, frames: parseInt(e.target.value || '0', 10) || 1 }))}
          />
          <button
            onClick={addSprite}
            className="border border-emerald-500/40 text-emerald-300 text-[10px] uppercase tracking-widest font-bold px-3 py-2 hover:bg-emerald-500/10 transition-colors"
          >
            <Plus size={12} className="inline mr-1" />
            Add
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {sprites.map((sprite) => (
          <div key={sprite.id} className="glass-panel border border-zinc-800 p-4 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-zinc-200 text-xs font-bold tracking-wide">{sprite.name}</div>
                <div className="text-zinc-500 text-[9px] uppercase tracking-wider">{sprite.id}</div>
              </div>
              <button
                onClick={() => removeSprite(sprite.id)}
                className="text-zinc-600 hover:text-red-400 transition-colors"
                title="Remove sprite"
              >
                <Trash2 size={14} />
              </button>
            </div>

            <div className="text-[10px] text-zinc-400 space-y-1">
              <div>
                Status:{' '}
                <span className="text-emerald-300 uppercase font-bold tracking-wide inline-flex items-center gap-1">
                  <CheckCircle2 size={12} /> {sprite.status}
                </span>
              </div>
              <div>Role: <span className="text-zinc-200">{sprite.role}</span></div>
              <div>Frames: <span className="text-zinc-200">{sprite.frames}</span></div>
              <div className="break-all">
                Sheet URL:{' '}
                <span className="text-cyan-300">{sprite.sheetUrl || 'Not set'}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SpriteRegistryPanel;
