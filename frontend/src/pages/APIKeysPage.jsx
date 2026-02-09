/**
 * API Keys Page
 * Manage API keys for programmatic access
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminOnly } from '../components/RoleGate';
import { toast } from 'sonner';
import { PageLoading } from '../components/ui/LoadingState';
import { NoAPIKeysFound } from '../components/ui/EmptyState';
import { getErrorMessage } from '../components/ui/ErrorMessage';

const APIKeysPage = () => {
  const { authAxios, currentTeam } = useAuth();
  
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [creating, setCreating] = useState(false);
  const [createdKey, setCreatedKey] = useState(null);
  const [copied, setCopied] = useState(false);

  const fetchKeys = useCallback(async () => {
    if (!currentTeam) return;
    
    setLoading(true);
    try {
      const res = await authAxios().get(`/teams/${currentTeam.id}/api-keys`);
      setKeys(res.data);
    } catch (e) {
      console.error('Failed to fetch API keys:', e);
      toast.error(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  }, [authAxios, currentTeam]);

  useEffect(() => {
    fetchKeys();
  }, [fetchKeys]);

  const handleCreate = async () => {
    if (!newKeyName.trim()) {
      toast.error('Please enter a name for the API key');
      return;
    }
    
    setCreating(true);
    try {
      const res = await authAxios().post(`/teams/${currentTeam.id}/api-keys`, {
        name: newKeyName.trim(),
      });
      
      setCreatedKey(res.data);
      setNewKeyName('');
      toast.success('API key created successfully');
      fetchKeys();
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setCreating(false);
    }
  };

  const handleRevoke = async (keyId, keyName) => {
    if (!window.confirm(`Are you sure you want to revoke "${keyName}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      await authAxios().delete(`/teams/${currentTeam.id}/api-keys/${keyId}`);
      toast.success('API key revoked');
      fetchKeys();
    } catch (e) {
      toast.error(getErrorMessage(e));
    }
  };

  const handleCopy = async () => {
    if (!createdKey?.key) return;
    
    try {
      await navigator.clipboard.writeText(createdKey.key);
      setCopied(true);
      toast.success('API key copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      toast.error('Failed to copy to clipboard');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const closeCreatedModal = () => {
    setCreatedKey(null);
    setShowCreateModal(false);
  };

  if (loading) {
    return <PageLoading message="Loading API keys..." />;
  }

  return (
    <div className="page-container" data-testid="api-keys-page">
      <header className="page-header">
        <h1>API Keys</h1>
        <p className="subtitle">Manage programmatic access to {currentTeam?.name}</p>
      </header>

      <div className="api-keys-content">
        <section className="api-keys-card settings-card" data-testid="api-keys-section">
          <div className="card-header">
            <div>
              <h2>Your API Keys</h2>
              <span className="key-count">{keys.length} key(s)</span>
            </div>
            <AdminOnly>
              <button
                className="btn-primary"
                onClick={() => setShowCreateModal(true)}
                data-testid="create-key-btn"
              >
                + Create API Key
              </button>
            </AdminOnly>
          </div>

          <div className="card-body" style={{ padding: '1.25rem' }}>
            <div className="api-keys-info">
              <p>
                Use API keys to authenticate requests to the Hybrid Intelligence API.
                Keys have full access to your team's resources.
              </p>
            </div>

            {keys.length === 0 ? (
              <AdminOnly fallback={
                <NoAPIKeysFound />
              }>
                <NoAPIKeysFound onCreateKey={() => setShowCreateModal(true)} />
              </AdminOnly>
            ) : (
              <div className="keys-list">
                {keys.map((key) => (
                  <div key={key.id} className="key-item" data-testid={`key-${key.id}`}>
                    <div className="key-info">
                      <div className="key-name">{key.name}</div>
                      <div className="key-prefix">
                        <code>{key.key_prefix}••••••••••••</code>
                      </div>
                    </div>
                    <div className="key-meta">
                      <span className="key-created">
                        Created: {formatDate(key.created_at)}
                      </span>
                      <span className="key-used">
                        Last used: {formatDate(key.last_used_at)}
                      </span>
                    </div>
                    <AdminOnly>
                      <button
                        className="btn-revoke"
                        onClick={() => handleRevoke(key.id, key.name)}
                        data-testid={`revoke-${key.id}`}
                      >
                        Revoke
                      </button>
                    </AdminOnly>
                  </div>
                ))}
              </div>
            )}

            <div className="api-keys-docs">
              <h3>Usage</h3>
              <p>Include your API key in requests using the Authorization header:</p>
              <code className="code-block">
                Authorization: Bearer hic_your_api_key_here
              </code>
            </div>
          </div>
        </section>
      </div>

      {/* Create Key Modal */}
      {showCreateModal && !createdKey && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowCreateModal(false)}>
          <div className="modal-content modal-small" data-testid="create-key-modal">
            <div className="modal-header">
              <h2>Create API Key</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="key-name">Key Name</label>
                <input
                  id="key-name"
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production Server"
                  autoFocus
                  disabled={creating}
                  data-testid="key-name-input"
                />
                <span className="field-hint">
                  Choose a descriptive name to identify this key
                </span>
              </div>
              <div className="modal-actions">
                <button
                  className="btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  className="btn-primary"
                  onClick={handleCreate}
                  disabled={creating || !newKeyName.trim()}
                  data-testid="create-key-submit"
                >
                  {creating ? 'Creating...' : 'Create Key'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Created Modal */}
      {createdKey && (
        <div className="modal-overlay" data-testid="key-created-modal">
          <div className="modal-content modal-small">
            <div className="modal-header">
              <h2>API Key Created</h2>
            </div>
            <div className="modal-body">
              <div className="key-created-warning">
                <span className="warning-icon">⚠️</span>
                <p>
                  <strong>Important:</strong> This is the only time you'll see this key.
                  Copy it now and store it securely.
                </p>
              </div>
              
              <div className="created-key-display">
                <label>Your API Key</label>
                <div className="key-value-container">
                  <code className="key-value" data-testid="created-key-value">
                    {createdKey.key}
                  </code>
                  <button
                    className="copy-btn"
                    onClick={handleCopy}
                    data-testid="copy-key-btn"
                  >
                    {copied ? '✓ Copied' : 'Copy'}
                  </button>
                </div>
              </div>
              
              <div className="modal-actions">
                <button
                  className="btn-primary"
                  onClick={closeCreatedModal}
                  data-testid="done-btn"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APIKeysPage;
