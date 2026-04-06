import { ChartBar, GameController } from "@phosphor-icons/react";
import { GAME_ICONS, GAME_COLORS } from "./constants";

const StatsPanel = ({ stats }) => (
  <div className="sla-panel" data-testid="stats-panel">
    <div className="sla-panel-header">
      <h2 className="sla-panel-title"><ChartBar size={24} weight="bold" /> STATS</h2>
    </div>
    <div className="sla-stats-grid">
      <div className="sla-stat-card">
        <span className="sla-stat-value">{stats.total_projects || 0}</span>
        <span className="sla-stat-label">TOTAL PROJECTS</span>
      </div>
      <div className="sla-stat-card">
        <span className="sla-stat-value">{stats.supported_game_types || 0}</span>
        <span className="sla-stat-label">GAME TYPES</span>
      </div>
      <div className="sla-stat-card">
        <span className="sla-stat-value">{stats.engines?.length || 0}</span>
        <span className="sla-stat-label">AI ENGINES</span>
      </div>
      <div className="sla-stat-card">
        <span className="sla-stat-value">v{stats.version || "1.0.0"}</span>
        <span className="sla-stat-label">VERSION</span>
      </div>
    </div>
    {Object.keys(stats.by_game_type || {}).length > 0 && (
      <div className="sla-type-breakdown">
        <h4 className="sla-label">PROJECTS BY TYPE</h4>
        {Object.entries(stats.by_game_type).map(([type, count]) => {
          const Icon = GAME_ICONS[type] || GameController;
          const color = GAME_COLORS[type] || "#facc15";
          return (
            <div key={type} className="sla-type-row">
              <Icon size={16} style={{ color }} />
              <span>{type.replace("_", " ")}</span>
              <span className="sla-type-count">{count}</span>
            </div>
          );
        })}
      </div>
    )}
  </div>
);

export default StatsPanel;
