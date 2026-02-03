import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useArcade, CANONS } from "../context/ArcadeContext";
import MachineModal from "../components/MachineModal";
import "../styles/Arcade.css";

const CanonRoom = () => {
  const { canonId } = useParams();
  const { tokens, jackpotPool, currentCanon, setCurrentCanon } = useArcade();
  const [selectedMachine, setSelectedMachine] = useState(null);

  const canon = CANONS[canonId];

  if (!canon) {
    return (
      <div className="arcade-container">
        <div className="error-state">
          <h2>Canon Not Found</h2>
          <Link to="/arcade">← Back to Arcade</Link>
        </div>
      </div>
    );
  }

  // Set current canon when entering room
  if (currentCanon !== canonId) {
    setCurrentCanon(canonId);
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "Easy": return "#4caf50";
      case "Medium": return "#ff9800";
      case "Hard": return "#f44336";
      case "Expert": return "#9c27b0";
      default: return "#666";
    }
  };

  return (
    <div 
      className="arcade-container canon-room" 
      data-canon={canonId}
      style={{
        '--canon-primary': canon.colors.primary,
        '--canon-secondary': canon.colors.secondary,
        '--canon-accent': canon.colors.accent,
        '--canon-bg': canon.colors.bg,
        '--canon-text': canon.colors.text,
        '--canon-neon': canon.colors.neon
      }}
      data-testid={`canon-room-${canonId}`}
    >
      {/* Canon-specific background */}
      <div className="canon-room-bg"></div>
      <div className="arcade-grid-bg"></div>

      {/* Header */}
      <header className="arcade-header">
        <div className="arcade-header-left">
          <Link to="/arcade" className="arcade-back">← Back to Hub</Link>
          <h1 className="arcade-title">
            <span className="canon-room-title">
              <span className="canon-icon-large">{canon.icon}</span>
              <span className="neon-text">{canon.name.toUpperCase()} ROOM</span>
            </span>
          </h1>
        </div>
        <div className="arcade-header-right">
          <div className="token-display">
            <span className="token-icon">🪙</span>
            <span className="token-amount">{tokens.toLocaleString()}</span>
          </div>
          <div className="multiplier-display">
            <span className="mult-icon">⚡</span>
            <span className="mult-value">{canon.multiplier}x</span>
          </div>
        </div>
      </header>

      {/* Canon Description */}
      <section className="canon-description">
        <p>{canon.description}</p>
        <div className="canon-stats">
          <div className="stat">
            <span className="stat-value">{canon.machines.length}</span>
            <span className="stat-label">Machines</span>
          </div>
          <div className="stat">
            <span className="stat-value">{canon.multiplier}x</span>
            <span className="stat-label">Multiplier</span>
          </div>
          <div className="stat">
            <span className="stat-value">{Math.floor(jackpotPool * canon.multiplier).toLocaleString()}</span>
            <span className="stat-label">Canon Jackpot</span>
          </div>
        </div>
      </section>

      {/* Machines Grid */}
      <section className="machines-section">
        <h2 className="section-title neon-text">MACHINES</h2>
        <div className="machines-grid" data-testid="machines-grid">
          {canon.machines.map(machine => (
            <div 
              key={machine.id}
              className="machine-card"
              onClick={() => setSelectedMachine(machine)}
              data-testid={`machine-${machine.id}`}
            >
              <div className="machine-card-art">
                <span className="machine-icon-large">{machine.icon}</span>
                <div className="machine-glow"></div>
              </div>
              <div className="machine-card-content">
                <h3 className="machine-name">{machine.name}</h3>
                <p className="machine-desc">{machine.desc}</p>
                <div className="machine-meta">
                  <span 
                    className="machine-difficulty"
                    style={{ color: getDifficultyColor(machine.difficulty) }}
                  >
                    {machine.difficulty}
                  </span>
                  <span className="machine-cost">
                    <span className="cost-icon">🪙</span>
                    {machine.cost}
                  </span>
                </div>
              </div>
              <button className="play-btn" data-testid={`play-${machine.id}`}>
                ▶ PLAY
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Canon Selector (mini) */}
      <section className="canon-switcher">
        <h3>Switch Canon</h3>
        <div className="canon-mini-selector">
          {Object.values(CANONS).map(c => (
            <Link
              key={c.id}
              to={`/arcade/${c.id}`}
              className={`canon-mini-btn ${c.id === canonId ? 'active' : ''}`}
              style={{ '--canon-color': c.colors.primary }}
            >
              {c.icon}
            </Link>
          ))}
        </div>
      </section>

      {/* Machine Modal */}
      {selectedMachine && (
        <MachineModal
          machine={selectedMachine}
          canon={canon}
          onClose={() => setSelectedMachine(null)}
        />
      )}
    </div>
  );
};

export default CanonRoom;
