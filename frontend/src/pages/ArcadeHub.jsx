import { Link } from "react-router-dom";
import { useArcade, CANONS } from "../context/ArcadeContext";
import "../styles/Arcade.css";

const ArcadeHub = () => {
  const { 
    tokens, 
    jackpotPool, 
    recentJackpots, 
    currentCanon, 
    setCurrentCanon,
    canonData,
    sessions 
  } = useArcade();

  const featuredMachines = Object.values(CANONS)
    .flatMap(canon => canon.machines.slice(0, 1).map(m => ({ ...m, canon: canon.id, canonName: canon.name })))
    .slice(0, 6);

  return (
    <div className="arcade-container" data-canon={currentCanon} data-testid="arcade-hub">
      {/* Retro Grid Background */}
      <div className="arcade-grid-bg"></div>
      
      {/* Header */}
      <header className="arcade-header">
        <div className="arcade-header-left">
          <Link to="/" className="arcade-back">← Exit Arcade</Link>
          <h1 className="arcade-title">
            <span className="neon-text">AI ARCADE</span>
          </h1>
        </div>
        <div className="arcade-header-right">
          <div className="token-display" data-testid="token-balance">
            <span className="token-icon">🪙</span>
            <span className="token-amount">{tokens.toLocaleString()}</span>
            <span className="token-label">TOKENS</span>
          </div>
          <div className="jackpot-display" data-testid="jackpot-pool">
            <span className="jackpot-icon">💎</span>
            <span className="jackpot-amount">{jackpotPool.toLocaleString()}</span>
            <span className="jackpot-label">JACKPOT</span>
          </div>
        </div>
      </header>

      {/* Canon Selector */}
      <section className="canon-selector-section">
        <h2 className="section-title neon-text">SELECT YOUR CANON</h2>
        <div className="canon-selector" data-testid="canon-selector">
          {Object.values(CANONS).map(canon => (
            <button
              key={canon.id}
              className={`canon-btn ${currentCanon === canon.id ? 'active' : ''}`}
              onClick={() => setCurrentCanon(canon.id)}
              style={{ 
                '--canon-color': canon.colors.primary,
                '--canon-neon': canon.colors.neon 
              }}
              data-testid={`canon-btn-${canon.id}`}
            >
              <span className="canon-icon">{canon.icon}</span>
              <span className="canon-name">{canon.name}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Current Canon Room Link */}
      <section className="current-canon-section">
        <Link 
          to={`/arcade/${currentCanon}`} 
          className="canon-room-link"
          style={{ '--canon-color': canonData.colors.primary }}
          data-testid="enter-canon-room"
        >
          <div className="canon-room-preview">
            <span className="canon-room-icon">{canonData.icon}</span>
            <div className="canon-room-info">
              <h3>{canonData.name} Room</h3>
              <p>{canonData.description}</p>
              <span className="multiplier-badge">{canonData.multiplier}x Multiplier</span>
            </div>
          </div>
          <span className="enter-arrow">→</span>
        </Link>
      </section>

      {/* Featured Machines */}
      <section className="featured-section">
        <h2 className="section-title neon-text">FEATURED MACHINES</h2>
        <div className="featured-grid" data-testid="featured-machines">
          {featuredMachines.map(machine => (
            <Link 
              key={`${machine.canon}-${machine.id}`}
              to={`/arcade/${machine.canon}`}
              className="featured-machine"
              style={{ '--canon-color': CANONS[machine.canon].colors.primary }}
            >
              <span className="machine-icon">{machine.icon}</span>
              <div className="machine-info">
                <h4>{machine.name}</h4>
                <span className="machine-canon">{machine.canonName}</span>
              </div>
              <div className="machine-cost">
                <span className="cost-icon">🪙</span>
                <span>{machine.cost}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Recent Jackpots */}
      <section className="jackpots-section">
        <h2 className="section-title neon-text">RECENT JACKPOTS</h2>
        {recentJackpots.length > 0 ? (
          <div className="jackpots-list" data-testid="recent-jackpots">
            {recentJackpots.slice(0, 5).map((jackpot, i) => (
              <div 
                key={i} 
                className="jackpot-item"
                style={{ '--canon-color': CANONS[jackpot.canon]?.colors.primary }}
              >
                <span className="jackpot-type">{jackpot.name}</span>
                <span className="jackpot-canon">{CANONS[jackpot.canon]?.icon} {CANONS[jackpot.canon]?.name}</span>
                <span className="jackpot-win">+{jackpot.amount.toLocaleString()} 🪙</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-jackpots">
            <p>No jackpots yet. Start playing to win!</p>
          </div>
        )}
      </section>

      {/* Quick Links */}
      <section className="quick-links-section">
        <h2 className="section-title neon-text">QUICK ACCESS</h2>
        <div className="quick-links" data-testid="quick-links">
          <Link to="/arcade/sessions" className="quick-link">
            <span className="link-icon">📋</span>
            <span>Sessions</span>
            <span className="link-count">{sessions.length}</span>
          </Link>
          <Link to="/arcade/wallet" className="quick-link">
            <span className="link-icon">💰</span>
            <span>Wallet</span>
            <span className="link-count">{tokens.toLocaleString()}</span>
          </Link>
          <Link to="/arcade/teams" className="quick-link">
            <span className="link-icon">👥</span>
            <span>AI Teams</span>
          </Link>
          <Link to="/arcade/packs" className="quick-link">
            <span className="link-icon">📦</span>
            <span>Output Packs</span>
          </Link>
        </div>
      </section>

      {/* Canon Rooms Grid */}
      <section className="all-canons-section">
        <h2 className="section-title neon-text">ALL CANON ROOMS</h2>
        <div className="canons-grid" data-testid="canons-grid">
          {Object.values(CANONS).map(canon => (
            <Link 
              key={canon.id}
              to={`/arcade/${canon.id}`}
              className="canon-card"
              style={{ 
                '--canon-color': canon.colors.primary,
                '--canon-bg': canon.colors.secondary,
                '--canon-neon': canon.colors.neon
              }}
            >
              <div className="canon-card-header">
                <span className="canon-card-icon">{canon.icon}</span>
                <span className="canon-card-multiplier">{canon.multiplier}x</span>
              </div>
              <h3 className="canon-card-name">{canon.name}</h3>
              <p className="canon-card-desc">{canon.description}</p>
              <div className="canon-card-machines">
                {canon.machines.length} Machines
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};

export default ArcadeHub;
