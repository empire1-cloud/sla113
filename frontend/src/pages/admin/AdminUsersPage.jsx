/**
 * Admin Users Page
 * User management interface (system admin only)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { PageLoading } from '../../components/ui/LoadingState';
import { getErrorMessage } from '../../components/ui/ErrorMessage';

const AdminUsersPage = () => {
  const { authAxios, user } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(50);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');

  const fetchUsers = useCallback(async () => {
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
        ...(roleFilter && { role: roleFilter }),
        ...(search && { search })
      });

      const res = await authAxios().get(`/admin/users?${params}`);
      setUsers(res.data);

      // Get total count for pagination
      const countRes = await authAxios().get('/admin/users/count');
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
  }, [authAxios, user, navigate, page, limit, search, roleFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleRoleChange = (e) => {
    setRoleFilter(e.target.value);
    setPage(1); // Reset to first page when filter changes
  };

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1); // Reset to first page when search changes
  };

  const handleRoleUpdate = async (userId, newRole) => {
    try {
      await authAxios().patch(`/admin/users/${userId}/role`, { role: newRole });
      // Refetch the user list to show updated role
      await fetchUsers();
    } catch (e) {
      setError(getErrorMessage(e));
    }
  };

  const handleStatusUpdate = async (userId, isActive) => {
    try {
      await authAxios().patch(`/admin/users/${userId}/status`, { is_active: isActive });
      // Refetch the user list to show updated status
      await fetchUsers();
    } catch (e) {
      setError(getErrorMessage(e));
    }
  };

  if (loading) {
    return <PageLoading message="Loading users..." />;
  }

  if (error) {
    return (
      <div className="page-container" data-testid="admin-users-error">
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
    <div className="page-container" data-testid="admin-users-page">
      <header className="page-header">
        <h1>User Management</h1>
        <p className="subtitle">Manage system users and their roles</p>
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
        <div className="admin-search-section">
          <input
            type="text"
            placeholder="Search users by email or name..."
            value={search}
            onChange={handleSearchChange}
            className="admin-search-input"
            data-testid="admin-user-search"
          />
          <select
            value={roleFilter}
            onChange={handleRoleChange}
            className="admin-role-filter"
            data-testid="admin-role-filter"
          >
            <option value="">All Roles</option>
            <option value="admin">Administrator</option>
            <option value="user">Standard User</option>
          </select>
        </div>
      </div>

      {users.length === 0 ? (
        <div className="admin-empty-state" data-testid="admin-users-empty">
          <span className="empty-icon">👥</span>
          <p className="empty-title">No users found</p>
          <p className="empty-desc">
            {search || roleFilter
              ? 'Try adjusting your search or filter criteria.'
              : 'No users registered in the system.'}
          </p>
        </div>
      ) : (
        <div className="admin-users-table">
          <div className="admin-table-header">
            <div className="table-header-cell">User ID</div>
            <div className="table-header-cell">Email</div>
            <div className="table-header-cell">Name</div>
            <div className="table-header-cell">Role</div>
            <div className="table-header-cell">Status</div>
            <div className="table-header-cell">Actions</div>
            <div className="table-header-cell">Created</div>
          </div>

          <div className="admin-table-body">
            {users.map((user) => (
              <div key={user.id} className="admin-table-row">
                <div className="table-cell">{user.id}</div>
                <div className="table-cell">{user.email}</div>
                <div className="table-cell">
                  {(user.first_name || '')} {(user.last_name || '')}
                </div>
                <div className="table-cell">
                  <select
                    value={user.system_role}
                    onChange={(e) => handleRoleUpdate(user.id, e.target.value)}
                    className="user-role-select"
                    data-testid={`user-role-${user.id}`}
                  >
                    <option value="admin">Administrator</option>
                    <option value="user">Standard User</option>
                  </select>
                </div>
                <div className="table-cell">
                  <select
                    value={user.is_active ? 'active' : 'inactive'}
                    onChange={(e) => handleStatusUpdate(user.id, e.target.value === 'active')}
                    className="user-status-select"
                    data-testid={`user-status-${user.id}`}
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>
                <div className="table-cell">
                  <div className="admin-action-buttons">
                    <button
                      onClick={() => navigate(`/admin/users/${user.id}`)}
                      className="btn-icon btn-view"
                      title="View Details"
                      data-testid={`view-user-${user.id}`}
                    >
                      👁️
                    </button>
                  </div>
                </div>
                <div className="table-cell">
                  {new Date(user.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="admin-pagination">
        <p className="pagination-info">
          Showing {startIndex}-{endIndex} of {total} users
        </p>
        <div className="pagination-controls">
          <button
            onClick={() => page > 1 && handlePageChange(page - 1)}
            disabled={page === 1}
            className="btn-pagination"
            data-testid="prev-page"
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
            data-testid="next-page"
          >
            Next ›
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminUsersPage;