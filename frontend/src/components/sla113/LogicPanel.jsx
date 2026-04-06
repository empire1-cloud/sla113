import { useState } from "react";
import axios from "axios";
import { Cpu, CircleNotch, Lightning } from "@phosphor-icons/react";
import { API, LOGIC_TYPES, NoProjectSelected } from "./constants";

const LogicPanel = ({ project }) => {
  const [logicType, setLogicType] = useState("mechanics");
  const [difficulty, setDifficulty] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!project) return <NoProjectSelected />;

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API}/logic/generate`, { project_id: project.id, logic_type: logicType, difficulty });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sla-panel" data-testid="logic-panel">
      <div className="sla-panel-header">
        <div>
          <h2 className="sla-panel-title"><Cpu size={24} weight="bold" /> LOGIC ENGINE</h2>
          <p className="sla-panel-subtitle">Generate game math for: {project.name}</p>
        </div>
      </div>
      <div className="sla-engine-controls">
        <div className="sla-control-row">
          <div className="sla-control-group">
            <label className="sla-label">LOGIC TYPE</label>
            <div className="sla-btn-group">
              {LOGIC_TYPES.map((t) => (
                <button key={t} className={`sla-btn-sm ${logicType === t ? "active" : ""}`} onClick={() => setLogicType(t)}>{t.toUpperCase()}</button>
              ))}
            </div>
          </div>
          <div className="sla-control-group">
            <label className="sla-label">DIFFICULTY</label>
            <div className="sla-btn-group">
              {["easy", "medium", "hard", "progressive"].map((d) => (
                <button key={d} className={`sla-btn-sm ${difficulty === d ? "active" : ""}`} onClick={() => setDifficulty(d)}>{d.toUpperCase()}</button>
              ))}
            </div>
          </div>
        </div>
        <button className="sla-btn primary sla-generate-btn" onClick={generate} disabled={loading} data-testid="logic-generate-btn">
          {loading ? <><CircleNotch size={16} className="sla-spin" /> COMPUTING...</> : <><Lightning size={16} weight="fill" /> GENERATE LOGIC</>}
        </button>
      </div>
      {error && <div className="sla-error" data-testid="logic-error">{error}</div>}
      {result && (
        <div className="sla-result" data-testid="logic-result">
          <div className="sla-result-header">
            <span className="sla-tag success">COMPUTED</span>
            <span className="sla-meta">{result.generation_time}s</span>
          </div>
          <pre className="sla-json-output">{JSON.stringify(result.specs, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default LogicPanel;
