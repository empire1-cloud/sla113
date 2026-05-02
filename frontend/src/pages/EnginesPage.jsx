import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ENGINE_CONFIG = {
  hybrid_intelligence_core: {
    path: "/core/execute",
    method: "POST",
    desc: "Master orchestrator - unified execution endpoint",
    payload: { prompt: "Create a strategy for launching a mobile app", task_type: "strategy" }
  },
  routing_engine: {
    path: "/route",
    method: "POST",
    desc: "Task classification and model selection",
    payload: { goal: "Analyze the competitive landscape for AI startups" }
  },
  strategy_engine: {
    path: "/strategy",
    method: "POST",
    desc: "Generate high-level actionable strategies",
    payload: { goal: "Launch a B2B SaaS product in 90 days", context: "Early-stage startup with $50K budget", tone: "direct" }
  },
  plan_builder_engine: {
    path: "/plan",
    method: "POST",
    desc: "Convert goals into execution plans",
    payload: { goal: "Build an MVP for a fitness tracking app", context: "2 developers, 6 week timeline" }
  },
  analysis_engine: {
    path: "/analyze",
    method: "POST",
    desc: "Deep SWOT and structured analysis",
    payload: { subject: "Remote work software market in 2025", focus_area: "competitive dynamics" }
  },
  opportunity_mapper_engine: {
    path: "/opportunities",
    method: "POST",
    desc: "Identify high-leverage opportunities",
    payload: { situation: "E-commerce store with declining traffic", goals: ["Increase revenue by 30%", "Expand to new markets"] }
  },
  evaluator_engine: {
    path: "/evaluate",
    method: "POST",
    desc: "Score and evaluate with criteria",
    payload: { subject: "New Product Idea", content: "AI-powered personal finance assistant that automatically categorizes expenses and suggests savings", criteria_preset: "idea" }
  },
  pricing_engine: {
    path: "/pricing",
    method: "POST",
    desc: "Generate pricing structures and tiers",
    payload: { product: "Cloud-based project management tool", target_market: "Small to medium businesses", pricing_model: "subscription" }
  },
  blueprint_engine: {
    path: "/blueprint",
    method: "POST",
    desc: "System architecture blueprints",
    payload: { system_description: "Real-time chat application with video calling", requirements: ["Handle 10K concurrent users", "End-to-end encryption", "Mobile and web support"] }
  },
  persona_engine: {
    path: "/persona",
    method: "POST",
    desc: "User/customer persona generation",
    payload: { audience: "Startup founders aged 25-40 in tech industry", product: "Business analytics dashboard", industry: "SaaS" }
  },
  anime_character_engine: {
    path: "/anime/character",
    method: "POST",
    desc: "Original anime character creation",
    payload: { concept: "A genius inventor who builds mechanical companions", role: "protagonist", genre: "steampunk", abilities_type: "technical" }
  },
  anime_lore_engine: {
    path: "/anime/lore",
    method: "POST",
    desc: "World-building and mythology",
    payload: { world_concept: "A world where music has magical properties", genre: "fantasy", themes: ["creativity", "harmony", "rebellion"] }
  },
  anime_story_engine: {
    path: "/anime/story",
    method: "POST",
    desc: "Narrative structure and story arcs",
    payload: { concept: "A young musician discovers their songs can heal or destroy", genre: "fantasy", episode_count: 12 }
  },
  art_direction_engine: {
    path: "/art-direction",
    method: "POST",
    desc: "Visual direction for creative projects",
    payload: { project: "Cyberpunk anime series", genre: "sci-fi", mood: "dark and neon", target_audience: "Young adults 18-30" }
  },
  money_pipeline_engine: {
    path: "/money-pipeline",
    method: "POST",
    desc: "Transform ideas into monetizable systems",
    payload: { idea: "AI-powered language learning app with personalized lessons", target_revenue: "$1M ARR", industry: "EdTech" }
  },
  pipeline_composer_engine: {
    path: "/pipeline/compose",
    method: "POST",
    desc: "Multi-engine workflow orchestration",
    payload: { request: "Create a full business plan for a food delivery startup", preferred_engines: ["strategy_engine", "pricing_engine", "persona_engine"] }
  },
  canon_enforcer: {
    path: null,
    method: null,
    desc: "Output normalization (internal)",
    payload: null
  },
  drift_monitor: {
    path: "/drift-report",
    method: "GET",
    desc: "Model behavioral tracking",
    payload: null
  },
  error_handler: {
    path: null,
    method: null,
    desc: "Structured error responses (internal)",
    payload: null
  }
};

