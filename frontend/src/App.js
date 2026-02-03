import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EngineCard = ({ name, index }) => {
  const getEngineIcon = (engineName) => {
    if (engineName.includes('strategy')) return '🎯';
    if (engineName.includes('plan')) return '📋';
    if (engineName.includes('analysis')) return '🔍';
    if (engineName.includes('opportunity')) return '💡';
    if (engineName.includes('evaluator')) return '⚖️';
    if (engineName.includes('pricing')) return '💰';
    if (engineName.includes('blueprint')) return '🏗️';
    if (engineName.includes('persona')) return '👤';
    if (engineName.includes('anime')) return '🎨';
    if (engineName.includes('art')) return '🖼️';
    if (engineName.includes('money')) return '💵';
    if (engineName.includes('pipeline')) return '🔗';
    if (engineName.includes('canon')) return '📜';
    if (engineName.includes('drift')) return '📊';
    if (engineName.includes('error')) return '🛡️';
    if (engineName.includes('routing')) return '🔀';
    if (engineName.includes('hybrid') || engineName.includes('core')) return '🧠';
    return '⚙️';
  };

  const formatEngineName = (name) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div 
      className="engine-card"
      style={{ animationDelay: `${index * 0.05}s` }}
      data-testid={`engine-card-${name}`}
    >
      <span className="engine-icon">{getEngineIcon(name)}</span>
      <span className="engine-name">{formatEngineName(name)}</span>
    </div>
  );
};

const ModelBadge = ({ name, status }) => (
  <div className={`model-badge ${status === 'available' ? 'available' : 'unavailable'}`} data-testid={`model-${name}`}>
    <span className="model-status-dot"></span>
    <span className="model-name">{name}</span>
  </div>
);

