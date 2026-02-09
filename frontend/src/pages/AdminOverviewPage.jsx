/**
 * Admin Overview Page
 * System administration dashboard (system admin only)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { PageLoading } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { getErrorMessage } from '../components/ui/ErrorMessage';

const AdminOverviewPage = () => {
  const { authAxios, user } = useAuth();
  const navigate = useNavigate();
  
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      const res = await authAxios().get('/admin/overview');
      setStats(res.data);
    } catch (e) {
      if (e.response?.status === 403) {
        setError('You do not have permission to access this page.');
      } else {
        setError(getErrorMessage(e));
      }
    } finally {
      setLoading(false);
    }
  }, [authAxios]);

  useEffect(() => {
    // Check if user is system admin
    if (user && user.system_role !== 'admin') {
      navigate('/');
      return;
    }
    fetchStats();
  }, [fetchStats, user, navigate]);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return <PageLoading message="Loading admin dashboard..." />;
  }

  if (error) {
    return (
      <div className="page-container" data-testid="admin-error">
        <div className="admin-error-card">
          <h2>Access Denied</h2>
          <p>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/')}>
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" data-testid="admin-page">
      <header className="page-header">
        <h1>Admin Overview</h1>
        <p className="subtitle">System Administration</p>
      </header>

      <div className="admin-grid">
        {/* Stats Cards */}
        <div className="admin-stats-row">
          <div className="admin-stat-card" data-testid="stat-users">
            <div className="stat-icon">👥</div>
            <div className="stat-value">{stats?.total_users || 0}</div>
            <div className="stat-label">Total Users</div>
            {stats?.today_signups > 0 && (
              <div className="stat-today">+{stats.today_signups} today</div>
            )}
          </div>
          
          <div className="admin-stat-card" data-testid="stat-teams">
            <div className="stat-icon">🏢</div>
            <div className="stat-value">{stats?.total_teams || 0}</div>
            <div className="stat-label">Total Teams</div>
          </div>
          
          <div className="admin-stat-card" data-testid="stat-executions">
            <div className="stat-icon">⚡</div>
            <div className="stat-value">{stats?.total_executions || 0}</div>
            <div className="stat-label">Total Executions</div>
            {stats?.today_executions > 0 && (
              <div className="stat-today">+{stats.today_executions} today</div>
            )}
          </div>
        </div>

        {/* Recent Signups */}
        <section className="admin-card settings-card" data-testid="recent-signups">
          <div className="card-header">
            <h2>Recent Signups</h2>
          </div>
          <div className="card-body" style={{ padding: '1rem' }}>
            {!stats?.recent_signups?.length ? (
              <EmptyState
                icon="👋"
                title="No recent signups"
                description="New user registrations will appear here."
              />
            ) : (
              <div className="signups-list">
                {stats.recent_signups.map((signup, index) => (
                  <div key={index} className="signup-item" data-testid={`signup-${index}`}>
                    <div className="signup-info">
                      <span className="signup-name">{signup.name}</span>
                      <span className="signup-email">{signup.email}</span>
                    </div>
                    <span className="signup-time">{formatDate(signup.created_at)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default AdminOverviewPage;
