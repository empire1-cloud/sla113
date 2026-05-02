/**
 * Pending Invites List
 * Shows all pending invites for a team with ability to revoke
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const PendingInvitesList = ({ teamId, refreshTrigger }) => {
  const { authAxios } = useAuth();
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchInvites = useCallback(async () => {
    if (!teamId) return;
    
    setLoading(true);
    try {
      const res = await authAxios().get(`/teams/${teamId}/invites`);
      setInvites(res.data);
    } catch (e) {
      console.error('Failed to fetch invites:', e);
      setInvites([]);
    } finally {
      setLoading(false);
    }
  }, [authAxios, teamId]);

  useEffect(() => {
    fetchInvites();
  }, [fetchInvites, refreshTrigger]);

  const handleRevoke = async (inviteId, email) => {
    if (!window.confirm(`Revoke invitation for ${email}?`)) {
      return;
    }
    
    try {
      await authAxios().delete(`/teams/${teamId}/invites/${inviteId}`);
      toast.success(`Invitation for ${email} revoked`);
      fetchInvites();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to revoke invitation');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getExpiryStatus = (expiresAt) => {
    if (!expiresAt) return { text: 'Unknown', class: '' };
    
    const now = new Date();
    const expiry = new Date(expiresAt);
    const daysLeft = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24));
    
    if (daysLeft <= 1) {
      return { text: 'Expires today', class: 'expiry-urgent' };
    } else if (daysLeft <= 3) {
      return { text: `Expires in ${daysLeft} days`, class: 'expiry-warning' };
    } else {
      return { text: `Expires in ${daysLeft} days`, class: 'expiry-normal' };
    }
  };

  const getRoleBadge = (role) => {
    const classes = {
      admin: 'badge-admin',
      member: 'badge-member',
    };
    return classes[role] || '';
  };

  if (loading) {
    return (
      <div className="invites-loading" data-testid="invites-loading">
        <div className="spinner"></div>
        <span>Loading invites...</span>
      </div>
    );
  }

  if (invites.length === 0) {
    return (
      <div className="no-invites" data-testid="no-invites">
        <p>No pending invitations</p>
      </div>
    );
  }

  return (
    <div className="invites-list" data-testid="pending-invites-list">
      {invites.map((invite) => {
        const expiry = getExpiryStatus(invite.expires_at);
        
        return (
          <div key={invite.id} className="invite-item" data-testid={`invite-${invite.id}`}>
            <div className="invite-info">
              <div className="invite-email">
                <span className="email-icon">📧</span>
                <span className="email-text">{invite.email}</span>
              </div>
              <div className="invite-meta">
                <span className={`role-badge ${getRoleBadge(invite.role)}`}>
                  {invite.role}
                </span>
                <span className="invite-by">
                  Invited by {invite.invited_by_name}
                </span>
                <span className="invite-date">
                  on {formatDate(invite.created_at)}
                </span>
              </div>
              <div className={`invite-expiry ${expiry.class}`}>
                ⏰ {expiry.text}
              </div>
            </div>
            <button
              className="btn-revoke"
              onClick={() => handleRevoke(invite.id, invite.email)}
              data-testid={`revoke-${invite.id}`}
            >
              Revoke
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default PendingInvitesList;
