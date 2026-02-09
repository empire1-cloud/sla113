import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { AdminOnly } from "../components/RoleGate";

const ExecutionHistoryPage = () => {
  const { authAxios, currentTeam } = useAuth();
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [search, setSearch] = useState("");
  const [engineFilter, setEngineFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [page, setPage] = useState(0);
  const [expandedLog, setExpandedLog] = useState(null);
  
  const limit = 20;

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append("limit", limit);
      params.append("offset", page * limit);
      if (search) params.append("search", search);
      if (engineFilter) params.append("engine", engineFilter);
      if (statusFilter) params.append("status", statusFilter);
      if (sourceFilter) params.append("source", sourceFilter);
      
      const res = await authAxios().get(`/history?${params.toString()}`);
      setLogs(res.data.logs);
      setTotal(res.data.total);
    } catch (e) {
      console.error(e);
      setLogs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [authAxios, search, engineFilter, statusFilter, sourceFilter, page]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await authAxios().get(`/history/stats`);
      setStats(res.data);
    } catch (e) {
      console.error(e);
    }
  }, [authAxios]);

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [fetchLogs, fetchStats, currentTeam]);

  const clearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear all execution history?")) return;
    try {
      await authAxios().delete(`/history/clear`);
      fetchLogs();
      fetchStats();
    } catch (e) {
      console.error(e);
    }
  };

  const formatDuration = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatTimestamp = (ts) => {
    const date = new Date(ts);
    return date.toLocaleString();
  };

  const getEngineIcon = (engine) => {
    const icons = {
      strategy_engine: "🎯",
      plan_builder_engine: "📋",
      analysis_engine: "🔍",
      opportunity_mapper_engine: "💡",
      evaluator_engine: "⚖️",
      pricing_engine: "💰",
      blueprint_engine: "🏗️",
      persona_engine: "👤",
      anime_character_engine: "🎨",
      anime_lore_engine: "📚",
      anime_story_engine: "📖",
      art_direction_engine: "🖼️",
      money_pipeline_engine: "💵",
      pipeline_composer_engine: "🔗",
      hybrid_intelligence_core: "🧠",
      routing_engine: "🔀"
    };
    return icons[engine] || "⚙️";
  };

  const formatEngineName = (name) => {
    return name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  };

  const uniqueEngines = [...new Set(logs.map(l => l.engine))];

  return (
    <div className="page-container" data-testid="history-page">
      <header className="page-header">
        <Link to="/" className="back-link">← Home</Link>
        <h1>📜 Execution History</h1>
        <p className="subtitle">Log of all engine calls and pipeline runs</p>
      </header>

      {/* Stats Cards */}
      {stats && (
        <div className="stats-row" data-testid="stats-row">
          <div className="stat-card">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <span className="stat-label">Total Executions</span>
              <span className="stat-value">{stats.total_executions}</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">✅</span>
            <div className="stat-content">
              <span className="stat-label">Success Rate</span>
              <span className="stat-value">{stats.success_rate}%</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">⏱️</span>
            <div className="stat-content">
              <span className="stat-label">Avg Duration</span>
              <span className="stat-value">{formatDuration(stats.avg_duration_ms)}</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">❌</span>
            <div className="stat-content">
              <span className="stat-label">Errors</span>
              <span className="stat-value">{stats.error_count}</span>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="history-filters" data-testid="filters">
        <div className="filter-row">
          <input
            type="text"
            placeholder="Search logs..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            className="filter-search"
            data-testid="search-input"
          />
          
          <select 
            value={engineFilter} 
            onChange={(e) => { setEngineFilter(e.target.value); setPage(0); }}
            className="filter-select"
            data-testid="engine-filter"
          >
            <option value="">All Engines</option>
            {stats?.engines && Object.keys(stats.engines).map(engine => (
              <option key={engine} value={engine}>
                {getEngineIcon(engine)} {formatEngineName(engine)} ({stats.engines[engine]})
              </option>
            ))}
          </select>
          
          <select 
            value={statusFilter} 
            onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            className="filter-select"
            data-testid="status-filter"
          >
            <option value="">All Status</option>
            <option value="success">✅ Success</option>
            <option value="error">❌ Error</option>
          </select>
          
          <select 
            value={sourceFilter} 
            onChange={(e) => { setSourceFilter(e.target.value); setPage(0); }}
            className="filter-select"
            data-testid="source-filter"
          >
            <option value="">All Sources</option>
            <option value="api">API Call</option>
            <option value="pipeline">Pipeline</option>
          </select>
          
          <AdminOnly>
            <button className="filter-clear-btn" onClick={clearHistory} data-testid="clear-btn">
              🗑️ Clear All
            </button>
          </AdminOnly>
        </div>
        
        <div className="filter-info">
          Showing {logs.length} of {total} logs
        </div>
      </div>

      {/* Logs Table */}
      <div className="history-table-container">
        {loading ? (
          <div className="loading-box">
            <div className="spinner"></div>
          </div>
        ) : logs.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📜</span>
            <h3>No Execution Logs</h3>
            <p>Run some engines to see execution history here</p>
          </div>
        ) : (
          <table className="history-table" data-testid="history-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Engine</th>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Source</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <>
                  <tr key={log.id} className={`log-row ${log.status}`} data-testid={`log-${log.id}`}>
                    <td className="timestamp-cell">{formatTimestamp(log.created_at)}</td>
                    <td className="engine-cell">
                      <span className="engine-icon">{getEngineIcon(log.engine)}</span>
                      {formatEngineName(log.engine)}
                    </td>
                    <td className="endpoint-cell">
                      <code>{log.pipeline_id ? `Pipeline: ${log.pipeline_id}` : 'Direct API'}</code>
                    </td>
                    <td className="status-cell">
                      <span className={`status-badge ${log.status}`}>
                        {log.status === "success" ? "✅" : "❌"} {log.status}
                      </span>
                    </td>
                    <td className="duration-cell">{formatDuration(log.duration_ms)}</td>
                    <td className="source-cell">
                      <span className={`source-badge ${log.source}`}>
                        {log.source === "pipeline" ? "🔗" : "🌐"} {log.source}
                      </span>
                    </td>
                    <td className="action-cell">
                      <button
                        className="expand-btn"
                        onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                        data-testid={`expand-${log.id}`}
                      >
                        {expandedLog === log.id ? "▼" : "▶"}
                      </button>
                    </td>
                  </tr>
                  {expandedLog === log.id && (
                    <tr className="expanded-row">
                      <td colSpan={7}>
                        <div className="log-details">
                          <div className="detail-section">
                            <h4>📥 Input</h4>
                            <pre>{log.input_summary || 'N/A'}</pre>
                          </div>
                          {log.output_summary && (
                            <div className="detail-section">
                              <h4>📤 Output</h4>
                              <pre>{log.output_summary}</pre>
                            </div>
                          )}
                          {log.error_message && (
                            <div className="detail-section error">
                              <h4>❌ Error</h4>
                              <pre>{log.error_message}</pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {total > limit && (
        <div className="pagination" data-testid="pagination">
          <button 
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
            className="page-btn"
          >
            ← Previous
          </button>
          <span className="page-info">
            Page {page + 1} of {Math.ceil(total / limit)}
          </span>
          <button 
            onClick={() => setPage(p => p + 1)}
            disabled={(page + 1) * limit >= total}
            className="page-btn"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
};

export default ExecutionHistoryPage;
