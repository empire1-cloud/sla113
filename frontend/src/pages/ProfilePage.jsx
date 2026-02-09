/**
 * Profile Page
 * User profile management with password change and session management
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import { PageLoading, LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { getErrorMessage, FormError } from '../components/ui/ErrorMessage';

const ProfilePage = () => {
  const { user, authAxios, teams, logout } = useAuth();
  
  // Profile state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);
  
  // Password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  
  // Sessions state
  const [sessions, setSessions] = useState([]);
  const [sessionsLoading, setSessionsLoading] = useState(true);

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setFirstName(user.first_name || '');
      setLastName(user.last_name || '');
    }
  }, [user]);

  // Fetch sessions
  const fetchSessions = useCallback(async () => {
    setSessionsLoading(true);
    try {
      const res = await authAxios().get('/auth/sessions');
      setSessions(res.data);
    } catch (e) {
      console.error('Failed to fetch sessions:', e);
      setSessions([]);
    } finally {
      setSessionsLoading(false);
    }
  }, [authAxios]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Update profile
  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setProfileLoading(true);
    
    try {
      await authAxios().put('/profile/me', {
        first_name: firstName,
        last_name: lastName
      });
      toast.success('Profile updated successfully');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  // Change password
  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');
    
    // Validate
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }
    
    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters');
      return;
    }
    
    if (!/[A-Z]/.test(newPassword)) {
      setPasswordError('Password must contain at least one uppercase letter');
      return;
    }
    
    if (!/[a-z]/.test(newPassword)) {
      setPasswordError('Password must contain at least one lowercase letter');
      return;
    }
    
    if (!/[0-9]/.test(newPassword)) {
      setPasswordError('Password must contain at least one number');
      return;
    }
    
    setPasswordLoading(true);
    
    try {
      await authAxios().put('/auth/password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (e) {
      setPasswordError(e.response?.data?.detail || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  // Revoke specific session
  const handleRevokeSession = async (sessionId) => {
    try {
      await authAxios().delete(`/auth/sessions/${sessionId}`);
      toast.success('Session revoked');
      fetchSessions();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to revoke session');
    }
  };

  // Logout all sessions
  const handleLogoutAll = async () => {
    if (!window.confirm('This will sign you out from all devices. Continue?')) {
      return;
    }
    
    try {
      await authAxios().post('/auth/logout', null, {
        params: { logout_all: true }
      });
      toast.success('All sessions revoked');
      logout();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to logout all sessions');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const getRoleLabel = (role) => {
    const labels = {
      admin: { text: 'Admin', class: 'badge-admin' },
      owner: { text: 'Owner', class: 'badge-owner' },
      member: { text: 'Member', class: 'badge-member' },
      user: { text: 'User', class: 'badge-user' }
    };
    return labels[role] || { text: role, class: '' };
  };

  if (!user) {
    return (
      <div className="page-container" data-testid="profile-loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="page-container" data-testid="profile-page">
      <header className="page-header">
        <h1>Profile Settings</h1>
        <p className="subtitle">Manage your account and security settings</p>
      </header>

      <div className="profile-grid">
        {/* Profile Info Card */}
        <section className="profile-card" data-testid="profile-info-card">
          <div className="card-header">
            <h2>Profile Information</h2>
          </div>
          <form onSubmit={handleUpdateProfile} className="profile-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={user.email}
                disabled
                className="input-disabled"
              />
              <span className="field-hint">Email cannot be changed</span>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">First Name</label>
                <input
                  id="firstName"
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="John"
                  data-testid="profile-first-name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="lastName">Last Name</label>
                <input
                  id="lastName"
                  type="text"
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="Doe"
                  data-testid="profile-last-name"
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={profileLoading}
              data-testid="profile-save-btn"
            >
              {profileLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </section>

        {/* System Role & Teams Card */}
        <section className="profile-card" data-testid="profile-roles-card">
          <div className="card-header">
            <h2>Roles & Memberships</h2>
          </div>
          
          <div className="roles-section">
            <div className="role-item">
              <span className="role-label">System Role</span>
              <span className={`role-badge ${getRoleLabel(user.system_role || 'user').class}`}>
                {getRoleLabel(user.system_role || 'user').text}
              </span>
            </div>
          </div>

          <div className="teams-list">
            <h3>Team Memberships</h3>
            {teams.length === 0 ? (
              <p className="no-teams">No team memberships</p>
            ) : (
              teams.map((team) => (
                <div key={team.id} className="team-membership-item" data-testid={`team-membership-${team.id}`}>
                  <div className="team-info">
                    <span className="team-icon">{team.type === 'personal' ? '👤' : '🏢'}</span>
                    <span className="team-name">{team.name}</span>
                  </div>
                  <span className={`role-badge ${getRoleLabel(team.role).class}`}>
                    {getRoleLabel(team.role).text}
                  </span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Change Password Card */}
        <section className="profile-card" data-testid="password-card">
          <div className="card-header">
            <h2>Change Password</h2>
          </div>
          <form onSubmit={handleChangePassword} className="profile-form">
            {passwordError && (
              <div className="auth-error" data-testid="password-error">
                {passwordError}
              </div>
            )}
            
            <div className="form-group">
              <label htmlFor="currentPassword">Current Password</label>
              <input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                required
                data-testid="current-password-input"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="newPassword">New Password</label>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                required
                data-testid="new-password-input"
              />
              <span className="field-hint">
                8+ characters, uppercase, lowercase, and number
              </span>
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm New Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
                data-testid="confirm-password-input"
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              disabled={passwordLoading || !currentPassword || !newPassword || !confirmPassword}
              data-testid="change-password-btn"
            >
              {passwordLoading ? 'Changing...' : 'Change Password'}
            </button>
          </form>
        </section>

        {/* Active Sessions Card */}
        <section className="profile-card sessions-card" data-testid="sessions-card">
          <div className="card-header">
            <h2>Active Sessions</h2>
            <button
              className="btn-danger-outline"
              onClick={handleLogoutAll}
              data-testid="logout-all-btn"
            >
              Logout All
            </button>
          </div>
          
          {sessionsLoading ? (
            <div className="sessions-loading">
              <div className="spinner"></div>
            </div>
          ) : sessions.length === 0 ? (
            <p className="no-sessions">No active sessions found</p>
          ) : (
            <div className="sessions-list">
              {sessions.map((session) => (
                <div key={session.id} className="session-item" data-testid={`session-${session.id}`}>
                  <div className="session-info">
                    <div className="session-device">
                      <span className="device-icon">💻</span>
                      <span className="device-info">
                        {session.device_info || 'Unknown Device'}
                      </span>
                    </div>
                    <div className="session-meta">
                      <span className="session-ip">
                        IP: {session.ip_address || 'Unknown'}
                      </span>
                      <span className="session-time">
                        Last active: {formatDate(session.last_used_at)}
                      </span>
                    </div>
                  </div>
                  <button
                    className="btn-revoke"
                    onClick={() => handleRevokeSession(session.id)}
                    data-testid={`revoke-session-${session.id}`}
                  >
                    Revoke
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default ProfilePage;
