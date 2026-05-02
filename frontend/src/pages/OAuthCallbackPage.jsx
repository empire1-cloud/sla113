/**
 * OAuth Callback Page
 * Handles OAuth provider redirects
 */

import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const OAuthCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { handleOAuthCallback } = useAuth();
  
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      const accessToken = searchParams.get('access_token');
      const refreshToken = searchParams.get('refresh_token');
      const errorParam = searchParams.get('error');
      const provider = searchParams.get('provider') || 'OAuth';

      if (errorParam) {
        setError(decodeURIComponent(errorParam));
        setProcessing(false);
        return;
      }

      if (!accessToken || !refreshToken) {
        setError('Authentication failed. Please try again.');
        setProcessing(false);
        return;
      }

      try {
        // Store tokens and get user data
        await handleOAuthCallback(accessToken, refreshToken);
        
        // Redirect to dashboard
        navigate('/', { replace: true });
      } catch (err) {
        setError(err.message || 'Failed to complete authentication');
        setProcessing(false);
      }
    };

    processCallback();
  }, [searchParams, navigate, handleOAuthCallback]);

  if (error) {
    return (
      <div className="oauth-callback-page" data-testid="oauth-error">
        <div className="oauth-container">
          <div className="oauth-error-card">
            <div className="error-icon">❌</div>
            <h2>Authentication Failed</h2>
            <p className="error-message">{error}</p>
            <div className="oauth-actions">
              <button
                onClick={() => navigate('/login')}
                className="btn-primary"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="oauth-callback-page" data-testid="oauth-processing">
      <div className="oauth-container">
        <div className="oauth-loading">
          <div className="spinner"></div>
          <h2>Completing Sign In...</h2>
          <p>Please wait while we authenticate your account.</p>
        </div>
      </div>
    </div>
  );
};

export default OAuthCallbackPage;
