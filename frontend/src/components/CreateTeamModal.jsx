/**
 * Create Team Modal
 * Modal dialog for creating a new team
 */

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const CreateTeamModal = ({ onClose }) => {
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { createTeam, switchTeam } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name.trim()) {
      setError('Team name is required');
      return;
    }

    setLoading(true);
    setError('');

    const result = await createTeam(name.trim(), 'organization');
    
    setLoading(false);

    if (result.success) {
      // Switch to the new team
      switchTeam(result.team.id);
      onClose();
    } else {
      setError(result.error);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} data-testid="create-team-modal">
      <div className="modal-content modal-small">
        <div className="modal-header">
          <h2>Create New Team</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <form onSubmit={handleSubmit} className="create-team-form">
            {error && (
              <div className="auth-error" data-testid="create-team-error">
                {error}
              </div>
            )}
            
            <div className="form-group">
              <label htmlFor="team-name">Team Name</label>
              <input
                id="team-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Awesome Team"
                autoFocus
                data-testid="team-name-input"
              />
              <span className="field-hint">
                Choose a name that represents your team or project
              </span>
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !name.trim()}
                data-testid="create-team-submit"
              >
                {loading ? 'Creating...' : 'Create Team'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateTeamModal;
