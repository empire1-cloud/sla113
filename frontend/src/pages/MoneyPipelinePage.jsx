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

  const renderList = (items) => {
    if (!items || !Array.isArray(items)) return null;
    return (
      <ul>
        {items.map((item, i) => (
          <li key={i}>{typeof item === 'object' ? JSON.stringify(item) : String(item)}</li>
        ))}
      </ul>
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
                <span>⏳ Generating...</span>
              ) : (
                <span>🚀 Generate Pipeline</span>
              )}
            </button>
          </form>

          <div className="sample-ideas">
            <h4>💡 Try a Sample</h4>
            <div className="sample-list">
              {sampleIdeas.map((sample, i) => (
                <button
                  key={i}
                  type="button"
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
                    type="button"
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
                    </div>
                    <div className="summary-card">
                      <h4>🏢 Business</h4>
                      <p>{String(result.business_model?.core_offer || "").slice(0, 80)}...</p>
                    </div>
                    <div className="summary-card">
                      <h4>📈 Forecast</h4>
                      <p>{String(result.forecast?.revenue_projection || "").slice(0, 80)}...</p>
                    </div>
                  </div>
                )}

                {activeTab === "market" && (
                  <div className="pipeline-section">
                    <h3>📊 Market Analysis</h3>
                    <div className="data-block">
                      <strong>Target Segments:</strong>
                      {renderList(result.market_analysis?.target_segments)}
                    </div>
                    <div className="data-block">
                      <strong>Pain Points:</strong>
                      {renderList(result.market_analysis?.pain_points)}
                    </div>
                    <div className="data-block">
                      <strong>Positioning:</strong>
                      <p>{result.market_analysis?.positioning_opportunity}</p>
                    </div>
                  </div>
                )}

                {activeTab === "pricing" && (
                  <div className="pipeline-section">
                    <h3>💰 Pricing Model</h3>
                    <div className="tiers-grid">
                      {result.pricing_model?.tiers?.map((tier, i) => (
                        <div key={i} className="tier-card">
                          <h4>{tier.name}</h4>
                          <p className="tier-price">{tier.price}</p>
                          {renderList(tier.features)}
                        </div>
                      ))}
                    </div>
                    <div className="data-block">
                      <strong>Strategy:</strong>
                      <p>{result.pricing_model?.monetization_strategy}</p>
                    </div>
                  </div>
                )}

                {activeTab === "business" && (
                  <div className="pipeline-section">
                    <h3>🏢 Business Model</h3>
                    <div className="data-block">
                      <strong>Core Offer:</strong>
                      <p>{result.business_model?.core_offer}</p>
                    </div>
                    <div className="data-block">
                      <strong>Delivery Model:</strong>
                      <p>{result.business_model?.delivery_model}</p>
                    </div>
                    <div className="data-block">
                      <strong>Retention Model:</strong>
                      <p>{result.business_model?.retention_model}</p>
                    </div>
                    <div className="data-block">
                      <strong>Expansion Model:</strong>
                      <p>{result.business_model?.expansion_model}</p>
                    </div>
                  </div>
                )}

                {activeTab === "execution" && (
                  <div className="pipeline-section">
                    <h3>📋 Execution Plan</h3>
                    <div className="data-block">
                      <strong>Phase 1:</strong>
                      {renderList(result.execution_plan?.phase_1)}
                    </div>
                    <div className="data-block">
                      <strong>Phase 2:</strong>
                      {renderList(result.execution_plan?.phase_2)}
                    </div>
                    <div className="data-block">
                      <strong>Phase 3:</strong>
                      {renderList(result.execution_plan?.phase_3)}
                    </div>
                    <div className="data-block">
                      <strong>Critical Path:</strong>
                      {renderList(result.execution_plan?.critical_path)}
                    </div>
                  </div>
                )}

                {activeTab === "forecast" && (
                  <div className="pipeline-section">
                    <h3>📈 Forecast</h3>
                    <div className="data-block">
                      <strong>Revenue Projection:</strong>
                      <p>{result.forecast?.revenue_projection}</p>
                    </div>
                    <div className="data-block">
                      <strong>Growth Drivers:</strong>
                      {renderList(result.forecast?.growth_drivers)}
                    </div>
                    <div className="data-block">
                      <strong>Risks:</strong>
                      {renderList(result.forecast?.risks)}
                    </div>
                    <div className="data-block">
                      <strong>Mitigations:</strong>
                      {renderList(result.forecast?.mitigations)}
                    </div>
                  </div>
                )}

                {activeTab === "marketing" && (
                  <div className="pipeline-section">
                    <h3>📣 Marketing Funnel</h3>
                    <div className="data-block">
                      <strong>Top of Funnel (TOFU):</strong>
                      {renderList(result.marketing_funnel?.top_of_funnel)}
                    </div>
                    <div className="data-block">
                      <strong>Middle of Funnel (MOFU):</strong>
                      {renderList(result.marketing_funnel?.middle_of_funnel)}
                    </div>
                    <div className="data-block">
                      <strong>Bottom of Funnel (BOFU):</strong>
                      {renderList(result.marketing_funnel?.bottom_of_funnel)}
                    </div>
                  </div>
                )}

                {activeTab === "launch" && (
                  <div className="pipeline-section">
                    <h3>🚀 Launch Strategy</h3>
                    <div className="data-block">
                      <strong>Pre-Launch:</strong>
                      {renderList(result.launch_strategy?.pre_launch)}
                    </div>
                    <div className="data-block">
                      <strong>Launch:</strong>
                      {renderList(result.launch_strategy?.launch)}
                    </div>
                    <div className="data-block">
                      <strong>Post-Launch:</strong>
                      {renderList(result.launch_strategy?.post_launch)}
                    </div>
                  </div>
                )}

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
