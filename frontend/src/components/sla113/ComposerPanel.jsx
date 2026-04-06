import { useState } from "react";
import axios from "axios";
import { Package, CircleNotch } from "@phosphor-icons/react";
import { API, NoProjectSelected } from "./constants";

const ComposerPanel = ({ project }) => {
  const [outputFormat, setOutputFormat] = useState("json");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!project) return <NoProjectSelected />;

  const compose = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API}/compose`, { project_id: project.id, include_vision: true, include_logic: true, output_format: outputFormat });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sla-panel" data-testid="composer-panel">
      <div className="sla-panel-header">
        <div>
          <h2 className="sla-panel-title"><Package size={24} weight="bold" /> COMPOSER</h2>
          <p className="sla-panel-subtitle">Assemble game bundle for: {project.name}</p>
        </div>
      </div>
      <div className="sla-engine-controls">
        <div className="sla-control-group">
          <label className="sla-label">OUTPUT FORMAT</label>
          <div className="sla-btn-group">
            {["json", "html5", "specification"].map((f) => (
              <button key={f} className={`sla-btn-sm ${outputFormat === f ? "active" : ""}`} onClick={() => setOutputFormat(f)}>{f.toUpperCase()}</button>
            ))}
          </div>
        </div>
        <button className="sla-btn primary sla-generate-btn" onClick={compose} disabled={loading} data-testid="compose-btn">
          {loading ? <><CircleNotch size={16} className="sla-spin" /> COMPOSING...</> : <><Package size={16} weight="fill" /> COMPOSE BUNDLE</>}
        </button>
      </div>
      {error && <div className="sla-error" data-testid="composer-error">{error}</div>}
      {result && (
        <div className="sla-result" data-testid="composer-result">
          <div className="sla-result-header">
            <span className="sla-tag success">COMPOSED</span>
            <span className="sla-meta">{result.generation_time}s</span>
          </div>
          <pre className="sla-json-output">{JSON.stringify(result.bundle, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default ComposerPanel;