const TestModal = ({ engine, config, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(JSON.stringify(config.payload, null, 2));

  const runTest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      const url = `${API}${config.path}`;
      
      if (config.method === "GET") {
        response = await axios.get(url, { timeout: 120000 });
      } else {
        const parsedPayload = JSON.parse(payload);
        // Add model override for faster testing
        if (!parsedPayload.model) {
          parsedPayload.model = "gemini-3-flash";
        }
        response = await axios.post(url, parsedPayload, { timeout: 120000 });
      }
      
      setResult(response.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const formatEngineName = (name) => {
    return name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  return (
    <div className="modal-overlay" onClick={onClose} data-testid="test-modal">
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{formatEngineName(engine)}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="modal-info">
            <p><strong>Endpoint:</strong> <code>{config.method} {config.path}</code></p>
            <p><strong>Description:</strong> {config.desc}</p>
          </div>

          {config.method === "POST" && (
            <div className="payload-section">
              <label>Request Payload:</label>
              <textarea
                value={payload}
                onChange={(e) => setPayload(e.target.value)}
                className="payload-editor"
                rows={8}
                data-testid="payload-editor"
              />
            </div>
          )}

          <button
            className="run-test-btn"
            onClick={runTest}
            disabled={loading}
            data-testid="run-test-btn"
          >
            {loading ? (
              <><span className="btn-spinner"></span> Running...</>
            ) : (
              <><span>▶</span> Run Test</>
            )}
          </button>

          {error && (
            <div className="modal-error" data-testid="modal-error">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="modal-result" data-testid="modal-result">
              <div className="result-header">
                <strong>Response:</strong>
                <span className="success-badge">✓ Success</span>
              </div>
              <pre className="result-json">{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const EnginesPage = () => {
  const [engines, setEngines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEngine, setSelectedEngine] = useState(null);

  useEffect(() => {
    fetchEngines();
  }, []);

  const fetchEngines = async () => {
    try {
      const res = await axios.get(`${API}/health`);
      setEngines(res.data.engines || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (name) => {
    if (name.includes('strategy')) return '🎯';
    if (name.includes('plan')) return '📋';
    if (name.includes('analysis')) return '🔍';
    if (name.includes('opportunity')) return '💡';
    if (name.includes('evaluator')) return '⚖️';
    if (name.includes('pricing')) return '💰';
    if (name.includes('blueprint')) return '🏗️';
    if (name.includes('persona')) return '👤';
    if (name.includes('anime')) return '🎨';
    if (name.includes('art')) return '🖼️';
    if (name.includes('money')) return '💵';
    if (name.includes('pipeline') || name.includes('composer')) return '🔗';
    if (name.includes('canon')) return '📜';
    if (name.includes('drift')) return '📊';
    if (name.includes('error')) return '🛡️';
    if (name.includes('routing')) return '🔀';
    if (name.includes('hybrid') || name.includes('core')) return '🧠';
    return '⚙️';
  };

  const formatName = (name) => name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

  const canTest = (engine) => {
    const config = ENGINE_CONFIG[engine];
    return config && config.path !== null;
  };

  if (loading) {
    return <div className="page-container"><div className="loading-box"><div className="spinner"></div></div></div>;
  }

  return (
    <div className="page-container" data-testid="engines-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <h1>📋 Engine Dashboard</h1>
        <p className="subtitle">{engines.length} AI engines available • Click "Test" to try any engine</p>
      </header>

      <div className="engines-table-container">
        <table className="engines-table" data-testid="engines-table">
          <thead>
            <tr>
              <th>Engine</th>
              <th>Method</th>
              <th>Endpoint</th>
              <th>Description</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {engines.map((engine) => {
              const config = ENGINE_CONFIG[engine] || { path: "-", method: "-", desc: "No description" };
              const testable = canTest(engine);
              
              return (
                <tr key={engine} data-testid={`engine-row-${engine}`}>
                  <td className="engine-name-cell">
                    <span className="engine-icon">{getIcon(engine)}</span>
                    <span>{formatName(engine)}</span>
                  </td>
                  <td className="method-cell">
                    {config.method ? (
                      <span className={`method-badge ${config.method?.toLowerCase()}`}>
                        {config.method}
                      </span>
                    ) : (
                      <span className="method-badge internal">-</span>
                    )}
                  </td>
                  <td className="endpoint-cell">
                    <code>{config.path || "internal"}</code>
                  </td>
                  <td className="desc-cell">{config.desc}</td>
                  <td className="action-cell">
                    {testable ? (
                      <button
                        className="btn-small btn-test"
                        onClick={() => setSelectedEngine(engine)}
                        data-testid={`test-btn-${engine}`}
                      >
                        Test
                      </button>
                    ) : (
                      <span className="internal-badge">Internal</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="engines-legend">
        <h4>Legend</h4>
        <div className="legend-items">
          <span><span className="method-badge post">POST</span> Requires input payload</span>
          <span><span className="method-badge get">GET</span> No input required</span>
          <span><span className="method-badge internal">-</span> Internal engine (not directly callable)</span>
        </div>
      </div>

      {selectedEngine && ENGINE_CONFIG[selectedEngine] && (
        <TestModal
          engine={selectedEngine}
          config={ENGINE_CONFIG[selectedEngine]}
          onClose={() => setSelectedEngine(null)}
        />
      )}
    </div>
  );
};

export default EnginesPage;
