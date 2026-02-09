import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend,
  AreaChart, Area
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Custom colors for charts
const COLORS = {
  green: "#00d4aa",
  blue: "#4d9fff",
  purple: "#a855f7",
  orange: "#ff9f43",
  red: "#ff6b6b",
  teal: "#14b8a6",
  pink: "#ec4899",
  yellow: "#eab308"
};

const CHART_COLORS = [
  COLORS.green, COLORS.blue, COLORS.purple, COLORS.orange,
  COLORS.teal, COLORS.pink, COLORS.yellow, COLORS.red
];

const AnalyticsPage = () => {
  // Data states
  const [engineUsage, setEngineUsage] = useState([]);
  const [engineLatency, setEngineLatency] = useState([]);
  const [engineErrors, setEngineErrors] = useState([]);
  const [driftStatus, setDriftStatus] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [pipelineGraph, setPipelineGraph] = useState(null);
  const [confidenceTrends, setConfidenceTrends] = useState([]);
  const [modelComparison, setModelComparison] = useState([]);
  const [realtimeStats, setRealtimeStats] = useState(null);
  
  // UI states
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("performance");
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch all analytics data
  const fetchAllData = useCallback(async () => {
    try {
      const [
        usageRes,
        latencyRes,
        errorsRes,
        driftRes,
        healthRes,
        graphRes,
        trendsRes,
        modelsRes,
        realtimeRes
      ] = await Promise.all([
        axios.get(`${API}/analytics/engine-usage`),
        axios.get(`${API}/analytics/engine-latency`),
        axios.get(`${API}/analytics/engine-errors`),
        axios.get(`${API}/analytics/drift-status`),
        axios.get(`${API}/analytics/system-health`),
        axios.get(`${API}/analytics/pipeline-graph`),
        axios.get(`${API}/analytics/confidence-trends`),
        axios.get(`${API}/analytics/model-comparison`),
        axios.get(`${API}/analytics/realtime-stats`)
      ]);

      setEngineUsage(usageRes.data);
      setEngineLatency(latencyRes.data);
      setEngineErrors(errorsRes.data);
      setDriftStatus(driftRes.data);
      setSystemHealth(healthRes.data);
      setPipelineGraph(graphRes.data);
      setConfidenceTrends(trendsRes.data);
      setModelComparison(modelsRes.data.models || []);
      setRealtimeStats(realtimeRes.data);
      setLastUpdate(new Date());
    } catch (e) {
      console.error("Failed to fetch analytics:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch realtime stats only (for polling)
  const fetchRealtimeOnly = useCallback(async () => {
    try {
      const [realtimeRes, healthRes] = await Promise.all([
        axios.get(`${API}/analytics/realtime-stats`),
        axios.get(`${API}/analytics/system-health`)
      ]);
      setRealtimeStats(realtimeRes.data);
      setSystemHealth(healthRes.data);
      setLastUpdate(new Date());
    } catch (e) {
      console.error("Realtime fetch error:", e);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Polling every 5 seconds
  useEffect(() => {
    const interval = setInterval(fetchRealtimeOnly, 5000);
    return () => clearInterval(interval);
  }, [fetchRealtimeOnly]);

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="analytics-tooltip">
          <p className="tooltip-label">{label}</p>
          {payload.map((p, i) => (
            <p key={i} className="tooltip-value" style={{ color: p.color }}>
              {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Gauge component for system metrics
  const GaugeCard = ({ label, value, max = 100, unit = "%", status }) => {
    const percentage = (value / max) * 100;
    const getColor = () => {
      if (percentage > 80) return COLORS.red;
      if (percentage > 60) return COLORS.orange;
      return COLORS.green;
    };

    return (
      <div className="gauge-card" data-testid={`gauge-${label.toLowerCase().replace(' ', '-')}`}>
        <div className="gauge-header">
          <span className="gauge-label">{label}</span>
          <span className={`gauge-status ${status || ''}`}></span>
        </div>
        <div className="gauge-ring">
          <svg viewBox="0 0 100 100">
            <circle className="gauge-bg" cx="50" cy="50" r="40" />
            <circle
              className="gauge-fill"
              cx="50" cy="50" r="40"
              style={{
                stroke: getColor(),
                strokeDasharray: `${percentage * 2.51} 251`
              }}
            />
          </svg>
          <div className="gauge-value">
            <span className="gauge-number">{value?.toFixed(1)}</span>
            <span className="gauge-unit">{unit}</span>
          </div>
        </div>
      </div>
    );
  };

  // Status indicator component
  const StatusIndicator = ({ status }) => {
    const colors = { green: COLORS.green, yellow: COLORS.orange, red: COLORS.red };
    return (
      <span 
        className="drift-indicator" 
        style={{ backgroundColor: colors[status] || COLORS.green }}
      />
    );
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-box">
          <div className="spinner"></div>
          <p>Loading analytics dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container analytics-page" data-testid="analytics-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <div className="header-content">
          <h1>📊 Monitoring & Analytics</h1>
          <p className="subtitle">Real-time system performance and AI quality metrics</p>
        </div>
        <div className="header-meta">
          <span className="live-indicator">
            <span className="live-dot"></span>
            LIVE
          </span>
          {lastUpdate && (
            <span className="last-update">
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </header>

      {/* Quick Stats Row */}
      <div className="stats-row quick-stats" data-testid="quick-stats">
        <div className="stat-card">
          <span className="stat-icon">📊</span>
          <div className="stat-content">
            <span className="stat-label">Total Executions</span>
            <span className="stat-value">{realtimeStats?.total_executions || 0}</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div className="stat-content">
            <span className="stat-label">Success Rate</span>
            <span className="stat-value">{realtimeStats?.success_rate || 0}%</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">⚡</span>
          <div className="stat-content">
            <span className="stat-label">Avg Latency</span>
            <span className="stat-value">{(realtimeStats?.avg_duration_ms / 1000)?.toFixed(1) || 0}s</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">🔥</span>
          <div className="stat-content">
            <span className="stat-label">Last 5 min</span>
            <span className="stat-value">{realtimeStats?.recent_5min?.count || 0} calls</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="analytics-tabs" data-testid="analytics-tabs">
        <button
          className={`tab-btn ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
          data-testid="tab-performance"
        >
          ⚙️ Engine Performance
        </button>
        <button
          className={`tab-btn ${activeTab === 'quality' ? 'active' : ''}`}
          onClick={() => setActiveTab('quality')}
          data-testid="tab-quality"
        >
          🎯 AI Quality & Drift
        </button>
        <button
          className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
          data-testid="tab-system"
        >
          🖥️ System Health
        </button>
      </div>

      {/* Tab Content */}
      <div className="analytics-content">
        {/* ENGINE PERFORMANCE TAB */}
        {activeTab === 'performance' && (
          <div className="tab-panel" data-testid="panel-performance">
            {/* Engine Usage Bar Chart */}
            <div className="chart-card large">
              <div className="chart-header">
                <h3>📈 Requests per Engine</h3>
                <span className="chart-subtitle">Total API calls by engine</span>
              </div>
              <div className="chart-body">
                {engineUsage.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={engineUsage} layout="vertical" margin={{ left: 120 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                      <XAxis type="number" stroke="#8888a0" />
                      <YAxis type="category" dataKey="display_name" stroke="#8888a0" width={110} tick={{ fontSize: 12 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="count" name="Requests" radius={[0, 4, 4, 0]}>
                        {engineUsage.map((entry, index) => (
                          <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-chart">No usage data available</div>
                )}
              </div>
            </div>

            {/* Latency Line Chart */}
            <div className="chart-card large">
              <div className="chart-header">
                <h3>⏱️ Average Response Time</h3>
                <span className="chart-subtitle">Latency in milliseconds per engine</span>
              </div>
              <div className="chart-body">
                {engineLatency.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={engineLatency} margin={{ left: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                      <XAxis dataKey="display_name" stroke="#8888a0" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                      <YAxis stroke="#8888a0" tickFormatter={(v) => `${(v/1000).toFixed(1)}s`} />
                      <Tooltip 
                        content={<CustomTooltip />}
                        formatter={(value) => [`${(value/1000).toFixed(2)}s`, 'Avg Latency']}
                      />
                      <Bar dataKey="avg_latency_ms" name="Avg Latency (ms)" fill={COLORS.blue} radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-chart">No latency data available</div>
                )}
              </div>
            </div>

            {/* Error Rate Table */}
            <div className="chart-card">
              <div className="chart-header">
                <h3>❌ Error Rates by Engine</h3>
                <span className="chart-subtitle">Error percentage and severity</span>
              </div>
              <div className="chart-body">
                {engineErrors.length > 0 ? (
                  <div className="error-table-container">
                    <table className="error-table" data-testid="error-table">
                      <thead>
                        <tr>
                          <th>Engine</th>
                          <th>Total Calls</th>
                          <th>Errors</th>
                          <th>Error Rate</th>
                          <th>Severity</th>
                        </tr>
                      </thead>
                      <tbody>
                        {engineErrors.map((e, i) => (
                          <tr key={i}>
                            <td>{e.display_name}</td>
                            <td>{e.total_calls}</td>
                            <td>{e.error_count}</td>
                            <td>{e.error_rate}%</td>
                            <td>
                              <span className={`severity-badge ${e.severity}`}>
                                {e.severity}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="empty-chart">No error data available</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* AI QUALITY & DRIFT TAB */}
        {activeTab === 'quality' && (
          <div className="tab-panel" data-testid="panel-quality">
            {/* Confidence Score Trends */}
            <div className="chart-card large">
              <div className="chart-header">
                <h3>📉 Confidence Score Trends</h3>
                <span className="chart-subtitle">AI confidence over the last 12 hours</span>
              </div>
              <div className="chart-body">
                {confidenceTrends.length > 0 ? (
                  <ResponsiveContainer width="100%" height={350}>
                    <AreaChart margin={{ left: 10, right: 30 }}>
                      <defs>
                        {confidenceTrends.map((trend, i) => (
                          <linearGradient key={i} id={`gradient-${i}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={CHART_COLORS[i % CHART_COLORS.length]} stopOpacity={0.3} />
                            <stop offset="95%" stopColor={CHART_COLORS[i % CHART_COLORS.length]} stopOpacity={0} />
                          </linearGradient>
                        ))}
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                      <XAxis 
                        dataKey="timestamp" 
                        stroke="#8888a0" 
                        tick={{ fontSize: 10 }}
                        tickFormatter={(t) => new Date(t).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        type="category"
                        allowDuplicatedCategory={false}
                      />
                      <YAxis stroke="#8888a0" domain={[0.5, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                      <Tooltip 
                        labelFormatter={(t) => new Date(t).toLocaleTimeString()}
                        formatter={(v) => [`${(v * 100).toFixed(1)}%`, 'Confidence']}
                      />
                      <Legend />
                      {confidenceTrends.map((trend, i) => (
                        <Area
                          key={i}
                          type="monotone"
                          data={trend.data_points}
                          dataKey="value"
                          name={trend.engine.replace(/_/g, ' ').replace('engine', '').trim()}
                          stroke={CHART_COLORS[i % CHART_COLORS.length]}
                          fill={`url(#gradient-${i})`}
                          strokeWidth={2}
                        />
                      ))}
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="empty-chart">No confidence data available</div>
                )}
              </div>
            </div>

            {/* Drift Alerts */}
            <div className="chart-card">
              <div className="chart-header">
                <h3>🚨 Drift Detection Alerts</h3>
                <span className="chart-subtitle">Real-time AI behavior monitoring</span>
              </div>
              <div className="chart-body">
                <div className="drift-grid" data-testid="drift-grid">
                  {driftStatus.length > 0 ? driftStatus.map((d, i) => (
                    <div key={i} className={`drift-card ${d.status}`}>
                      <div className="drift-header">
                        <StatusIndicator status={d.status} />
                        <span className="drift-engine">{d.engine.replace(/_/g, ' ').replace('engine', '')}</span>
                      </div>
                      <div className="drift-body">
                        <div className="drift-trend">
                          <span className="trend-label">Trend:</span>
                          <span className={`trend-value ${d.confidence_trend}`}>
                            {d.confidence_trend === 'rising' && '↑'}
                            {d.confidence_trend === 'falling' && '↓'}
                            {d.confidence_trend === 'stable' && '→'}
                            {d.confidence_trend}
                          </span>
                        </div>
                        <p className="drift-message">{d.message}</p>
                      </div>
                    </div>
                  )) : (
                    <div className="empty-chart">No drift data available</div>
                  )}
                </div>
              </div>
            </div>

            {/* Model Comparison */}
            <div className="chart-card">
              <div className="chart-header">
                <h3>🤖 Model Version Comparison</h3>
                <span className="chart-subtitle">Performance metrics across LLM models</span>
              </div>
              <div className="chart-body">
                <div className="model-table-container">
                  <table className="model-table" data-testid="model-table">
                    <thead>
                      <tr>
                        <th>Model</th>
                        <th>Provider</th>
                        <th>Avg Latency</th>
                        <th>Tokens/sec</th>
                        <th>Cost/1K</th>
                        <th>Primary Use</th>
                      </tr>
                    </thead>
                    <tbody>
                      {modelComparison.map((m, i) => (
                        <tr key={i}>
                          <td className="model-name">{m.name}</td>
                          <td>{m.provider}</td>
                          <td>{(m.avg_latency_ms / 1000).toFixed(1)}s</td>
                          <td>{m.tokens_per_second}</td>
                          <td>${m.cost_per_1k_tokens}</td>
                          <td className="model-use">{m.primary_use}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SYSTEM HEALTH TAB */}
        {activeTab === 'system' && (
          <div className="tab-panel" data-testid="panel-system">
            {/* System Gauges */}
            <div className="gauges-row">
              <GaugeCard 
                label="CPU Usage" 
                value={systemHealth?.cpu_usage || 0} 
                status={systemHealth?.status}
              />
              <GaugeCard 
                label="Memory" 
                value={systemHealth?.memory_usage || 0} 
                status={systemHealth?.status}
              />
              <GaugeCard 
                label="Disk" 
                value={systemHealth?.disk_usage || 0} 
                status={systemHealth?.status}
              />
            </div>

            {/* System Stats */}
            <div className="system-stats-row">
              <div className="system-stat-card">
                <div className="system-stat-icon">🔗</div>
                <div className="system-stat-content">
                  <span className="system-stat-value">{systemHealth?.active_connections || 0}</span>
                  <span className="system-stat-label">Active Connections</span>
                </div>
              </div>
              <div className="system-stat-card">
                <div className="system-stat-icon">⏰</div>
                <div className="system-stat-content">
                  <span className="system-stat-value">{systemHealth?.uptime_hours?.toFixed(1) || 0}h</span>
                  <span className="system-stat-label">Uptime</span>
                </div>
              </div>
              <div className="system-stat-card">
                <div className="system-stat-icon">📡</div>
                <div className="system-stat-content">
                  <span className={`system-stat-value ${systemHealth?.status}`}>
                    {systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
                  </span>
                  <span className="system-stat-label">System Status</span>
                </div>
              </div>
            </div>

            {/* Pipeline Visualization */}
            <div className="chart-card large">
              <div className="chart-header">
                <h3>🔄 Active Pipelines</h3>
                <span className="chart-subtitle">Current pipeline flow and throughput</span>
              </div>
              <div className="chart-body">
                <div className="pipeline-stats">
                  <div className="pipeline-stat">
                    <span className="pipeline-stat-value">{pipelineGraph?.active_pipelines || 0}</span>
                    <span className="pipeline-stat-label">Active Pipelines</span>
                  </div>
                  <div className="pipeline-stat">
                    <span className="pipeline-stat-value">{pipelineGraph?.queue_length || 0}</span>
                    <span className="pipeline-stat-label">Queue Length</span>
                  </div>
                  <div className="pipeline-stat">
                    <span className="pipeline-stat-value">{pipelineGraph?.throughput_per_minute || 0}/min</span>
                    <span className="pipeline-stat-label">Throughput</span>
                  </div>
                </div>
                
                {/* Simple Pipeline Flow */}
                <div className="pipeline-flow" data-testid="pipeline-flow">
                  {pipelineGraph?.nodes?.map((node, i) => (
                    <div key={node.id} className="pipeline-flow-item">
                      <div className={`flow-node ${node.type} ${node.status}`}>
                        <span className="flow-node-icon">
                          {node.type === 'input' && '📥'}
                          {node.type === 'output' && '📤'}
                          {node.type === 'engine' && '⚙️'}
                        </span>
                        <span className="flow-node-name">{node.name}</span>
                      </div>
                      {i < pipelineGraph.nodes.length - 1 && (
                        <span className="flow-connector">→</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
