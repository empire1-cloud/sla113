import { useState } from "react";
import axios from "axios";
import { Eye, CircleNotch, Sparkle } from "@phosphor-icons/react";
import { API, ASSET_TYPES, STYLES, NoProjectSelected } from "./constants";

const VisionPanel = ({ project }) => {
  const [assetType, setAssetType] = useState("sprites");
  const [style, setStyle] = useState("pixel_art");
  const [count, setCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!project) return <NoProjectSelected />;

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API}/vision/generate`, { project_id: project.id, asset_type: assetType, style, count });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sla-panel" data-testid="vision-panel">
      <div className="sla-panel-header">
        <div>
          <h2 className="sla-panel-title"><Eye size={24} weight="bold" /> VISION ENGINE</h2>
          <p className="sla-panel-subtitle">Generate visual assets for: {project.name}</p>
        </div>
      </div>
      <div className="sla-engine-controls">
        <div className="sla-control-row">
          <div className="sla-control-group">
            <label className="sla-label">ASSET TYPE</label>
            <div className="sla-btn-group">
              {ASSET_TYPES.map((t) => (
                <button key={t} className={`sla-btn-sm ${assetType === t ? "active" : ""}`} onClick={() => setAssetType(t)}>{t.toUpperCase()}</button>
              ))}
            </div>
          </div>
          <div className="sla-control-group">
            <label className="sla-label">STYLE</label>
            <div className="sla-btn-group">
              {STYLES.map((s) => (
                <button key={s} className={`sla-btn-sm ${style === s ? "active" : ""}`} onClick={() => setStyle(s)}>{s.replace("_", " ").toUpperCase()}</button>
              ))}
            </div>
          </div>
          <div className="sla-control-group">
            <label className="sla-label">COUNT: {count}</label>
            <input type="range" min={1} max={15} value={count} onChange={(e) => setCount(+e.target.value)} className="sla-range" />
          </div>
        </div>
        <button className="sla-btn primary sla-generate-btn" onClick={generate} disabled={loading} data-testid="vision-generate-btn">
          {loading ? <><CircleNotch size={16} className="sla-spin" /> GENERATING...</> : <><Sparkle size={16} weight="fill" /> GENERATE ASSETS</>}
        </button>
      </div>
      {error && <div className="sla-error" data-testid="vision-error">{error}</div>}
      {result && (
        <div className="sla-result" data-testid="vision-result">
          <div className="sla-result-header">
            <span className="sla-tag success">GENERATED</span>
            <span className="sla-meta">{result.generation_time}s</span>
          </div>
          <div className="sla-assets-grid">
            {result.assets?.map((asset, i) => (
              <div key={i} className="sla-asset-card" data-testid={`vision-asset-${i}`}>
                <div className="sla-asset-header">
                  <h4>{asset.name || `Asset ${i + 1}`}</h4>
                  <span className="sla-tag">{asset.type || assetType}</span>
                </div>
                <p className="sla-asset-desc">{asset.description}</p>
                {asset.color_palette && (
                  <div className="sla-palette">
                    {asset.color_palette.map((c, j) => (<span key={j} className="sla-color-dot" style={{ background: c }} title={c} />))}
                  </div>
                )}
                {asset.dimensions && <span className="sla-meta">{asset.dimensions.width}x{asset.dimensions.height}px</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VisionPanel;
