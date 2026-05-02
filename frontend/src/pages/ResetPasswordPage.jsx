/**
 * Reset Password Page
 * Set new password using reset token
 */

import { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [validating, setValidating] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Validate token on mount
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setValidating(false);
        return;
      }

      try {
        const res = await axios.get(`${API}/auth/password-reset/validate/${token}`);
        setTokenValid(res.data.valid);
      } catch (err) {
        setTokenValid(false);
      } finally {
        setValidating(false);
      }
    };

    validateToken();
  }, [token]);

  const validatePassword = () => {
    if (password.length < 8) return 'Password must be at least 8 characters';
    if (!/[A-Z]/.test(password)) return 'Password must contain an uppercase letter';
    if (!/[a-z]/.test(password)) return 'Password must contain a lowercase letter';
    if (!/\d/.test(password)) return 'Password must contain a number';
    if (password !== confirmPassword) return 'Passwords do not match';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const validationError = validatePassword();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API}/auth/password-reset/confirm`, {
        token,
        new_password: password,
      });
      setSuccess(true);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to reset password';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  // Loading state
  if (validating) {
    return (
      <div className="auth-page" data-testid="reset-loading">
        <div className="auth-container">
          <div className="auth-loading">
            <div className="spinner"></div>
            <p>Validating reset link...</p>
          </div>
        </div>
      </div>
    );
  }

  // Invalid/expired token
  if (!token || !tokenValid) {
    return (
      <div className="auth-page" data-testid="reset-invalid">
        <div className="auth-container">
          <div className="auth-header">
            <div className="error-icon">❌</div>
            <h1>Invalid Reset Link</h1>
            <p>This password reset link is invalid or has expired.</p>
          </div>

          <div className="reset-info">
            <p>Reset links expire after 15 minutes for security.</p>
          </div>

          <div className="auth-actions">
            <Link to="/forgot-password" className="btn-primary">
              Request New Link
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="auth-page" data-testid="reset-success">
        <div className="auth-container">
          <div className="auth-header">
            <div className="success-icon">✅</div>
            <h1>Password Reset!</h1>
            <p>Your password has been successfully reset.</p>
          </div>

          <div className="reset-info">
            <p>You can now sign in with your new password.</p>
            <p>All other sessions have been logged out for security.</p>
          </div>

          <div className="auth-actions">
            <Link to="/login" className="btn-primary" data-testid="login-btn">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page" data-testid="reset-password-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Reset Password</h1>
          <p>Enter your new password below</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" data-testid="reset-form">
          {error && (
            <div className="auth-error" data-testid="reset-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoFocus
              data-testid="reset-password"
            />
            <span className="field-hint">
              8+ characters, uppercase, lowercase, and number
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
              data-testid="reset-confirm"
            />
          </div>

          <button
            type="submit"
            className="auth-btn primary"
            disabled={loading || !password || !confirmPassword}
            data-testid="reset-submit"
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            <Link to="/login" data-testid="back-link">Back to login</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;
