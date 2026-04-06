import { useState } from "react";
import axios from "axios";
import { Plus, Trash, FolderOpen, Eye, Cpu, Package, GameController } from "@phosphor-icons/react";
import { API, GAME_ICONS, GAME_COLORS } from "./constants";
import CreateProjectModal from "./CreateProjectModal";

const DashboardPanel = ({ projects, gameTypes, onSelect, onRefresh }) => {
  const [showCreate, setShowCreate] = useState(false);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this project?")) return;
    try {
      await axios.delete(`${API}/projects/${id}`);
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="sla-panel" data-testid="dashboard-panel">
      <div className="sla-panel-header">
        <div>
          <h2 className="sla-panel-title">GAME PROJECTS</h2>
          <p className="sla-panel-subtitle">{projects.length} projects created</p>
        </div>
        <button className="sla-btn primary" onClick={() => setShowCreate(true)} data-testid="new-project-btn">
          <Plus size={16} weight="bold" /> NEW PROJECT
        </button>
      </div>
      {projects.length === 0 ? (
        <div className="sla-empty" data-testid="empty-projects">
          <FolderOpen size={48} weight="thin" />
          <p>No projects yet</p>
          <button className="sla-btn primary" onClick={() => setShowCreate(true)}>
            <Plus size={16} weight="bold" /> CREATE YOUR FIRST GAME
          </button>
        </div>
      ) : (
        <div className="sla-projects-grid">
          {projects.map((p) => {
            const Icon = GAME_ICONS[p.game_type] || GameController;
            const color = GAME_COLORS[p.game_type] || "#facc15";
            return (
              <div key={p.id} className="sla-project-card" onClick={() => onSelect(p)} data-testid={`project-card-${p.id}`}>
                <div className="sla-project-icon" style={{ color }}><Icon size={32} weight="bold" /></div>
                <div className="sla-project-info">
                  <h4>{p.name}</h4>
                  <span className="sla-tag" style={{ borderColor: color, color }}>{p.game_type_info?.name || p.game_type}</span>
                  <p className="sla-meta">{p.theme} &middot; {p.target_platform}</p>
                </div>
                <div className="sla-project-stats">
                  <span title="Vision assets">{p.vision_assets?.length || 0} <Eye size={12} /></span>
                  <span title="Logic specs">{p.logic_specs?.length || 0} <Cpu size={12} /></span>
                  <span title="Compositions">{p.compositions?.length || 0} <Package size={12} /></span>
                </div>
                <div className="sla-project-actions">
                  <button className="sla-icon-btn danger" onClick={(e) => handleDelete(p.id, e)} data-testid={`delete-project-${p.id}`}>
                    <Trash size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
      {showCreate && <CreateProjectModal gameTypes={gameTypes} onClose={() => setShowCreate(false)} onCreate={() => onRefresh()} />}
    </div>
  );
};

export default DashboardPanel;
