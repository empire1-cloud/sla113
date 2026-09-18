import { useCallback, useEffect, useMemo, useState } from "react";
import { useAuth } from "../context/AuthContext";

const COLORS = { gold: "#d4af37", pink: "#ff1493", cyan: "#00c8ff", bg: "#050505" };

export default function EconomicTruthPage() {
  const { authAxios, currentTeam } = useAuth();
  const [coverage, setCoverage] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!currentTeam?.id) return;
    setLoading(true);
    setError("");
    try {
      const api = authAxios();
      const [coverageResponse, metricsResponse, graphResponse] = await Promise.all([
        api.get("/economic-truth/coverage"),
        api.get(`/economic-truth/metrics/${currentTeam.id}`),
        api.get(`/economic-truth/graph/${currentTeam.id}`),
      ]);
      setCoverage(coverageResponse.data);
      setMetrics(metricsResponse.data);
      setGraph(graphResponse.data);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || requestError.message || "Economic Truth runtime unavailable");
    } finally {
      setLoading(false);
    }
  }, [authAxios, currentTeam?.id]);

  useEffect(() => { refresh(); }, [refresh]);

  const lastNodes = useMemo(() => (graph.nodes || []).slice(0, 18), [graph.nodes]);

  return (
    <div style={{ minHeight: "100vh", background: COLORS.bg, color: "#f5f5f5", padding: "28px" }}>
      <header style={{ display: "flex", justifyContent: "space-between", gap: 24, alignItems: "flex-start", marginBottom: 28 }}>
        <div>
          <div style={{ color: COLORS.gold, letterSpacing: 3, fontSize: 12 }}>EMPIRE-1 · ECONOMIC TRUTH LAYER</div>
          <h1 style={{ margin: "8px 0", fontSize: "clamp(30px,5vw,58px)" }}>Every Economic Action. Proven.</h1>
          <p style={{ color: "#aaa", maxWidth: 760 }}>Intent, authority, execution, ledger effect, settlement, provenance, verification, and reversal—one causal Receipt Graph.</p>
        </div>
        <button onClick={refresh} style={{ background: "transparent", color: COLORS.gold, border: `1px solid ${COLORS.gold}`, padding: "10px 16px", cursor: "pointer" }}>REFRESH PROOF</button>
      </header>

      {error && <div style={{ border: "1px solid #8b0000", background: "#210606", padding: 16, marginBottom: 20 }}><strong>FAIL-CLOSED:</strong> {error}</div>}
      {loading ? <p>Loading verified state…</p> : (
        <>
          <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(190px,1fr))", gap: 12, marginBottom: 22 }}>
            <Metric label="Coverage" value={coverage ? `${coverage.coverage_percent}%` : "—"} color={coverage?.claim_allowed ? COLORS.gold : "#ff5555"} />
            <Metric label="Receipts Issued" value={metrics?.receipts_issued ?? 0} color={COLORS.cyan} />
            <Metric label="Verified" value={metrics?.by_type?.verification ?? 0} color="#62ff9a" />
            <Metric label="Refused" value={metrics?.by_type?.refusal ?? 0} color="#ff5555" />
            <Metric label="Reversed" value={metrics?.by_type?.reversal ?? 0} color={COLORS.pink} />
          </section>

          <section style={{ display: "grid", gridTemplateColumns: "minmax(0,2fr) minmax(260px,1fr)", gap: 16 }}>
            <div style={panel}>
              <h2 style={{ marginTop: 0 }}>Receipt Graph</h2>
              {lastNodes.length === 0 ? <p style={{ color: "#777" }}>No economic receipts yet. The system will not invent activity.</p> :
                <div style={{ display: "grid", gap: 8 }}>
                  {lastNodes.map((node, index) => (
                    <div key={node.id} style={{ display: "grid", gridTemplateColumns: "26px minmax(0,1fr) auto", gap: 10, alignItems: "center", padding: 10, background: "#0b0b0b", borderLeft: `2px solid ${index === 0 ? COLORS.gold : "#333"}` }}>
                      <span style={{ color: COLORS.gold }}>●</span>
                      <div><strong>{node.type}</strong><div style={{ color: "#777", fontSize: 12 }}>{node.id}</div></div>
                      <span style={{ fontSize: 12, color: "#aaa" }}>{node.state}</span>
                    </div>
                  ))}
                </div>}
            </div>
            <div style={panel}>
              <h2 style={{ marginTop: 0 }}>Claim Gate</h2>
              <div style={{ fontSize: 28, color: coverage?.claim_allowed ? COLORS.gold : "#ff5555", marginBottom: 12 }}>
                {coverage?.claim_allowed ? "AUTHORIZED" : "REFUSED"}
              </div>
              <p style={{ color: "#aaa" }}>{coverage?.claim_allowed ? "Every registered economic surface is governed by the shared receipt contract." : "The public claim remains blocked until every required surface is enabled."}</p>
              {(coverage?.uncovered_surfaces || []).map((surface) => <div key={surface} style={{ padding: "7px 0", borderBottom: "1px solid #222", color: "#ff7777" }}>{surface}</div>)}
              <div style={{ marginTop: 18, color: "#777", fontSize: 12 }}>{coverage?.contract_version}</div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

function Metric({ label, value, color }) {
  return <div style={{ ...panel, padding: 18 }}><div style={{ color: "#777", fontSize: 11, letterSpacing: 2 }}>{label.toUpperCase()}</div><div style={{ fontSize: 30, color, marginTop: 8 }}>{value}</div></div>;
}
const panel = { border: "1px solid #202020", background: "linear-gradient(145deg,#101010,#070707)", padding: 20, boxShadow: "0 10px 40px rgba(0,0,0,.35)" };