const MoneyPipelineTester = () => {
  const [idea, setIdea] = useState("AI-powered fitness coaching app for busy professionals");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const sampleIdeas = [
    "AI-powered fitness coaching app for busy professionals",
    "Subscription box for remote workers' productivity tools",
    "B2B SaaS for automated invoice processing",
    "Marketplace for freelance legal services",
    "Smart home energy optimization platform"
  ];

  const testMoneyPipeline = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await axios.post(`${API}/money-pipeline`, {
        idea: idea,
        model: "gemini-3-flash"
      }, { timeout: 120000 });
      setResult(response.data);
    } catch (e) {
      console.error(e);
      setError(e.response?.data?.detail || e.message || "Failed to generate pipeline");
    } finally {
      setLoading(false);
    }
  };

  const randomizeIdea = () => {
    const randomIdea = sampleIdeas[Math.floor(Math.random() * sampleIdeas.length)];
    setIdea(randomIdea);
  };

  return (
    <div className="money-pipeline-tester" data-testid="money-pipeline-tester">
      <h2 className="section-title">
        <span>💵</span> Test Money Pipeline Engine
      </h2>
      
      <div className="input-group">
        <label htmlFor="idea-input">Enter your idea:</label>
        <div className="input-row">
          <input
            id="idea-input"
            type="text"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            placeholder="Describe your business idea..."
            className="idea-input"
            data-testid="idea-input"
          />
          <button 
            onClick={randomizeIdea} 
            className="randomize-btn"
            title="Try a random idea"
            data-testid="randomize-btn"
          >
            🎲
          </button>
        </div>
      </div>

      <button
        onClick={testMoneyPipeline}
        disabled={loading || !idea.trim()}
        className={`test-button ${loading ? 'loading' : ''}`}
        data-testid="test-money-pipeline-btn"
      >
        {loading ? (
          <>
            <span className="btn-spinner"></span>
            Generating Pipeline...
          </>
        ) : (
          <>
            <span>🚀</span> Generate Money Pipeline
          </>
        )}
      </button>

      {error && (
        <div className="error-message" data-testid="error-message">
          <span>⚠️</span> {error}
        </div>
      )}

      {result && (
        <div className="result-container" data-testid="pipeline-result">
          <div className="result-header">
            <h3>Pipeline Generated Successfully</h3>
          </div>
          
          <div className="result-grid">
            <div className="result-card">
              <h4>📊 Market Analysis</h4>
              <p><strong>Segments:</strong> {result.market_analysis?.target_segments?.length || 0}</p>
              <p><strong>Pain Points:</strong> {result.market_analysis?.pain_points?.length || 0}</p>
              <p className="highlight">{result.market_analysis?.positioning_opportunity?.slice(0, 100)}...</p>
            </div>

            <div className="result-card">
              <h4>💰 Pricing Model</h4>
              <p><strong>Tiers:</strong> {result.pricing_model?.tiers?.length || 0}</p>
              {result.pricing_model?.tiers?.map((tier, i) => (
                <p key={i} className="tier-item">{tier.name}: {tier.price}</p>
              ))}
            </div>

            <div className="result-card">
              <h4>🏢 Business Model</h4>
              <p><strong>Core Offer:</strong></p>
              <p className="highlight">{result.business_model?.core_offer?.slice(0, 120)}...</p>
            </div>

            <div className="result-card">
              <h4>📈 Forecast</h4>
              <p><strong>Revenue Projection:</strong></p>
              <p className="highlight">{result.forecast?.revenue_projection?.slice(0, 100)}...</p>
              <p><strong>Risks:</strong> {result.forecast?.risks?.length || 0}</p>
            </div>

            <div className="result-card">
              <h4>📋 Execution Plan</h4>
              <p><strong>Phase 1:</strong> {result.execution_plan?.phase_1?.length || 0} actions</p>
              <p><strong>Phase 2:</strong> {result.execution_plan?.phase_2?.length || 0} actions</p>
              <p><strong>Critical Path:</strong> {result.execution_plan?.critical_path?.length || 0} items</p>
            </div>

            <div className="result-card">
              <h4>📣 Marketing Funnel</h4>
              <p><strong>TOFU:</strong> {result.marketing_funnel?.top_of_funnel?.length || 0} tactics</p>
              <p><strong>MOFU:</strong> {result.marketing_funnel?.middle_of_funnel?.length || 0} tactics</p>
              <p><strong>BOFU:</strong> {result.marketing_funnel?.bottom_of_funnel?.length || 0} tactics</p>
            </div>
          </div>

          <details className="raw-details">
            <summary>View Raw JSON Response</summary>
            <pre className="raw-json">{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
};

const Home = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/health`);
      setHealthData(response.data);
      setError(null);
    } catch (e) {
      console.error(e, 'Error fetching health data');
      setError('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  if (loading) {
    return (
      <div className="dashboard" data-testid="loading-screen">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Connecting to Hybrid Intelligence Core...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard" data-testid="error-screen">
        <div className="error-container">
          <span className="error-icon">⚠️</span>
          <h2>Connection Error</h2>
          <p>{error}</p>
          <button onClick={fetchHealth} className="retry-button" data-testid="retry-button">
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard" data-testid="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">
            <span className="title-icon">🧠</span>
            Hybrid Intelligence Core
          </h1>
          <div className={`status-badge ${healthData?.status === 'healthy' ? 'healthy' : 'unhealthy'}`} data-testid="status-badge">
            <span className="status-dot"></span>
            {healthData?.status?.toUpperCase() || 'UNKNOWN'}
          </div>
        </div>
        <p className="dashboard-subtitle">{healthData?.pipeline || 'AI Pipeline'}</p>
      </header>

      <section className="section models-section">
        <h2 className="section-title">Available Models</h2>
        <div className="models-grid" data-testid="models-grid">
          {healthData?.models && Object.entries(healthData.models).map(([name, status]) => (
            <ModelBadge key={name} name={name} status={status} />
          ))}
        </div>
      </section>

      <section className="section engines-section">
        <h2 className="section-title">
          Active Engines 
          <span className="engine-count" data-testid="engine-count">{healthData?.engines?.length || 0}</span>
        </h2>
        <div className="engines-grid" data-testid="engines-grid">
          {healthData?.engines?.map((engine, index) => (
            <EngineCard key={engine} name={engine} index={index} />
          ))}
        </div>
      </section>

      <section className="section">
        <MoneyPipelineTester />
      </section>

      <footer className="dashboard-footer">
        <p>Backend: <code>{BACKEND_URL}</code></p>
        <button onClick={fetchHealth} className="refresh-button" data-testid="refresh-button">
          ↻ Refresh
        </button>
      </footer>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
