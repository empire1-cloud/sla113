/**
 * App Header Component
 * Global navigation header with team switcher and user menu
 */

import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import TeamSwitcher from './TeamSwitcher';

const AppHeader = () => {
  const { user, logout, isAuthenticated, currentTeam } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getUserInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.email) {
      return user.email[0].toUpperCase();
    }
    return '?';
  };

  // Check if user is owner/admin of current team
  const isTeamAdmin = currentTeam && ['owner', 'admin'].includes(currentTeam.role);
  const isSystemAdmin = user?.system_role === 'admin';

  if (!isAuthenticated) {
    return (
      <header className="app-header" data-testid="app-header">
        <Link to="/" className="app-logo">
          <span className="logo-icon">🧠</span>
          <span className="logo-text">Hybrid Intelligence</span>
        </Link>
        <nav className="header-nav">
          <Link to="/login" className="nav-link" data-testid="login-nav">Sign In</Link>
          <Link to="/signup" className="nav-link primary" data-testid="signup-nav">Get Started</Link>
        </nav>
      </header>
    );
  }

  return (
    <header className="app-header" data-testid="app-header">
      <Link to="/" className="app-logo">
        <span className="logo-icon">🧠</span>
        <span className="logo-text">Hybrid Intelligence</span>
      </Link>

      <nav className="header-nav-main">
        <Link to="/engines" className="nav-link" data-testid="engines-nav">Engines</Link>
        <Link to="/pipeline-composer" className="nav-link" data-testid="composer-nav">Composer</Link>
        <Link to="/sla113" className="nav-link sla113-nav" data-testid="sla113-nav">SLA113</Link>
        <Link to="/analytics" className="nav-link" data-testid="analytics-nav">Analytics</Link>
        <Link to="/history" className="nav-link" data-testid="history-nav">History</Link>
      </nav>

      <div className="header-right">
        <TeamSwitcher />
        
        <div className="user-menu-container" ref={menuRef}>
          <button
            className="user-avatar-btn"
            onClick={() => setShowUserMenu(!showUserMenu)}
            data-testid="user-menu-toggle"
          >
            <span className="user-avatar">{getUserInitials()}</span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown" data-testid="user-dropdown">
              <div className="user-info">
                <span className="user-name">
                  {user?.first_name} {user?.last_name}
                </span>
                <span className="user-email">{user?.email}</span>
              </div>
              
              <div className="dropdown-divider"></div>
              
              <Link
                to="/profile"
                className="dropdown-item"
                onClick={() => setShowUserMenu(false)}
                data-testid="profile-link"
              >
                <span>👤</span>
                <span>Profile Settings</span>
              </Link>
              
              {isTeamAdmin && (
                <>
                  <Link
                    to="/billing"
                    className="dropdown-item"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="billing-link"
                  >
                    <span>💳</span>
                    <span>Billing</span>
                  </Link>
                  
                  <Link
                    to="/settings/api-keys"
                    className="dropdown-item"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="api-keys-link"
                  >
                    <span>🔑</span>
                    <span>API Keys</span>
                  </Link>
                </>
              )}
              
              {isSystemAdmin && (
                <>
                  <div className="dropdown-divider"></div>
                  <Link
                    to="/admin/overview"
                    className="dropdown-item admin-link"
                    onClick={() => setShowUserMenu(false)}
                    data-testid="admin-link"
                  >
                    <span>🛡️</span>
                    <span>Admin Dashboard</span>
                  </Link>
                </>
              )}
              
              <div className="dropdown-divider"></div>
              
              <button
                className="dropdown-item logout"
                onClick={handleLogout}
                data-testid="logout-btn"
              >
                <span>🚪</span>
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
