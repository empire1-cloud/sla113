import { useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MoneyPipelinePage = () => {
  const [formData, setFormData] = useState({
    idea: "",
    target_revenue: "",
    industry: "",
    context: ""
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("summary");

  const sampleIdeas = [
    { idea: "AI-powered resume screening for HR teams", revenue: "$500K ARR", industry: "HR Tech" },
    { idea: "Subscription meal kit for keto dieters", revenue: "$1M ARR", industry: "Food & Beverage" },
    { idea: "B2B invoice automation SaaS", revenue: "$2M ARR", industry: "FinTech" },
    { idea: "Online marketplace for vintage watches", revenue: "$750K ARR", industry: "E-commerce" },
    { idea: "AI writing assistant for legal documents", revenue: "$3M ARR", industry: "Legal Tech" }
  ];

  const loadSample = (sample) => {
    setFormData({
      idea: sample.idea,
      target_revenue: sample.revenue,
      industry: sample.industry,
      context: ""
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.idea.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        idea: formData.idea,
        model: "gemini-3-flash"
      };
      if (formData.target_revenue) payload.target_revenue = formData.target_revenue;
      if (formData.industry) payload.industry = formData.industry;
      if (formData.context) payload.context = formData.context;

      const res = await axios.post(`${API}/money-pipeline`, payload, { timeout: 120000 });
      setResult(res.data);
      setActiveTab("summary");
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Failed to generate pipeline");
    } finally {
      setLoading(false);
    }
  };

  const renderSection = (title, data, icon) => {
    if (!data) return null;
    return (
      <div className="pipeline-section">
        <h3>{icon} {title}</h3>
        {Array.isArray(data) ? (
          <ul>{data.map((item, i) => <li key={i}>{typeof item === 'object' ? JSON.stringify(item) : item}</li>)}</ul>
        ) : typeof data === 'object' ? (
          <div className="nested-data">
            {Object.entries(data).map(([key, val]) => (
              <div key={key} className="data-row">
                <strong>{key.replace(/_/g, ' ')}:</strong>
                <span>{Array.isArray(val) ? val.join(', ') : typeof val === 'object' ? JSON.stringify(val) : val}</span>
              </div>
            ))}
          </div>
        ) : (
          <p>{data}</p>
        )}
      </div>
    );
  };

  return (
    <div className="page-container" data-testid="money-pipeline-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <h1>💵 Universal Money Pipeline</h1>
        <p className="subtitle">Transform any idea into a complete monetizable system</p>
      </header>

      <div className="pipeline-layout">
        <aside className="pipeline-sidebar">
          <form onSubmit={handleSubmit} className="pipeline-form" data-testid="pipeline-form">
            <div className="form-group">
              <label>Business Idea *</label>
              <textarea
                value={formData.idea}
                onChange={(e) => setFormData({ ...formData, idea: e.target.value })}
                placeholder="Describe your business idea..."
                rows={3}
                required
                data-testid="idea-input"
              />
            </div>

            <div className="form-group">
              <label>Target Revenue</label>
              <input
                type="text"
                value={formData.target_revenue}
                onChange={(e) => setFormData({ ...formData, target_revenue: e.target.value })}
                placeholder="e.g., $1M ARR"
                data-testid="revenue-input"
              />
            </div>

            <div className="form-group">
              <label>Industry</label>
              <input
                type="text"
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                placeholder="e.g., SaaS, E-commerce"
                data-testid="industry-input"
              />
            </div>

            <div className="form-group">
              <label>Additional Context</label>
              <textarea
                value={formData.context}
                onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                placeholder="Any constraints or details..."
                rows={2}
                data-testid="context-input"
              />
            </div>

            <button
              type="submit"
              className="btn-submit"
              disabled={loading || !formData.idea.trim()}
              data-testid="submit-btn"
            >
              {loading ? (
                <><span className="btn-spinner"></span> Generating...</>
              ) : (
                <>🚀 Generate Pipeline</>
              )}
            </button>
          </form>

          <div className="sample-ideas">
            <h4>💡 Try a Sample</h4>
            <div className="sample-list">
              {sampleIdeas.map((sample, i) => (
                <button
                  key={i}
                  className="sample-btn"
                  onClick={() => loadSample(sample)}
                  data-testid={`sample-btn-${i}`}
                >
                  {sample.idea.slice(0, 40)}...
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="pipeline-main">
          {error && (
            <div className="error-box" data-testid="error-box">
              <span>⚠️</span> {error}
            </div>
          )}

          {loading && (
            <div className="loading-box">
              <div className="spinner"></div>
              <p>Generating your money pipeline...</p>
              <p className="loading-sub">This may take up to 60 seconds</p>
            </div>
          )}

          {result && !loading && (
            <div className="pipeline-results" data-testid="pipeline-results">
              <div className="tabs">
                {["summary", "market", "pricing", "business", "execution", "forecast", "marketing", "launch", "raw"].map(tab => (
                  <button
                    key={tab}
                    className={`tab ${activeTab === tab ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab)}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              <div className="tab-content">
                {activeTab === "summary" && (
                  <div className="summary-grid">
                    <div className="summary-card">
                      <h4>📊 Market</h4>
                      <p>{result.market_analysis?.target_segments?.length || 0} segments</p>
                      <p>{result.market_analysis?.pain_points?.length || 0} pain points</p>
                    </div>
                    <div className="summary-card">
                      <h4>💰 Pricing</h4>
                      <p>{result.pricing_model?.tiers?.length || 0} tiers</p>
                      <p>{result.pricing_model?.monetization_strategy?.slice(0, 50)}...</p>
                    </div>
                    <div className="summary-card">
                      <h4>🏢 Business</h4>
                      <p>{result.business_model?.core_offer?.slice(0, 80)}...</p>
                    </div>
                    <div className="summary-card">
                      <h4>📈 Forecast</h4>
                      <p>{result.forecast?.revenue_projection?.slice(0, 80)}...</p>
                    </div>
                  </div>
                )}

                {activeTab === "market" && renderSection("Market Analysis", result.market_analysis, "📊")}
                {activeTab === "pricing" && (
                  <div>
                    {renderSection("Pricing Model", result.pricing_model, "💰")}
                    {result.pricing_model?.tiers && (
                      <div className="tiers-grid">
                        {result.pricing_model.tiers.map((tier, i) => (
                          <div key={i} className="tier-card">
                            <h4>{tier.name}</h4>
                            <p className="tier-price">{tier.price}</p>
                            <ul>{tier.features?.map((f, j) => <li key={j}>{f}</li>)}</ul>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                {activeTab === "business" && renderSection("Business Model", result.business_model, "🏢")}
                {activeTab === "execution" && renderSection("Execution Plan", result.execution_plan, "📋")}
                {activeTab === "forecast" && renderSection("Forecast", result.forecast, "📈")}
                {activeTab === "marketing" && renderSection("Marketing Funnel", result.marketing_funnel, "📣")}
                {activeTab === "launch" && renderSection("Launch Strategy", result.launch_strategy, "🚀")}
                {activeTab === "raw" && (
                  <pre className="raw-json" data-testid="raw-json">{JSON.stringify(result, null, 2)}</pre>
                )}
              </div>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="empty-state">
              <span className="empty-icon">💵</span>
              <h3>Ready to Transform Your Idea</h3>
              <p>Enter your business idea and click Generate to create a complete monetization pipeline</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default MoneyPipelinePage;
