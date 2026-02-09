/**
 * Login Page
 * Email/password authentication with error handling
 * Supports invite token flow for team invitations
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const LoginPage = () => {
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('invite');
  const inviteEmail = searchParams.get('email');
  
  const [email, setEmail] = useState(inviteEmail || '');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [inviteInfo, setInviteInfo] = useState(null);
  
  const { login, authAxios, refreshTeams } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/';
  
  // Fetch invite info if token present
  useEffect(() => {
    const fetchInviteInfo = async () => {
      if (!inviteToken) return;
      
      try {
        const res = await axios.get(`${API}/invites/validate/${inviteToken}`);
        if (res.data.valid) {
          setInviteInfo(res.data);
          if (res.data.email) {
            setEmail(res.data.email);
          }
        }
      } catch (e) {
        console.error('Failed to validate invite:', e);
      }
    };
    
    fetchInviteInfo();
  }, [inviteToken]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const result = await login(email, password);
    
    if (result.success) {
      // If there's an invite token, accept it automatically
      if (inviteToken) {
        try {
          await authAxios().post('/teams/invites/accept', { token: inviteToken });
          await refreshTeams();
        } catch (e) {
          console.error('Failed to auto-accept invite:', e);
          // Check if it's an email mismatch error
          if (e.response?.data?.detail?.includes('different email')) {
            setError('This invite was sent to a different email address');
            setLoading(false);
            return;
          }
        }
      }
      
      navigate(from === '/login' ? '/' : from, { replace: true });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };
  
  return (
    <div className="auth-page" data-testid="login-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          {inviteInfo ? (
            <p>Sign in to join <strong>{inviteInfo.team_name}</strong></p>
          ) : (
            <p>Sign in to your account</p>
          )}
        </div>
        
        {inviteInfo && (
          <div className="invite-banner" data-testid="invite-banner">
            <span className="invite-banner-icon">🎉</span>
            <span>Invitation from {inviteInfo.invited_by_name}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="auth-form" data-testid="login-form">
          {error && (
            <div className="auth-error" data-testid="login-error">
              {error}
            </div>
          )}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
              data-testid="login-email"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
              data-testid="login-password"
            />
          </div>
          
          <button
            type="submit"
            className="auth-btn primary"
            disabled={loading}
            data-testid="login-submit"
          >
            {loading ? 'Signing in...' : inviteInfo ? 'Sign In & Join Team' : 'Sign In'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link 
              to={inviteToken ? `/signup?invite=${inviteToken}&email=${encodeURIComponent(email)}` : '/signup'} 
              data-testid="signup-link"
            >
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
