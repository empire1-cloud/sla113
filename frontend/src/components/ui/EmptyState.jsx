/**
 * Empty State Component
 * Reusable empty state indicator with customizable icon, title, and action
 */

import { cn } from '../../lib/utils';

export const EmptyState = ({ 
  icon,
  title = 'No data found',
  description,
  action,
  className = '' 
}) => {
  return (
    <div 
      className={cn(
        'flex flex-col items-center justify-center py-16 text-center',
        className
      )} 
      data-testid="empty-state"
    >
      {icon && (
        <div className="text-5xl mb-4 opacity-50">{icon}</div>
      )}
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-[var(--text-secondary)] max-w-md mb-6">
          {description}
        </p>
      )}
      {action && (
        <div className="mt-2">{action}</div>
      )}
    </div>
  );
};

// Pre-configured empty states for common use cases
export const NoDataFound = ({ type = 'items', onAction, actionLabel }) => (
  <EmptyState
    icon="📭"
    title={`No ${type} yet`}
    description={`When you have ${type}, they will appear here.`}
    action={onAction && (
      <button className="btn-primary" onClick={onAction}>
        {actionLabel || `Add ${type}`}
      </button>
    )}
  />
);

export const NoActivityFound = () => (
  <EmptyState
    icon="📋"
    title="No recent activity"
    description="Activity from your team will appear here as actions are performed."
  />
);

export const NoAPIKeysFound = ({ onCreateKey }) => (
  <EmptyState
    icon="🔑"
    title="No API keys yet"
    description="Create your first API key to start accessing the API programmatically."
    action={onCreateKey && (
      <button className="btn-primary" onClick={onCreateKey} data-testid="create-first-key-btn">
        + Create API Key
      </button>
    )}
  />
);

export const NoBillingData = () => (
  <EmptyState
    icon="💳"
    title="Billing not configured"
    description="Payment processing is currently in mock mode. Contact support to enable billing."
  />
);

export default EmptyState;
