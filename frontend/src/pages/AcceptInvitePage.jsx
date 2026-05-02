/**
 * Accept Invite Page
 * Handles the invite acceptance flow
 */

import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const AcceptInvitePage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated, user, authAxios, refreshTeams } = useAuth();
  
  const token = searchParams.get('token');
  
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [inviteData, setInviteData] = useState(null);
  const [error, setError] = useState('');
  const [emailMismatch, setEmailMismatch] = useState(false);

  // Validate invite token on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setError('No invite token provided');
        setLoading(false);
        return;
      }
      
      try {
        const res = await axios.get(`${API}/invites/validate/${token}`);
        
        if (!res.data.valid) {
          setError(res.data.error || 'Invalid invite');
        } else {
          setInviteData(res.data);
          
          // Check email mismatch if user is logged in
          if (isAuthenticated && user) {
            if (user.email.toLowerCase() !== res.data.email.toLowerCase()) {
              setEmailMismatch(true);
            }
          }
        }
      } catch (e) {
        setError('Failed to validate invite');
      } finally {
        setLoading(false);
      }
    };
    
    validateToken();
  }, [token, isAuthenticated, user]);

  // Accept the invite
  const handleAccept = async () => {
    if (!token) return;
    
    setAccepting(true);
    
    try {
      await authAxios().post('/teams/invites/accept', { token });
      
      toast.success(`Successfully joined ${inviteData.team_name}!`);
      
      // Refresh teams list
      await refreshTeams();
      
      // Navigate to home
      navigate('/');
    } catch (e) {
      const message = e.response?.data?.detail || 'Failed to accept invite';
      toast.error(message);
      setError(message);
    } finally {
      setAccepting(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="invite-page" data-testid="invite-page-loading">
        <div className="invite-container">
          <div className="invite-loading">
            <div className="spinner"></div>
            <p>Validating invite...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !inviteData) {
    return (
      <div className="invite-page" data-testid="invite-page-error">
        <div className="invite-container">
          <div className="invite-error-card">
            <div className="error-icon">❌</div>
            <h2>Invite Not Valid</h2>
            <p className="error-message">{error}</p>
            <Link to="/" className="btn-primary">
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Email mismatch - user logged in with different email
  if (emailMismatch && isAuthenticated) {
    return (
      <div className="invite-page" data-testid="invite-page-mismatch">
        <div className="invite-container">
          <div className="invite-card">
            <div className="invite-icon">⚠️</div>
            <h2>Email Mismatch</h2>
            <p className="invite-mismatch-text">
              This invite was sent to <strong>{inviteData.email}</strong>, 
              but you're logged in as <strong>{user.email}</strong>.
            </p>
            <div className="invite-actions">
              <Link to="/login" className="btn-secondary">
                Sign in with {inviteData.email}
              </Link>
              <Link to="/" className="btn-primary">
                Go to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Not authenticated - show login/signup options
  if (!isAuthenticated) {
    return (
      <div className="invite-page" data-testid="invite-page-auth">
        <div className="invite-container">
          <div className="invite-card">
            <div className="invite-header">
              <span className="invite-icon">🎉</span>
              <h2>You've Been Invited!</h2>
            </div>
            
            <div className="invite-details">
              <div className="invite-team">
                <span className="team-icon">🏢</span>
                <span className="team-name">{inviteData.team_name}</span>
              </div>
              
              <p className="invite-text">
                <strong>{inviteData.invited_by_name}</strong> invited you to join as a
                <span className={`role-badge badge-${inviteData.role}`}> {inviteData.role}</span>
              </p>
              
              <p className="invite-email-note">
                This invite was sent to <strong>{inviteData.email}</strong>
              </p>
            </div>
            
            <div className="invite-auth-options">
              <p className="auth-prompt">
                Sign in or create an account to accept this invitation
              </p>
              
              <div className="invite-actions">
                <Link 
                  to={`/login?invite=${token}&email=${encodeURIComponent(inviteData.email)}`} 
                  className="btn-secondary"
                  data-testid="invite-login-btn"
                >
                  Sign In
                </Link>
                <Link 
                  to={`/signup?invite=${token}&email=${encodeURIComponent(inviteData.email)}`} 
                  className="btn-primary"
                  data-testid="invite-signup-btn"
                >
                  Create Account
                </Link>
              </div>
            </div>
            
            <div className="invite-expiry-note">
              ⏰ This invite expires on {new Date(inviteData.expires_at).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Authenticated with correct email - show accept button
  return (
    <div className="invite-page" data-testid="invite-page-accept">
      <div className="invite-container">
        <div className="invite-card">
          <div className="invite-header">
            <span className="invite-icon">🎉</span>
            <h2>Accept Invitation</h2>
          </div>
          
          <div className="invite-details">
            <div className="invite-team">
              <span className="team-icon">🏢</span>
              <span className="team-name">{inviteData.team_name}</span>
            </div>
            
            <p className="invite-text">
              <strong>{inviteData.invited_by_name}</strong> invited you to join as a
              <span className={`role-badge badge-${inviteData.role}`}> {inviteData.role}</span>
            </p>
          </div>
          
          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}
          
          <div className="invite-actions">
            <Link to="/" className="btn-secondary">
              Decline
            </Link>
            <button
              onClick={handleAccept}
              className="btn-primary"
              disabled={accepting}
              data-testid="accept-invite-btn"
            >
              {accepting ? 'Joining...' : 'Accept & Join Team'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AcceptInvitePage;
