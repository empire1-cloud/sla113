import "./SLA113Page.css";
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  GameController, Lightning, Eye, Cpu, Package, ChartBar,
  ArrowRight, CircleNotch,
} from "@phosphor-icons/react";
import { API, GAME_ICONS, GAME_COLORS } from "../components/sla113/constants";
import DashboardPanel from "../components/sla113/DashboardPanel";
import VisionPanel from "../components/sla113/VisionPanel";
import LogicPanel from "../components/sla113/LogicPanel";
import ComposerPanel from "../components/sla113/ComposerPanel";
import StatsPanel from "../components/sla113/StatsPanel";

const NAV_ITEMS = [
  { id: "dashboard", label: "DASHBOARD", icon: GameController },
  { id: "vision", label: "VISION ENGINE", icon: Eye },
  { id: "logic", label: "LOGIC ENGINE", icon: Cpu },
  { id: "composer", label: "COMPOSER", icon: Package },
  { id: "stats", label: "STATS", icon: ChartBar },
];

const SLA113Page = () => {
  const [activePanel, setActivePanel] = useState("dashboard");
  const [projects, setProjects] = useState([]);
  const [gameTypes, setGameTypes] = useState({});
  const [selectedProject, setSelectedProject] = useState(null);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchData = useCallback(async () => {
    try {
      const [projRes, typesRes, statsRes] = await Promise.all([
        axios.get(`${API}/projects`),
        axios.get(`${API}/game-types`),
        axios.get(`${API}/stats`),
      ]);
      setProjects(projRes.data.projects || []);
      setGameTypes(typesRes.data.game_types || {});
      setStats(statsRes.data || {});
    } catch (e) {
      console.error("Failed to load SLA113 data:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    setActivePanel("vision");
  };

  if (loading) {
    return (
      <div className="sla-container" data-testid="sla113-loading">
        <div className="sla-loading">
          <CircleNotch size={40} className="sla-spin" />
          <p>INITIALIZING SLA113...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="sla-container" data-testid="sla113-page">
      <aside className="sla-sidebar" data-testid="sla113-sidebar">
        <div className="sla-sidebar-brand">
          <Lightning size={28} weight="fill" className="sla-brand-icon" />
          <span className="sla-brand-text">SLA113</span>
        </div>
        <p className="sla-sidebar-subtitle">UNIVERSAL GAME STUDIO</p>

        <nav className="sla-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id}
                className={`sla-nav-item ${activePanel === item.id ? "active" : ""}`}
                onClick={() => setActivePanel(item.id)}
                data-testid={`nav-${item.id}`}>
                <Icon size={18} weight={activePanel === item.id ? "bold" : "regular"} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {selectedProject && (
          <div className="sla-sidebar-project" data-testid="sidebar-active-project">
            <span className="sla-label">ACTIVE PROJECT</span>
            <div className="sla-active-project">
              {(() => {
                const Icon = GAME_ICONS[selectedProject.game_type] || GameController;
                return <Icon size={16} style={{ color: GAME_COLORS[selectedProject.game_type] }} />;
              })()}
              <span>{selectedProject.name}</span>
            </div>
          </div>
        )}

        <button className="sla-btn-back" onClick={() => navigate("/")} data-testid="back-to-core">
          <ArrowRight size={14} style={{ transform: "rotate(180deg)" }} /> BACK TO CORE
        </button>
      </aside>

      <main className="sla-main">
        {activePanel === "dashboard" && (
          <DashboardPanel projects={projects} gameTypes={gameTypes} onSelect={handleProjectSelect} onRefresh={fetchData} />
        )}
        {activePanel === "vision" && <VisionPanel project={selectedProject} />}
        {activePanel === "logic" && <LogicPanel project={selectedProject} />}
        {activePanel === "composer" && <ComposerPanel project={selectedProject} />}
        {activePanel === "stats" && <StatsPanel stats={stats} />}
      </main>
    </div>
  );
};

export default SLA113Page;
