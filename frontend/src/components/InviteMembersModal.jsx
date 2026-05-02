/**
 * Invite Members Modal
 * Modal for inviting new members to a team
 */

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const InviteMembersModal = ({ onClose, teamId }) => {
  const { authAxios } = useAuth();
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email.trim()) {
      setError('Email is required');
      return;
    }
    
    // Basic email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    setLoading(true);
    
    try {
      const res = await authAxios().post(`/teams/${teamId}/invites`, {
        email: email.trim(),
        role,
      });
      
      toast.success(`Invitation sent to ${email}`);
      onClose(true); // Close with refresh flag
    } catch (e) {
      const message = e.response?.data?.detail || 'Failed to send invitation';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} data-testid="invite-modal">
      <div className="modal-content modal-small">
        <div className="modal-header">
          <h2>Invite Team Member</h2>
          <button className="modal-close" onClick={() => onClose(false)}>&times;</button>
        </div>
        
        <div className="modal-body">
          <form onSubmit={handleSubmit} className="invite-form">
            {error && (
              <div className="auth-error" data-testid="invite-error">
                {error}
              </div>
            )}
            
            <div className="form-group">
              <label htmlFor="invite-email">Email Address</label>
              <input
                id="invite-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="colleague@example.com"
                autoFocus
                data-testid="invite-email-input"
              />
              <span className="field-hint">
                They'll receive an email with a link to join the team
              </span>
            </div>

            <div className="form-group">
              <label htmlFor="invite-role">Role</label>
              <select
                id="invite-role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                data-testid="invite-role-select"
              >
                <option value="member">Member</option>
                <option value="admin">Admin</option>
              </select>
              <span className="field-hint">
                {role === 'admin' 
                  ? 'Admins can manage members and settings' 
                  : 'Members can access all features but cannot manage team'}
              </span>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => onClose(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !email.trim()}
                data-testid="send-invite-btn"
              >
                {loading ? 'Sending...' : 'Send Invitation'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default InviteMembersModal;
