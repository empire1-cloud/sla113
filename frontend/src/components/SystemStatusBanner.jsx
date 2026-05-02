/**
 * System Status Banner
 * Shows warnings when external services are not configured (admin only)
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SystemStatusBanner = () => {
  const { user, isAuthenticated } = useAuth();
  const [status, setStatus] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  // Only show for system admins
  const isSystemAdmin = user?.system_role === 'admin';

  const fetchStatus = useCallback(async () => {
    if (!isAuthenticated || !isSystemAdmin) return;

    try {
      const res = await axios.get(`${API_URL}/api/system/status`);
      setStatus(res.data);
    } catch (e) {
      console.error('Failed to fetch system status:', e);
    }
  }, [isAuthenticated, isSystemAdmin]);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Don't show if not admin, dismissed, or no status
  if (!isSystemAdmin || dismissed || !status) return null;

  // Check for warnings
  const warnings = [];
  
  if (!status.services?.email_enabled) {
    warnings.push({
      key: 'email',
      icon: '📧',
      message: 'Email service not configured',
      detail: 'Password reset and invite emails will not be sent',
    });
  }

  if (!status.services?.stripe_enabled) {
    warnings.push({
      key: 'stripe',
      icon: '💳',
      message: 'Stripe not configured',
      detail: 'Billing features are in mock mode',
    });
  }

  const oauthProviders = status.services?.oauth_enabled || {};
  if (!oauthProviders.google && !oauthProviders.github) {
    warnings.push({
      key: 'oauth',
      icon: '🔐',
      message: 'OAuth providers not configured',
      detail: 'Social login options are disabled',
    });
  }

  // No warnings, don't show banner
  if (warnings.length === 0) return null;

  return (
    <div 
      className="system-status-banner"
      data-testid="system-status-banner"
    >
      <div className="banner-content">
        <div className="banner-header">
          <span className="banner-icon">⚠️</span>
          <span className="banner-title">
            Development Mode — {warnings.length} service{warnings.length > 1 ? 's' : ''} not configured
          </span>
        </div>
        <div className="banner-warnings">
          {warnings.map((warning) => (
            <div key={warning.key} className="warning-item" data-testid={`warning-${warning.key}`}>
              <span className="warning-icon">{warning.icon}</span>
              <div className="warning-text">
                <span className="warning-message">{warning.message}</span>
                <span className="warning-detail">{warning.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <button 
        className="banner-dismiss"
        onClick={() => setDismissed(true)}
        aria-label="Dismiss"
        data-testid="dismiss-banner"
      >
        ×
      </button>

      <style>{`
        .system-status-banner {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
          padding: 0.75rem 1.5rem;
          background: rgba(255, 159, 67, 0.1);
          border-bottom: 1px solid rgba(255, 159, 67, 0.3);
        }

        .banner-content {
          flex: 1;
        }

        .banner-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .banner-icon {
          font-size: 1rem;
        }

        .banner-title {
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--accent-orange);
        }

        .banner-warnings {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .warning-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.35rem 0.75rem;
          background: var(--bg-secondary);
          border-radius: 6px;
          font-size: 0.8rem;
        }

        .warning-icon {
          font-size: 0.9rem;
        }

        .warning-text {
          display: flex;
          flex-direction: column;
        }

        .warning-message {
          color: var(--text-primary);
          font-weight: 500;
        }

        .warning-detail {
          color: var(--text-secondary);
          font-size: 0.75rem;
        }

        .banner-dismiss {
          background: none;
          border: none;
          color: var(--text-secondary);
          font-size: 1.25rem;
          cursor: pointer;
          padding: 0.25rem;
          line-height: 1;
          transition: color 0.2s;
        }

        .banner-dismiss:hover {
          color: var(--text-primary);
        }

        @media (max-width: 768px) {
          .system-status-banner {
            padding: 0.75rem 1rem;
          }

          .banner-warnings {
            flex-direction: column;
            gap: 0.5rem;
          }

          .warning-item {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default SystemStatusBanner;
