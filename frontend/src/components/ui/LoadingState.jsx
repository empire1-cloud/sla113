/**
 * Loading State Component
 * Reusable loading indicator with optional message
 */

import { cn } from '../../lib/utils';

export const LoadingState = ({ 
  message = 'Loading...', 
  size = 'default',
  className = '' 
}) => {
  const spinnerSizes = {
    small: 'w-5 h-5 border-2',
    default: 'w-10 h-10 border-3',
    large: 'w-16 h-16 border-4',
  };

  return (
    <div className={cn('flex flex-col items-center justify-center gap-4 py-12', className)} data-testid="loading-state">
      <div 
        className={cn(
          'rounded-full border-t-[var(--accent-green)] border-[var(--border-color)] animate-spin',
          spinnerSizes[size] || spinnerSizes.default
        )}
        style={{ borderStyle: 'solid' }}
      />
      {message && (
        <p className="text-[var(--text-secondary)] text-sm">{message}</p>
      )}
    </div>
  );
};

export const PageLoading = ({ message = 'Loading...' }) => (
  <div className="page-container" data-testid="page-loading">
    <div className="page-loading">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  </div>
);

export const InlineLoading = ({ size = 'small' }) => (
  <span className="inline-flex items-center gap-2">
    <span className={cn(
      'rounded-full border-t-[var(--accent-green)] border-[var(--border-color)] animate-spin',
      size === 'small' ? 'w-4 h-4 border-2' : 'w-6 h-6 border-2'
    )} style={{ borderStyle: 'solid' }} />
  </span>
);

export default LoadingState;
