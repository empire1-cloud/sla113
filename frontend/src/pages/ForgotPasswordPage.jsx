/**
 * Forgot Password Page
 * Request password reset email
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await axios.post(`${API}/auth/password-reset/request`, { email });
      setSubmitted(true);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to send reset email';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="auth-page" data-testid="forgot-password-success">
        <div className="auth-container">
          <div className="auth-header">
            <div className="success-icon">📧</div>
            <h1>Check Your Email</h1>
            <p>If an account exists with that email, you'll receive password reset instructions.</p>
          </div>
          
          <div className="reset-info">
            <p>The link will expire in <strong>15 minutes</strong>.</p>
            <p>Didn't receive the email? Check your spam folder or try again.</p>
          </div>
          
          <div className="auth-actions">
            <button
              onClick={() => {
                setSubmitted(false);
                setEmail('');
              }}
              className="btn-secondary"
            >
              Try Again
            </button>
            <Link to="/login" className="btn-primary">
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page" data-testid="forgot-password-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Forgot Password?</h1>
          <p>Enter your email and we'll send you a reset link</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form" data-testid="forgot-form">
          {error && (
            <div className="auth-error" data-testid="forgot-error">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoFocus
              data-testid="forgot-email"
            />
          </div>

          <button
            type="submit"
            className="auth-btn primary"
            disabled={loading || !email}
            data-testid="forgot-submit"
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Remember your password?{' '}
            <Link to="/login" data-testid="login-link">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
