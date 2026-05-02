/**
 * Error Message Components
 * Standardized error display components
 */

import { cn } from '../../lib/utils';

// Map of error codes to user-friendly messages
const ERROR_MESSAGES = {
  // Auth errors
  'invalid_credentials': 'Invalid email or password. Please try again.',
  'user_not_found': 'No account found with this email address.',
  'email_already_exists': 'An account with this email already exists.',
  'weak_password': 'Password does not meet security requirements.',
  'invalid_token': 'Your session has expired. Please log in again.',
  
  // Password reset errors
  'expired_reset_token': 'This password reset link has expired. Please request a new one.',
  'invalid_reset_token': 'This password reset link is invalid. Please request a new one.',
  'reset_token_used': 'This password reset link has already been used.',
  
  // Invite errors
  'expired_invite': 'This invitation has expired. Please ask for a new invite.',
  'invalid_invite': 'This invitation link is invalid.',
  'invite_already_accepted': 'This invitation has already been accepted.',
  'already_team_member': 'You are already a member of this team.',
  
  // Billing errors
  'billing_not_configured': 'Payment processing is currently unavailable. Please try again later.',
  'stripe_error': 'Payment processing error. Please try again or contact support.',
  'usage_limit_exceeded': 'You have reached your usage limit. Please upgrade your plan.',
  'invalid_plan': 'The selected plan is not available.',
  
  // API errors
  'rate_limited': 'Too many requests. Please wait a moment and try again.',
  'forbidden': 'You do not have permission to perform this action.',
  'not_found': 'The requested resource was not found.',
  'server_error': 'An unexpected error occurred. Please try again later.',
  
  // Network errors
  'network_error': 'Unable to connect. Please check your internet connection.',
  'timeout': 'The request timed out. Please try again.',
};

/**
 * Get a user-friendly error message
 */
export const getErrorMessage = (error) => {
  // Handle string errors
  if (typeof error === 'string') {
    return ERROR_MESSAGES[error] || error;
  }
  
  // Handle axios error responses
  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    // Check if it's a known error code
    if (typeof detail === 'string' && ERROR_MESSAGES[detail.toLowerCase()]) {
      return ERROR_MESSAGES[detail.toLowerCase()];
    }
    
    return detail;
  }
  
  // Handle error objects with message
  if (error?.message) {
    // Network errors
    if (error.message === 'Network Error') {
      return ERROR_MESSAGES['network_error'];
    }
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

/**
 * Error Alert Component
 */
export const ErrorAlert = ({ 
  error, 
  title,
  onDismiss,
  className = '' 
}) => {
  const message = getErrorMessage(error);
  
  return (
    <div 
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg',
        'bg-[rgba(255,107,107,0.1)] border border-[rgba(255,107,107,0.3)]',
        className
      )}
      role="alert"
      data-testid="error-alert"
    >
      <span className="text-[var(--accent-red)] text-lg flex-shrink-0">⚠️</span>
      <div className="flex-1">
        {title && (
          <h4 className="font-semibold text-[var(--accent-red)] mb-1">{title}</h4>
        )}
        <p className="text-sm text-[var(--accent-red)]">{message}</p>
      </div>
      {onDismiss && (
        <button 
          onClick={onDismiss}
          className="text-[var(--accent-red)] hover:opacity-70 text-lg"
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  );
};

/**
 * Inline Error (for form fields)
 */
export const FieldError = ({ error, className = '' }) => {
  if (!error) return null;
  
  const message = getErrorMessage(error);
  
  return (
    <span 
      className={cn('field-error text-[var(--accent-red)] text-xs mt-1', className)}
      role="alert"
    >
      {message}
    </span>
  );
};

/**
 * Form Error Banner
 */
export const FormError = ({ error, className = '' }) => {
  if (!error) return null;
  
  const message = getErrorMessage(error);
  
  return (
    <div 
      className={cn('auth-error mb-4', className)}
      role="alert"
      data-testid="form-error"
    >
      {message}
    </div>
  );
};

export default { ErrorAlert, FieldError, FormError, getErrorMessage, ERROR_MESSAGES };
