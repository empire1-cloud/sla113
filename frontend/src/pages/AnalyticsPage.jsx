import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast, Toaster } from "sonner";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, Legend,
  AreaChart, Area, LineChart, Line
} from "recharts";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const WS_URL = process.env.REACT_APP_BACKEND_URL?.replace('https://', 'wss://').replace('http://', 'ws://');

// Theme colors
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

// Thresholds for alerts
const THRESHOLDS = {
  cpu: { warning: 70, critical: 80 },
  memory: { warning: 80, critical: 90 },
  disk: { warning: 85, critical: 95 },
  drift: { warning: 0.7, critical: 0.5 }
};

// Default widget visibility
const DEFAULT_WIDGETS = {
  quickStats: true,
  engineUsage: true,
  engineLatency: true,
  errorRates: true,
  confidenceTrends: true,
  driftAlerts: true,
  modelComparison: true,
  systemGauges: true,
  detailedStats: true,
  systemStats: true,
  pipelineFlow: true
};

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
  const [sparklineData, setSparklineData] = useState({});
  
  // UI states
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("performance");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [connectionType, setConnectionType] = useState("polling"); // "websocket" | "polling"
  const [theme, setTheme] = useState(() => localStorage.getItem("analytics-theme") || "dark");
  const [widgets, setWidgets] = useState(() => {
    const saved = localStorage.getItem("analytics-widgets");
    return saved ? JSON.parse(saved) : DEFAULT_WIDGETS;
  });
  const [showSettings, setShowSettings] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [prevHealth, setPrevHealth] = useState(null);
  
  // WebSocket ref
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  
  // Alert check function
  const checkAlerts = useCallback((health, drift) => {
    const newAlerts = [];
    
    if (health) {
      if (health.cpu_usage > THRESHOLDS.cpu.critical) {
        newAlerts.push({ type: 'critical', metric: 'CPU', value: health.cpu_usage, threshold: THRESHOLDS.cpu.critical });
      } else if (health.cpu_usage > THRESHOLDS.cpu.warning) {
        newAlerts.push({ type: 'warning', metric: 'CPU', value: health.cpu_usage, threshold: THRESHOLDS.cpu.warning });
      }
      
      if (health.memory_usage > THRESHOLDS.memory.critical) {
        newAlerts.push({ type: 'critical', metric: 'Memory', value: health.memory_usage, threshold: THRESHOLDS.memory.critical });
      } else if (health.memory_usage > THRESHOLDS.memory.warning) {
        newAlerts.push({ type: 'warning', metric: 'Memory', value: health.memory_usage, threshold: THRESHOLDS.memory.warning });
      }
      
      if (health.disk_usage > THRESHOLDS.disk.critical) {
        newAlerts.push({ type: 'critical', metric: 'Disk', value: health.disk_usage, threshold: THRESHOLDS.disk.critical });
      } else if (health.disk_usage > THRESHOLDS.disk.warning) {
        newAlerts.push({ type: 'warning', metric: 'Disk', value: health.disk_usage, threshold: THRESHOLDS.disk.warning });
      }
    }
    
    if (drift) {
      drift.forEach(d => {
        if (d.status === 'red') {
          newAlerts.push({ type: 'critical', metric: 'Drift', engine: d.engine, message: d.message });
        } else if (d.status === 'yellow') {
          newAlerts.push({ type: 'warning', metric: 'Drift', engine: d.engine, message: d.message });
        }
      });
    }
    
    // Show toast for new critical alerts
    newAlerts.forEach(alert => {
      if (alert.type === 'critical') {
        toast.error(`🚨 ${alert.metric} Alert: ${alert.value ? `${alert.value.toFixed(1)}%` : alert.message}`, {
          duration: 5000,
        });
      }
    });
    
    setAlerts(newAlerts);
  }, []);

  // Update sparkline data
  const updateSparklines = useCallback((usage, latency) => {
    setSparklineData(prev => {
      const newData = { ...prev };
      const timestamp = Date.now();
      
      usage.forEach(u => {
        if (!newData[u.engine]) newData[u.engine] = { usage: [], latency: [] };
        newData[u.engine].usage = [...(newData[u.engine].usage || []).slice(-11), { t: timestamp, v: u.count }];
      });
      
      latency.forEach(l => {
        if (!newData[l.engine]) newData[l.engine] = { usage: [], latency: [] };
        newData[l.engine].latency = [...(newData[l.engine].latency || []).slice(-11), { t: timestamp, v: l.avg_latency_ms }];
      });
      
      return newData;
    });
  }, []);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!WS_URL) return;
    
    try {
      const ws = new WebSocket(`${WS_URL}/api/analytics/ws`);
      
      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnectionType("websocket");
        toast.success("🔌 Real-time connection established", { duration: 2000 });
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'realtime') {
            setRealtimeStats(data.stats);
            setSystemHealth(data.health);
            setLastUpdate(new Date());
            checkAlerts(data.health, driftStatus);
          } else if (data.type === 'drift_alert') {
            toast.warning(`⚠️ Drift Alert: ${data.engine}`, { duration: 4000 });
            setDriftStatus(prev => prev.map(d => 
              d.engine === data.engine ? { ...d, status: data.status, message: data.message } : d
            ));
          }
        } catch (e) {
          console.error("WebSocket message parse error:", e);
        }
      };
      
      ws.onclose = () => {
        console.log("WebSocket disconnected, falling back to polling");
        setConnectionType("polling");
        wsRef.current = null;
        // Reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
      };
      
      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        ws.close();
      };
      
      wsRef.current = ws;
    } catch (e) {
      console.error("WebSocket connection failed:", e);
      setConnectionType("polling");
    }
  }, [checkAlerts, driftStatus]);

  // Fetch all analytics data
  const fetchAllData = useCallback(async () => {
    try {
      const [
        usageRes, latencyRes, errorsRes, driftRes,
        healthRes, graphRes, trendsRes, modelsRes, realtimeRes
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
      
      updateSparklines(usageRes.data, latencyRes.data);
      checkAlerts(healthRes.data, driftRes.data);
    } catch (e) {
      console.error("Failed to fetch analytics:", e);
      toast.error("Failed to fetch analytics data");
    } finally {
      setLoading(false);
    }
  }, [checkAlerts, updateSparklines]);

  // Fetch realtime stats only (for polling fallback)
  const fetchRealtimeOnly = useCallback(async () => {
    if (connectionType === "websocket" && wsRef.current?.readyState === WebSocket.OPEN) return;
    
    try {
      const [realtimeRes, healthRes, driftRes] = await Promise.all([
        axios.get(`${API}/analytics/realtime-stats`),
        axios.get(`${API}/analytics/system-health`),
        axios.get(`${API}/analytics/drift-status`)
      ]);
      
      setPrevHealth(systemHealth);
      setRealtimeStats(realtimeRes.data);
      setSystemHealth(healthRes.data);
      setDriftStatus(driftRes.data);
      setLastUpdate(new Date());
      checkAlerts(healthRes.data, driftRes.data);
    } catch (e) {
      console.error("Realtime fetch error:", e);
    }
  }, [connectionType, systemHealth, checkAlerts]);

  // Initial load
  useEffect(() => {
    fetchAllData();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
    };
  }, [fetchAllData, connectWebSocket]);

  // Polling every 5 seconds (fallback)
  useEffect(() => {
    const interval = setInterval(fetchRealtimeOnly, 5000);
    return () => clearInterval(interval);
  }, [fetchRealtimeOnly]);

  // Save theme preference
  useEffect(() => {
    localStorage.setItem("analytics-theme", theme);
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Save widget preferences
  useEffect(() => {
    localStorage.setItem("analytics-widgets", JSON.stringify(widgets));
  }, [widgets]);

  // Export functions
  const exportData = useCallback((format) => {
    const exportPayload = {
      exportedAt: new Date().toISOString(),
      engineUsage,
      engineLatency,
      engineErrors,
      driftStatus,
      systemHealth,
      confidenceTrends: confidenceTrends.map(t => ({
        engine: t.engine,
        currentConfidence: t.current_confidence,
        trend: t.trend
      }))
    };
    
    let content, filename, type;
    
    if (format === 'json') {
      content = JSON.stringify(exportPayload, null, 2);
      filename = `analytics-export-${Date.now()}.json`;
      type = 'application/json';
    } else {
      // CSV export
      const csvRows = [
        ['Category', 'Engine', 'Metric', 'Value'],
        ...engineUsage.map(e => ['Usage', e.engine, 'count', e.count]),
        ...engineLatency.map(e => ['Latency', e.engine, 'avg_ms', e.avg_latency_ms]),
        ...engineErrors.map(e => ['Errors', e.engine, 'error_rate', e.error_rate]),
        ...driftStatus.map(d => ['Drift', d.engine, 'status', d.status]),
        ['System', 'CPU', 'usage', systemHealth?.cpu_usage || 0],
        ['System', 'Memory', 'usage', systemHealth?.memory_usage || 0],
        ['System', 'Disk', 'usage', systemHealth?.disk_usage || 0]
      ];
      content = csvRows.map(r => r.join(',')).join('\n');
      filename = `analytics-export-${Date.now()}.csv`;
      type = 'text/csv';
    }
    
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Exported as ${format.toUpperCase()}`);
  }, [engineUsage, engineLatency, engineErrors, driftStatus, systemHealth, confidenceTrends]);

  // Toggle widget visibility
  const toggleWidget = (widgetKey) => {
    setWidgets(prev => ({ ...prev, [widgetKey]: !prev[widgetKey] }));
  };

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

  // Skeleton loader component
  const Skeleton = ({ className }) => (
    <div className={`skeleton-loader ${className || ''}`} />
  );

  // Gauge component with animation
  const GaugeCard = ({ label, value, max = 100, unit = "%", status, prevValue }) => {
    const percentage = (value / max) * 100;
    const getColor = () => {
      if (percentage > 80) return COLORS.red;
      if (percentage > 60) return COLORS.orange;
      return COLORS.green;
    };

    const isIncreasing = prevValue !== null && value > prevValue;
    const isDecreasing = prevValue !== null && value < prevValue;

    return (
      <div className="gauge-card" data-testid={`gauge-${label.toLowerCase().replace(' ', '-')}`}>
        <div className="gauge-header">
          <span className="gauge-label">{label}</span>
          <div className="gauge-header-right">
            {isIncreasing && <span className="trend-arrow up">↑</span>}
            {isDecreasing && <span className="trend-arrow down">↓</span>}
            <span className={`gauge-status ${status || ''}`}></span>
          </div>
        </div>
        <div className="gauge-ring">
          <svg viewBox="0 0 100 100">
            <circle className="gauge-bg" cx="50" cy="50" r="40" />
            <circle
              className="gauge-fill animated-gauge"
              cx="50" cy="50" r="40"
              style={{
                stroke: getColor(),
                strokeDasharray: `${percentage * 2.51} 251`
              }}
            />
          </svg>
          <div className="gauge-value">
            <span className={`gauge-number ${isIncreasing ? 'flash-up' : ''} ${isDecreasing ? 'flash-down' : ''}`}>
              {value?.toFixed(1)}
            </span>
            <span className="gauge-unit">{unit}</span>
          </div>
        </div>
      </div>
    );
  };

  // Mini sparkline component
  const MiniSparkline = ({ data, color = COLORS.blue, height = 30 }) => {
    if (!data || data.length < 2) return <span className="sparkline-empty">—</span>;
    
    return (
      <ResponsiveContainer width={80} height={height}>
        <LineChart data={data}>
          <Line 
            type="monotone" 
            dataKey="v" 
            stroke={color} 
            strokeWidth={1.5}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    );
  };

  // Status indicator component
  const StatusIndicator = ({ status }) => {
    const colors = { green: COLORS.green, yellow: COLORS.orange, red: COLORS.red };
    return (
      <span 
        className={`drift-indicator ${status === 'red' ? 'pulse-alert' : ''}`}
        style={{ backgroundColor: colors[status] || COLORS.green }}
      />
    );
  };

  // Settings modal
  const SettingsModal = () => (
    <div className="settings-modal-overlay" onClick={() => setShowSettings(false)}>
      <div className="settings-modal" onClick={e => e.stopPropagation()}>
        <div className="settings-header">
          <h3>⚙️ Dashboard Settings</h3>
          <button className="close-btn" onClick={() => setShowSettings(false)}>×</button>
        </div>
        <div className="settings-body">
          <div className="settings-section">
            <h4>🎨 Theme</h4>
            <div className="theme-toggle">
              <button 
                className={`theme-btn ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => setTheme('dark')}
              >
                🌙 Dark
              </button>
              <button 
                className={`theme-btn ${theme === 'light' ? 'active' : ''}`}
                onClick={() => setTheme('light')}
              >
                ☀️ Light
              </button>
            </div>
          </div>
          
          <div className="settings-section">
            <h4>📊 Visible Widgets</h4>
            <div className="widget-toggles">
              {Object.entries(widgets).map(([key, visible]) => (
                <label key={key} className="widget-toggle">
                  <input 
                    type="checkbox" 
                    checked={visible} 
                    onChange={() => toggleWidget(key)}
                  />
                  <span>{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                </label>
              ))}
            </div>
          </div>
          
          <div className="settings-section">
            <h4>📤 Export Data</h4>
            <div className="export-buttons">
              <button className="export-btn" onClick={() => exportData('json')}>
                📄 Export JSON
              </button>
              <button className="export-btn" onClick={() => exportData('csv')}>
                📊 Export CSV
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Alert banner component
  const AlertBanner = () => {
    const criticalAlerts = alerts.filter(a => a.type === 'critical');
    const warningAlerts = alerts.filter(a => a.type === 'warning');
    
    if (alerts.length === 0) return null;
    
    return (
      <div className="alert-banner" data-testid="alert-banner">
        {criticalAlerts.length > 0 && (
          <div className="alert-item critical">
            <span className="alert-icon">🚨</span>
            <span>{criticalAlerts.length} Critical Alert{criticalAlerts.length > 1 ? 's' : ''}</span>
          </div>
        )}
        {warningAlerts.length > 0 && (
          <div className="alert-item warning">
            <span className="alert-icon">⚠️</span>
            <span>{warningAlerts.length} Warning{warningAlerts.length > 1 ? 's' : ''}</span>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`page-container analytics-page ${theme}`} data-testid="analytics-loading">
        <Toaster position="top-right" theme={theme} />
        <header className="page-header">
          <Link to="/" className="back-link">← Home</Link>
          <div className="header-content">
            <h1>📊 Monitoring & Analytics</h1>
            <p className="subtitle">Loading dashboard...</p>
          </div>
        </header>
        <div className="skeleton-grid">
          <Skeleton className="skeleton-stat" />
          <Skeleton className="skeleton-stat" />
          <Skeleton className="skeleton-stat" />
          <Skeleton className="skeleton-stat" />
        </div>
        <Skeleton className="skeleton-chart" />
        <Skeleton className="skeleton-chart" />
      </div>
    );
  }

  return (
    <div className={`page-container analytics-page ${theme}`} data-testid="analytics-page">
      <Toaster position="top-right" theme={theme} richColors />
      
      {showSettings && <SettingsModal />}
      
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <div className="header-content">
          <h1>📊 Monitoring & Analytics</h1>
          <p className="subtitle">Real-time system performance and AI quality metrics</p>
        </div>
        <div className="header-actions">
          <div className={`connection-badge ${connectionType}`}>
            <span className={`conn-dot ${connectionType}`}></span>
            {connectionType === 'websocket' ? 'LIVE' : 'POLLING'}
          </div>
          {lastUpdate && (
            <span className="last-update" data-testid="last-update">
              Updated: {lastUpdate.toLocaleTimeString()}
            </span>
          )}
          <button className="settings-btn" onClick={() => setShowSettings(true)} data-testid="settings-btn">
            ⚙️
          </button>
        </div>
      </header>

      <AlertBanner />

      {/* Quick Stats Row */}
      {widgets.quickStats && (
        <div className="stats-row quick-stats" data-testid="quick-stats">
          <div className="stat-card animated-card">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <span className="stat-label">Total Executions</span>
              <span className="stat-value animate-value">{realtimeStats?.total_executions || 0}</span>
            </div>
          </div>
          <div className="stat-card animated-card">
            <span className="stat-icon">✅</span>
            <div className="stat-content">
              <span className="stat-label">Success Rate</span>
              <span className="stat-value animate-value">{realtimeStats?.success_rate || 0}%</span>
            </div>
          </div>
          <div className="stat-card animated-card">
            <span className="stat-icon">⚡</span>
            <div className="stat-content">
              <span className="stat-label">Avg Latency</span>
              <span className="stat-value animate-value">{(realtimeStats?.avg_duration_ms / 1000)?.toFixed(1) || 0}s</span>
            </div>
          </div>
          <div className="stat-card animated-card">
            <span className="stat-icon">🔥</span>
            <div className="stat-content">
              <span className="stat-label">Last 5 min</span>
              <span className="stat-value animate-value">{realtimeStats?.recent_5min?.count || 0} calls</span>
            </div>
          </div>
        </div>
      )}

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
            {widgets.engineUsage && (
              <div className="chart-card large animated-card">
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
            )}

            {/* Latency Chart with Sparklines */}
            {widgets.engineLatency && (
              <div className="chart-card large animated-card">
                <div className="chart-header">
                  <h3>⏱️ Average Response Time</h3>
                  <span className="chart-subtitle">Latency in milliseconds per engine</span>
                </div>
                <div className="chart-body">
                  {engineLatency.length > 0 ? (
                    <>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={engineLatency} margin={{ left: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a3a" />
                          <XAxis dataKey="display_name" stroke="#8888a0" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={80} />
                          <YAxis stroke="#8888a0" tickFormatter={(v) => `${(v/1000).toFixed(1)}s`} />
                          <Tooltip formatter={(value) => [`${(value/1000).toFixed(2)}s`, 'Avg Latency']} />
                          <Bar dataKey="avg_latency_ms" name="Avg Latency (ms)" fill={COLORS.blue} radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                      
                      {/* Sparkline table */}
                      <div className="sparkline-table">
                        <h4>📉 Recent Trends</h4>
                        <div className="sparkline-grid">
                          {engineLatency.slice(0, 6).map((e, i) => (
                            <div key={i} className="sparkline-item">
                              <span className="sparkline-name">{e.display_name}</span>
                              <MiniSparkline 
                                data={sparklineData[e.engine]?.latency} 
                                color={CHART_COLORS[i % CHART_COLORS.length]}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="empty-chart">No latency data available</div>
                  )}
                </div>
              </div>
            )}

            {/* Error Rate Table */}
            {widgets.errorRates && (
              <div className="chart-card animated-card">
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
                            <th>Total</th>
                            <th>Errors</th>
                            <th>Rate</th>
                            <th>Severity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {engineErrors.map((e, i) => (
                            <tr key={i} className="animated-row">
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
            )}
          </div>
        )}

        {/* AI QUALITY & DRIFT TAB */}
        {activeTab === 'quality' && (
          <div className="tab-panel" data-testid="panel-quality">
            {/* Confidence Score Trends */}
            {widgets.confidenceTrends && (
              <div className="chart-card large animated-card">
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
            )}

            {/* Drift Alerts */}
            {widgets.driftAlerts && (
              <div className="chart-card animated-card">
                <div className="chart-header">
                  <h3>🚨 Drift Detection Alerts</h3>
                  <span className="chart-subtitle">Real-time AI behavior monitoring</span>
                </div>
                <div className="chart-body">
                  <div className="drift-grid" data-testid="drift-grid">
                    {driftStatus.length > 0 ? driftStatus.map((d, i) => (
                      <div key={i} className={`drift-card ${d.status} ${d.status === 'red' ? 'alert-pulse' : ''}`}>
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
            )}

            {/* Model Comparison */}
            {widgets.modelComparison && (
              <div className="chart-card animated-card">
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
                          <tr key={i} className="animated-row">
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
            )}
          </div>
        )}

        {/* SYSTEM HEALTH TAB */}
        {activeTab === 'system' && (
          <div className="tab-panel" data-testid="panel-system">
            {/* Metrics Source Indicator */}
            <div className="metrics-source-banner" data-testid="metrics-source">
              <span className={`source-indicator ${systemHealth?.psutil_available ? 'real' : 'mock'}`}>
                {systemHealth?.psutil_available ? '🟢 Real Metrics (psutil)' : '🟡 Mock Metrics (psutil unavailable)'}
              </span>
              <span className={`connection-type ${connectionType}`}>
                {connectionType === 'websocket' ? '⚡ WebSocket' : '🔄 Polling (5s)'}
              </span>
            </div>

            {/* System Gauges */}
            {widgets.systemGauges && (
              <div className="gauges-row">
                <GaugeCard 
                  label="CPU Usage" 
                  value={systemHealth?.cpu_usage || 0} 
                  status={systemHealth?.status}
                  prevValue={prevHealth?.cpu_usage}
                />
                <GaugeCard 
                  label="Memory" 
                  value={systemHealth?.memory_usage || 0} 
                  status={systemHealth?.status}
                  prevValue={prevHealth?.memory_usage}
                />
                <GaugeCard 
                  label="Disk" 
                  value={systemHealth?.disk_usage || 0} 
                  status={systemHealth?.status}
                  prevValue={prevHealth?.disk_usage}
                />
              </div>
            )}

            {/* Detailed Memory & Disk Stats */}
            {widgets.detailedStats && (
              <div className="detailed-stats-row">
                <div className="detailed-stat-card animated-card">
                  <div className="detailed-stat-header">
                    <span className="detailed-stat-icon">🧠</span>
                    <span className="detailed-stat-title">Memory Details</span>
                  </div>
                  <div className="detailed-stat-body">
                    <div className="stat-row">
                      <span className="stat-key">Total:</span>
                      <span className="stat-val">{systemHealth?.memory_total_gb || 0} GB</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-key">Used:</span>
                      <span className="stat-val">{systemHealth?.memory_used_gb || 0} GB</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-key">Usage:</span>
                      <span className="stat-val highlight">{systemHealth?.memory_usage || 0}%</span>
                    </div>
                  </div>
                </div>
                <div className="detailed-stat-card animated-card">
                  <div className="detailed-stat-header">
                    <span className="detailed-stat-icon">💾</span>
                    <span className="detailed-stat-title">Disk Details</span>
                  </div>
                  <div className="detailed-stat-body">
                    <div className="stat-row">
                      <span className="stat-key">Total:</span>
                      <span className="stat-val">{systemHealth?.disk_total_gb || 0} GB</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-key">Used:</span>
                      <span className="stat-val">{systemHealth?.disk_used_gb || 0} GB</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-key">Usage:</span>
                      <span className="stat-val highlight">{systemHealth?.disk_usage || 0}%</span>
                    </div>
                  </div>
                </div>
                <div className="detailed-stat-card animated-card">
                  <div className="detailed-stat-header">
                    <span className="detailed-stat-icon">📊</span>
                    <span className="detailed-stat-title">Load Average</span>
                  </div>
                  <div className="detailed-stat-body">
                    {systemHealth?.load_average ? (
                      <>
                        <div className="stat-row">
                          <span className="stat-key">1 min:</span>
                          <span className="stat-val">{systemHealth.load_average[0]}</span>
                        </div>
                        <div className="stat-row">
                          <span className="stat-key">5 min:</span>
                          <span className="stat-val">{systemHealth.load_average[1]}</span>
                        </div>
                        <div className="stat-row">
                          <span className="stat-key">15 min:</span>
                          <span className="stat-val">{systemHealth.load_average[2]}</span>
                        </div>
                      </>
                    ) : (
                      <div className="stat-row">
                        <span className="stat-val muted">Not available</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* System Stats */}
            {widgets.systemStats && (
              <div className="system-stats-row">
                <div className="system-stat-card animated-card">
                  <div className="system-stat-icon">🔗</div>
                  <div className="system-stat-content">
                    <span className="system-stat-value animate-value">{systemHealth?.active_connections || 0}</span>
                    <span className="system-stat-label">Active Connections</span>
                  </div>
                </div>
                <div className="system-stat-card animated-card">
                  <div className="system-stat-icon">⏰</div>
                  <div className="system-stat-content">
                    <span className="system-stat-value animate-value">{systemHealth?.uptime_hours?.toFixed(1) || 0}h</span>
                    <span className="system-stat-label">Uptime</span>
                  </div>
                </div>
                <div className="system-stat-card animated-card">
                  <div className="system-stat-icon">📡</div>
                  <div className="system-stat-content">
                    <span className={`system-stat-value ${systemHealth?.status}`}>
                      {systemHealth?.status?.toUpperCase() || 'UNKNOWN'}
                    </span>
                    <span className="system-stat-label">System Status</span>
                  </div>
                </div>
              </div>
            )}

            {/* Pipeline Visualization */}
            {widgets.pipelineFlow && (
              <div className="chart-card large animated-card">
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
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;
