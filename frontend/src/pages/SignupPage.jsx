/**
 * Signup Page
 * New user registration with validation
 * Supports invite token flow for team invitations
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SignupPage = () => {
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('invite');
  const inviteEmail = searchParams.get('email');
  
  const [formData, setFormData] = useState({
    email: inviteEmail || '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [inviteInfo, setInviteInfo] = useState(null);
  
  const { signup, authAxios, refreshTeams } = useAuth();
  const navigate = useNavigate();
  
  // Fetch invite info if token present
  useEffect(() => {
    const fetchInviteInfo = async () => {
      if (!inviteToken) return;
      
      try {
        const res = await axios.get(`${API}/invites/validate/${inviteToken}`);
        if (res.data.valid) {
          setInviteInfo(res.data);
          // Pre-fill email if from invite
          if (res.data.email) {
            setFormData(prev => ({ ...prev, email: res.data.email }));
          }
        }
      } catch (e) {
        console.error('Failed to validate invite:', e);
      }
    };
    
    fetchInviteInfo();
  }, [inviteToken]);
  
  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/\d/.test(password)) errors.push('One number');
    return errors;
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear field errors on change
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: null }));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});
    
    // Validate
    const errors = {};
    
    if (!formData.firstName.trim()) {
      errors.firstName = 'First name is required';
    }
    
    if (!formData.lastName.trim()) {
      errors.lastName = 'Last name is required';
    }
    
    const passwordErrors = validatePassword(formData.password);
    if (passwordErrors.length > 0) {
      errors.password = passwordErrors.join(', ');
    }
    
    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }
    
    setLoading(true);
    
    const result = await signup(
      formData.email,
      formData.password,
      formData.firstName.trim(),
      formData.lastName.trim()
    );
    
    if (result.success) {
      // If there's an invite token, accept it automatically
      if (inviteToken) {
        try {
          await authAxios().post('/teams/invites/accept', { token: inviteToken });
          await refreshTeams();
        } catch (e) {
          console.error('Failed to auto-accept invite:', e);
          // Still redirect even if invite acceptance fails
        }
      }
      
      navigate('/', { replace: true });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };
  
  return (
    <div className="auth-page" data-testid="signup-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Create Account</h1>
          {inviteInfo ? (
            <p>Join <strong>{inviteInfo.team_name}</strong> as {inviteInfo.role}</p>
          ) : (
            <p>Get started with Hybrid Intelligence</p>
          )}
        </div>
        
        {inviteInfo && (
          <div className="invite-banner" data-testid="invite-banner">
            <span className="invite-banner-icon">🎉</span>
            <span>You've been invited by {inviteInfo.invited_by_name}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="auth-form" data-testid="signup-form">
          {error && (
            <div className="auth-error" data-testid="signup-error">
              {error}
            </div>
          )}
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                value={formData.firstName}
                onChange={handleChange}
                placeholder="John"
                required
                data-testid="signup-firstname"
              />
              {fieldErrors.firstName && (
                <span className="field-error">{fieldErrors.firstName}</span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                value={formData.lastName}
                onChange={handleChange}
                placeholder="Doe"
                required
                data-testid="signup-lastname"
              />
              {fieldErrors.lastName && (
                <span className="field-error">{fieldErrors.lastName}</span>
              )}
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
              autoComplete="email"
              disabled={!!inviteInfo}
              className={inviteInfo ? 'input-disabled' : ''}
              data-testid="signup-email"
            />
            {inviteInfo && (
              <span className="field-hint">
                Email is set from the invitation
              </span>
            )}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              autoComplete="new-password"
              data-testid="signup-password"
            />
            {fieldErrors.password && (
              <span className="field-error">{fieldErrors.password}</span>
            )}
            <span className="field-hint">
              8+ characters, uppercase, lowercase, and number
            </span>
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="••••••••"
              required
              autoComplete="new-password"
              data-testid="signup-confirm"
            />
            {fieldErrors.confirmPassword && (
              <span className="field-error">{fieldErrors.confirmPassword}</span>
            )}
          </div>
          
          <button
            type="submit"
            className="auth-btn primary"
            disabled={loading}
            data-testid="signup-submit"
          >
            {loading ? 'Creating account...' : inviteInfo ? 'Create Account & Join Team' : 'Create Account'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link 
              to={inviteToken ? `/login?invite=${inviteToken}&email=${encodeURIComponent(formData.email)}` : '/login'} 
              data-testid="login-link"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupPage;
