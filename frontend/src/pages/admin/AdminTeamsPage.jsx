/**
 * Admin Teams Page
 * Team management interface (system admin only)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageLoading } from '../../components/ui/LoadingState';
import { getErrorMessage } from '../../components/ui/ErrorMessage';

const AdminTeamsPage = () => {
  const { authAxios, user } = useAuth();
  const navigate = useNavigate();

  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(50);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');

  const fetchTeams = useCallback(async () => {
    if (user?.system_role !== 'admin') {
      navigate('/');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams({
        skip: ((page - 1) * limit).toString(),
        limit: limit.toString(),
        ...(search && { search })
      });

      const res = await authAxios().get(`/admin/teams?${params}`);
      setTeams(res.data);

      // Get total count for pagination
      const countRes = await authAxios().get('/admin/teams/count');
      setTotal(countRes.data.total || 0);
    } catch (e) {
      if (e.response?.status === 403) {
        setError('You do not have permission to access this page.');
        navigate('/');
      } else {
        setError(getErrorMessage(e));
      }
    } finally {
      setLoading(false);
    }
  }, [authAxios, user, navigate, page, limit, search]);

  useEffect(() => {
    fetchTeams();
  }, [fetchTeams]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1); // Reset to first page when search changes
  };

  if (loading) {
    return <PageLoading message="Loading teams..." />;
  }

  if (error) {
    return (
      <div className="page-container" data-testid="admin-teams-error">
        <div className="admin-error-card">
          <h2>Error</h2>
          <p>{error}</p>
          <button className="btn-primary" onClick={() => navigate('/admin/overview')}>
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / limit) || 1;
  const startIndex = (page - 1) * limit + 1;
  const endIndex = Math.min(page * limit, total);

  return (
    <div className="page-container" data-testid="admin-teams-page">
      <header className="page-header">
        <h1>Team Management</h1>
        <p className="subtitle">Manage teams and their members</p>
        <div className="admin-actions">
          <button
            className="btn-secondary"
            onClick={() => navigate('/admin/overview')}
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <div className="admin-controls">
        <input
          type="text"
          placeholder="Search teams by name..."
          value={search}
          onChange={handleSearchChange}
          className="admin-search-input"
          data-testid="admin-team-search"
        />
      </div>

      {teams.length === 0 ? (
        <div className="admin-empty-state" data-testid="admin-teams-empty">
          <span className="empty-icon">🏢</span>
          <p className="empty-title">No teams found</p>
          <p className="empty-desc">
            {search
              ? 'Try adjusting your search criteria.'
              : 'No teams have been created yet.'}
          </p>
        </div>
      ) : (
        <div className="admin-teams-table">
          <div className="admin-table-header">
            <div className="table-header-cell">Team ID</div>
            <div className="table-header-cell">Name</div>
            <div className="table-header-cell">Slug</div>
            <div className="table-header-cell">Type</div>
            <div className="table-header-cell">Owner</div>
            <div className="table-header-cell">Members</div>
            <div className="table-header-cell">Status</div>
            <div className="table-header-cell">Created</div>
          </div>

          <div className="admin-table-body">
            {teams.map((team) => (
              <div key={team.id} className="admin-table-row">
                <div className="table-cell">{team.id}</div>
                <div className="table-cell">{team.name}</div>
                <div className="table-cell">{team.slug}</div>
                <div className="table-cell">{team.type}</div>
                <div className="table-cell">
                  {team.owner_id} {/* Would ideally show owner name */}
                </div>
                <div className="table-cell">{team.member_count || 0}</div>
                <div className="table-cell">
                  {team.is_active ? (
                    <span className="status-active">Active</span>
                  ) : (
                    <span className="status-inactive">Inactive</span>
                  )}
                </div>
                <div className="table-cell">
                  {new Date(team.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="admin-pagination">
        <p className="pagination-info">
          Showing {startIndex}-{endIndex} of {total} teams
        </p>
        <div className="pagination-controls">
          <button
            onClick={() => page > 1 && handlePageChange(page - 1)}
            disabled={page === 1}
            className="btn-pagination"
            data-testid="prev-page="prev"
          >
            ‹ Previous
          </button>
          <span className="page-info">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => page < totalPages && handlePageChange(page + 1)}
            disabled={page === totalPages}
            className="btn-pagination"
            data-page="next"
          >
            Next ›
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminTeamsPage;