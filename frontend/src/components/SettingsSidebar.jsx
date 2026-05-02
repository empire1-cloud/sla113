/**
 * Settings Sidebar Component
 * Consistent navigation sidebar for all settings pages
 */

import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const SettingsSidebar = () => {
  const { currentTeam, user } = useAuth();
  const location = useLocation();

  // Check if user is owner/admin of current team
  const isTeamAdmin = currentTeam && ['owner', 'admin'].includes(currentTeam.role);
  const isSystemAdmin = user?.system_role === 'admin';

  const navItems = [
    {
      label: 'Profile',
      path: '/profile',
      icon: '👤',
      description: 'Personal settings',
      visible: true,
    },
    {
      label: 'Team Settings',
      path: '/team/settings',
      icon: '👥',
      description: 'Members & invites',
      visible: true,
    },
    {
      label: 'Billing',
      path: '/billing',
      icon: '💳',
      description: 'Plans & usage',
      visible: isTeamAdmin,
    },
    {
      label: 'API Keys',
      path: '/settings/api-keys',
      icon: '🔑',
      description: 'Programmatic access',
      visible: isTeamAdmin,
    },
    {
      label: 'Admin Dashboard',
      path: '/admin/overview',
      icon: '🛡️',
      description: 'System administration',
      visible: isSystemAdmin,
      divider: true,
    },
  ];

  const isSettingsPage = [
    '/profile',
    '/team/settings',
    '/billing',
    '/settings/api-keys',
    '/admin/overview',
  ].includes(location.pathname);

  // Only show sidebar on settings pages
  if (!isSettingsPage) return null;

  return (
    <aside className="settings-sidebar" data-testid="settings-sidebar">
      <div className="sidebar-header">
        <h3>Settings</h3>
      </div>
      <nav className="sidebar-nav">
        {navItems
          .filter(item => item.visible)
          .map((item, index) => (
            <div key={item.path}>
              {item.divider && <div className="sidebar-divider" />}
              <NavLink
                to={item.path}
                className={({ isActive }) => 
                  `sidebar-item ${isActive ? 'active' : ''}`
                }
                data-testid={`sidebar-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <span className="sidebar-icon">{item.icon}</span>
                <div className="sidebar-text">
                  <span className="sidebar-label">{item.label}</span>
                  <span className="sidebar-desc">{item.description}</span>
                </div>
              </NavLink>
            </div>
          ))}
      </nav>

      <style>{`
        .settings-sidebar {
          width: 260px;
          background: var(--bg-card);
          border-right: 1px solid var(--border-color);
          min-height: calc(100vh - 60px);
          position: sticky;
          top: 60px;
          flex-shrink: 0;
        }

        .sidebar-header {
          padding: 1.25rem 1.25rem 0.75rem;
          border-bottom: 1px solid var(--border-color);
        }

        .sidebar-header h3 {
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-secondary);
          margin: 0;
        }

        .sidebar-nav {
          padding: 0.75rem;
        }

        .sidebar-divider {
          height: 1px;
          background: var(--border-color);
          margin: 0.5rem 0;
        }

        .sidebar-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          border-radius: 8px;
          text-decoration: none;
          color: var(--text-primary);
          transition: all 0.2s;
          margin-bottom: 0.25rem;
        }

        .sidebar-item:hover {
          background: var(--bg-secondary);
        }

        .sidebar-item.active {
          background: var(--bg-secondary);
          border-left: 3px solid var(--accent-green);
          padding-left: calc(0.75rem - 3px);
        }

        .sidebar-icon {
          font-size: 1.1rem;
          flex-shrink: 0;
        }

        .sidebar-text {
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .sidebar-label {
          font-size: 0.9rem;
          font-weight: 500;
        }

        .sidebar-desc {
          font-size: 0.75rem;
          color: var(--text-secondary);
        }

        @media (max-width: 1024px) {
          .settings-sidebar {
            display: none;
          }
        }
      `}</style>
    </aside>
  );
};

export default SettingsSidebar;
