import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const HomePage = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    fetchHealth();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`${API}/health`);
      setHealth(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const quickTest = async () => {
    setTestLoading(true);
    setTestResult(null);
    try {
      const res = await axios.post(`${API}/money-pipeline`, {
        idea: "AI-powered task management for remote teams",
        model: "gemini-3-flash"
      }, { timeout: 120000 });
      setTestResult({ success: true, data: res.data });
    } catch (e) {
      setTestResult({ success: false, error: e.message });
    } finally {
      setTestLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Connecting to backend...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" data-testid="home-page">
      <header className="page-header">
        <h1>🧠 Hybrid Intelligence Core</h1>
        <p className="subtitle">Multi-Model AI Pipeline System</p>
      </header>

      <div className="stats-row">
        <div className="stat-card" data-testid="status-card">
          <div className={`status-indicator ${health?.status === 'healthy' ? 'green' : 'red'}`}></div>
          <div className="stat-content">
            <span className="stat-label">Status</span>
            <span className="stat-value">{health?.status?.toUpperCase() || 'UNKNOWN'}</span>
          </div>
        </div>

        <div className="stat-card" data-testid="engine-count-card">
          <span className="stat-icon">⚙️</span>
          <div className="stat-content">
            <span className="stat-label">Active Engines</span>
            <span className="stat-value">{health?.engines?.length || 0}</span>
          </div>
        </div>

        <div className="stat-card" data-testid="models-card">
          <span className="stat-icon">🤖</span>
          <div className="stat-content">
            <span className="stat-label">LLM Models</span>
            <span className="stat-value">{health?.models ? Object.keys(health.models).length : 0}</span>
          </div>
        </div>
      </div>

      <div className="models-row">
        {health?.models && Object.entries(health.models).map(([name, status]) => (
          <div key={name} className={`model-chip ${status}`}>
            <span className="model-dot"></span>
            {name}
          </div>
        ))}
      </div>

      <section className="action-section">
        <h2>Quick Actions</h2>
        <div className="action-grid">
          <Link to="/engines" className="action-card" data-testid="view-engines-link">
            <span className="action-icon">📋</span>
            <h3>View All Engines</h3>
            <p>Browse {health?.engines?.length || 0} available AI engines</p>
          </Link>

          <Link to="/money-pipeline" className="action-card" data-testid="money-pipeline-link">
            <span className="action-icon">💵</span>
            <h3>Money Pipeline</h3>
            <p>Transform ideas into monetizable systems</p>
          </Link>

          <div className="action-card clickable" onClick={quickTest} data-testid="quick-test-card">
            <span className="action-icon">🚀</span>
            <h3>Quick Test</h3>
            <p>Test Money Pipeline with sample idea</p>
            {testLoading && <div className="mini-spinner"></div>}
          </div>
        </div>
      </section>

      {testResult && (
        <section className="test-result-section" data-testid="test-result">
          <h2>{testResult.success ? '✅ Test Successful' : '❌ Test Failed'}</h2>
          {testResult.success ? (
            <div className="result-summary">
              <p><strong>Market Segments:</strong> {testResult.data.market_analysis?.target_segments?.length || 0}</p>
              <p><strong>Pricing Tiers:</strong> {testResult.data.pricing_model?.tiers?.length || 0}</p>
              <p><strong>Core Offer:</strong> {testResult.data.business_model?.core_offer?.slice(0, 100)}...</p>
              <Link to="/money-pipeline" className="btn-primary">Open Full Pipeline →</Link>
            </div>
          ) : (
            <p className="error-text">{testResult.error}</p>
          )}
        </section>
      )}

      <section className="engines-preview">
        <h2>Engines Overview</h2>
        <div className="engines-mini-grid">
          {health?.engines?.slice(0, 10).map((engine, i) => (
            <div key={engine} className="engine-mini-card" style={{ animationDelay: `${i * 0.05}s` }}>
              {engine.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
            </div>
          ))}
          {health?.engines?.length > 10 && (
            <Link to="/engines" className="engine-mini-card more">
              +{health.engines.length - 10} more
            </Link>
          )}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
