import { useState } from "react";
import axios from "axios";
import { Plus, Lightning, CircleNotch, GameController } from "@phosphor-icons/react";
import { API, GAME_ICONS, GAME_COLORS } from "./constants";

const CreateProjectModal = ({ gameTypes, onClose, onCreate }) => {
  const [form, setForm] = useState({ name: "", game_type: "", theme: "", target_platform: "web" });
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!form.name || !form.game_type) return;
    setCreating(true);
    try {
      const res = await axios.post(`${API}/projects`, form);
      onCreate(res.data);
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="sla-modal-overlay" onClick={onClose} data-testid="create-project-modal">
      <div className="sla-modal" onClick={(e) => e.stopPropagation()}>
        <div className="sla-modal-header">
          <h3><Plus size={20} weight="bold" /> NEW GAME PROJECT</h3>
          <button onClick={onClose} className="sla-modal-close" data-testid="modal-close-btn">&times;</button>
        </div>
        <div className="sla-modal-body">
          <label className="sla-label">PROJECT NAME</label>
          <input className="sla-input" placeholder="e.g. Neon Fish Hunt" value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })} data-testid="project-name-input" />
          <label className="sla-label">GAME TYPE</label>
          <div className="sla-game-type-grid">
            {Object.entries(gameTypes).map(([key, info]) => {
              const Icon = GAME_ICONS[key] || GameController;
              const color = GAME_COLORS[key] || "#facc15";
              return (
                <button key={key} className={`sla-game-type-card ${form.game_type === key ? "active" : ""}`}
                  onClick={() => setForm({ ...form, game_type: key })}
                  style={form.game_type === key ? { borderColor: color, color } : {}}
                  data-testid={`game-type-${key}`}>
                  <Icon size={24} weight="bold" /><span>{info.name}</span>
                </button>
              );
            })}
          </div>
          <label className="sla-label">THEME</label>
          <input className="sla-input" placeholder="cyberpunk, fantasy, ocean, space..."
            value={form.theme} onChange={(e) => setForm({ ...form, theme: e.target.value })} data-testid="project-theme-input" />
          <label className="sla-label">PLATFORM</label>
          <div className="sla-btn-group">
            {["web", "mobile", "both"].map((p) => (
              <button key={p} className={`sla-btn-sm ${form.target_platform === p ? "active" : ""}`}
                onClick={() => setForm({ ...form, target_platform: p })} data-testid={`platform-${p}`}>{p.toUpperCase()}</button>
            ))}
          </div>
        </div>
        <div className="sla-modal-footer">
          <button className="sla-btn secondary" onClick={onClose}>Cancel</button>
          <button className="sla-btn primary" onClick={handleCreate}
            disabled={!form.name || !form.game_type || creating} data-testid="create-project-submit">
            {creating ? <CircleNotch size={16} className="sla-spin" /> : <Lightning size={16} weight="fill" />}
            {creating ? "CREATING..." : "CREATE PROJECT"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateProjectModal;
