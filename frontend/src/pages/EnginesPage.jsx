import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ENGINE_DATA = {
  hybrid_intelligence_core: { path: "/api/core/execute", desc: "Master orchestrator - unified execution endpoint" },
  routing_engine: { path: "/api/route", desc: "Task classification and model selection" },
  strategy_engine: { path: "/api/strategy", desc: "Generate high-level actionable strategies" },
  plan_builder_engine: { path: "/api/plan", desc: "Convert goals into execution plans" },
  analysis_engine: { path: "/api/analyze", desc: "Deep SWOT and structured analysis" },
  opportunity_mapper_engine: { path: "/api/opportunities", desc: "Identify high-leverage opportunities" },
  evaluator_engine: { path: "/api/evaluate", desc: "Score and evaluate with criteria" },
  pricing_engine: { path: "/api/pricing", desc: "Generate pricing structures and tiers" },
  blueprint_engine: { path: "/api/blueprint", desc: "System architecture blueprints" },
  persona_engine: { path: "/api/persona", desc: "User/customer persona generation" },
  anime_character_engine: { path: "/api/anime/character", desc: "Original anime character creation" },
  anime_lore_engine: { path: "/api/anime/lore", desc: "World-building and mythology" },
  anime_story_engine: { path: "/api/anime/story", desc: "Narrative structure and story arcs" },
  art_direction_engine: { path: "/api/art-direction", desc: "Visual direction for creative projects" },
  money_pipeline_engine: { path: "/api/money-pipeline", desc: "Transform ideas into monetizable systems" },
  pipeline_composer_engine: { path: "/api/pipeline/compose", desc: "Multi-engine workflow orchestration" },
  canon_enforcer: { path: "-", desc: "Output normalization (internal)" },
  drift_monitor: { path: "/api/drift-report", desc: "Model behavioral tracking" },
  error_handler: { path: "-", desc: "Structured error responses (internal)" }
};

const TEST_PAYLOADS = {
  strategy_engine: { goal: "Launch a SaaS product in 90 days", model: "gemini-3-flash" },
  analysis_engine: { subject: "Remote work software market", model: "gemini-3-flash" },
  pricing_engine: { product: "AI Writing Assistant", model: "gemini-3-flash" },
  persona_engine: { audience: "Startup founders aged 25-40", model: "gemini-3-flash" },
  blueprint_engine: { system_description: "E-commerce platform with payments", model: "gemini-3-flash" },
  anime_character_engine: { concept: "Time-traveling samurai", genre: "shonen", model: "gemini-3-flash" },
  money_pipeline_engine: { idea: "AI tutoring platform", model: "gemini-3-flash" }
};

const EnginesPage = () => {
  const [engines, setEngines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testingEngine, setTestingEngine] = useState(null);
  const [testResults, setTestResults] = useState({});

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

  const testEngine = async (engineName) => {
    const payload = TEST_PAYLOADS[engineName];
    if (!payload) return;

    const engineInfo = ENGINE_DATA[engineName];
    if (!engineInfo || engineInfo.path === "-") return;

    setTestingEngine(engineName);
    try {
      const res = await axios.post(`${process.env.REACT_APP_BACKEND_URL}${engineInfo.path}`, payload, { timeout: 120000 });
      setTestResults(prev => ({ ...prev, [engineName]: { success: true, data: res.data } }));
    } catch (e) {
      setTestResults(prev => ({ ...prev, [engineName]: { success: false, error: e.message } }));
    } finally {
      setTestingEngine(null);
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

  if (loading) {
    return <div className="page-container"><div className="loading-box"><div className="spinner"></div></div></div>;
  }

  return (
    <div className="page-container" data-testid="engines-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <h1>📋 Engine Dashboard</h1>
        <p className="subtitle">{engines.length} AI engines available</p>
      </header>

      <div className="engines-table-container">
        <table className="engines-table" data-testid="engines-table">
          <thead>
            <tr>
              <th>Engine</th>
              <th>Endpoint</th>
              <th>Description</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {engines.map((engine) => {
              const info = ENGINE_DATA[engine] || { path: "-", desc: "No description" };
              const canTest = TEST_PAYLOADS[engine] && info.path !== "-";
              const result = testResults[engine];
              
              return (
                <tr key={engine} data-testid={`engine-row-${engine}`}>
                  <td className="engine-name-cell">
                    <span className="engine-icon">{getIcon(engine)}</span>
                    <span>{formatName(engine)}</span>
                  </td>
                  <td className="endpoint-cell">
                    <code>{info.path}</code>
                  </td>
                  <td className="desc-cell">{info.desc}</td>
                  <td className="action-cell">
                    {engine === 'money_pipeline_engine' ? (
                      <Link to="/money-pipeline" className="btn-small btn-primary">
                        Open →
                      </Link>
                    ) : canTest ? (
                      <button
                        className={`btn-small ${result?.success ? 'btn-success' : result?.success === false ? 'btn-error' : 'btn-secondary'}`}
                        onClick={() => testEngine(engine)}
                        disabled={testingEngine === engine}
                        data-testid={`test-btn-${engine}`}
                      >
                        {testingEngine === engine ? '...' : result?.success ? '✓' : result?.success === false ? '✗' : 'Test'}
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

      {Object.keys(testResults).length > 0 && (
        <section className="test-results-section">
          <h2>Test Results</h2>
          <div className="results-grid">
            {Object.entries(testResults).map(([engine, result]) => (
              <div key={engine} className={`result-card ${result.success ? 'success' : 'error'}`}>
                <h4>{getIcon(engine)} {formatName(engine)}</h4>
                {result.success ? (
                  <pre className="result-json">{JSON.stringify(result.data, null, 2).slice(0, 500)}...</pre>
                ) : (
                  <p className="error-text">{result.error}</p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

export default EnginesPage;
