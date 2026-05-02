/**
 * Billing Page
 * Manage subscription, view usage, and upgrade plans
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminOnly } from '../components/RoleGate';
import { toast } from 'sonner';
import { PageLoading } from '../components/ui/LoadingState';
import { NoBillingData } from '../components/ui/EmptyState';
import { getErrorMessage } from '../components/ui/ErrorMessage';

const BillingPage = () => {
  const { authAxios, currentTeam } = useAuth();
  
  const [data, setData] = useState(null);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [error, setError] = useState('');

  const fetchBillingData = useCallback(async () => {
    if (!currentTeam) return;
    
    setLoading(true);
    setError('');
    try {
      const billingRes = await authAxios().get('/billing/team');
      const plansRes = await authAxios().get('/billing/plans');
      
      setData(billingRes.data);
      setPlans(plansRes.data.plans || []);
    } catch (e) {
      console.error('Failed to fetch billing:', e);
      setError(getErrorMessage(e));
      toast.error('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  }, [authAxios, currentTeam]);

  useEffect(() => {
    fetchBillingData();
  }, [fetchBillingData]);

  const handleUpgrade = async (planKey) => {
    setUpgrading(true);
    try {
      const res = await authAxios().post('/billing/checkout-session', { plan: planKey });
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      } else {
        toast.info('Stripe is not configured. Running in mock mode.');
      }
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setUpgrading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const res = await authAxios().post('/billing/portal-session', {});
      if (res.data.portal_url) {
        window.location.href = res.data.portal_url;
      } else {
        toast.info('Stripe is not configured. Running in mock mode.');
      }
    } catch (e) {
      toast.error(getErrorMessage(e));
    }
  };

  if (loading) {
    return <PageLoading message="Loading billing information..." />;
  }

  if (error || !data) {
    return (
      <div className="page-container" data-testid="billing-error">
        <header className="page-header">
          <h1>Billing & Usage</h1>
          <p className="subtitle">{currentTeam?.name}</p>
        </header>
        <NoBillingData />
      </div>
    );
  }

  const billing = data.billing || {};
  const usage = data.usage || {};
  const teamName = currentTeam ? currentTeam.name : '';
  const stripeConfigured = billing.stripe_configured;

  return (
    <div className="page-container" data-testid="billing-page">
      <header className="page-header">
        <h1>Billing & Usage</h1>
        <p className="subtitle">{teamName}</p>
      </header>

      {!stripeConfigured && (
        <div className="mock-mode-banner" data-testid="mock-mode-banner">
          <span className="banner-icon">ℹ️</span>
          <span className="banner-text">
            <strong>Mock Mode:</strong> Stripe is not configured. Billing features are simulated.
          </span>
        </div>
      )}

      <div className="billing-grid">
        <section className="billing-card settings-card" data-testid="current-plan">
          <div className="card-header">
            <h2>Current Plan</h2>
            <span className="status-badge badge-success">{billing.status || 'Active'}</span>
          </div>
          <div className="card-body" style={{ padding: '1.25rem' }}>
            <div className="plan-details">
              <div className="plan-name">{billing.plan_name || 'Free'}</div>
            </div>
            <AdminOnly>
              {stripeConfigured && billing.plan !== 'free' && (
                <button 
                  className="btn-secondary manage-btn" 
                  onClick={handleManageBilling}
                  disabled={upgrading}
                >
                  Manage Billing
                </button>
              )}
            </AdminOnly>
          </div>
        </section>

        <section className="billing-card settings-card" data-testid="usage-card">
          <div className="card-header">
            <h2>Current Usage</h2>
          </div>
          <div className="card-body" style={{ padding: '1.25rem' }}>
            <div className="usage-meters">
              <div className="usage-meter">
                <div className="meter-header">
                  <span className="meter-label">Executions</span>
                  <span className="meter-value">
                    {usage.usage ? usage.usage.executions_count : 0} / {usage.limits ? usage.limits.executions_per_month : 100}
                  </span>
                </div>
                <div className="meter-bar">
                  <div 
                    className="meter-fill" 
                    style={{ width: `${Math.min(usage.percentages ? usage.percentages.executions : 0, 100)}%` }} 
                  />
                </div>
                {(usage.percentages?.executions || 0) > 80 && (
                  <p className="usage-warning">Approaching usage limit</p>
                )}
              </div>
            </div>
          </div>
        </section>

        <AdminOnly>
          <section className="billing-card settings-card plans-card" data-testid="plans-section">
            <div className="card-header">
              <h2>Available Plans</h2>
            </div>
            <div className="card-body" style={{ padding: '1.25rem' }}>
              {plans.length === 0 ? (
                <p className="no-plans">No plans available</p>
              ) : (
                <div className="plans-grid">
                  {plans.map((plan) => (
                    <div key={plan.key} className="plan-card" data-testid={`plan-${plan.key}`}>
                      <h3>{plan.name}</h3>
                      <div className="plan-card-limits">
                        <span>
                          {plan.limits.executions_per_month === -1 
                            ? 'Unlimited' 
                            : plan.limits.executions_per_month} executions/mo
                        </span>
                      </div>
                      {billing.plan !== plan.key && plan.has_price && stripeConfigured && (
                        <button 
                          className="btn-primary" 
                          onClick={() => handleUpgrade(plan.key)} 
                          disabled={upgrading}
                        >
                          {upgrading ? 'Processing...' : 'Upgrade'}
                        </button>
                      )}
                      {billing.plan === plan.key && (
                        <span className="current-plan-badge">Current Plan</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </AdminOnly>
      </div>

      <style>{`
        .mock-mode-banner {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem 1rem;
          margin-bottom: 1.5rem;
          background: rgba(77, 159, 255, 0.1);
          border: 1px solid rgba(77, 159, 255, 0.3);
          border-radius: 8px;
        }

        .mock-mode-banner .banner-icon {
          font-size: 1rem;
        }

        .mock-mode-banner .banner-text {
          font-size: 0.85rem;
          color: var(--accent-blue);
        }

        .usage-warning {
          font-size: 0.8rem;
          color: var(--accent-orange);
          margin-top: 0.5rem;
        }

        .current-plan-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: rgba(0, 212, 170, 0.15);
          color: var(--accent-green);
          border-radius: 9999px;
          font-size: 0.8rem;
          font-weight: 500;
          margin-top: 0.5rem;
        }

        .no-plans {
          color: var(--text-secondary);
          text-align: center;
          padding: 2rem;
        }
      `}</style>
    </div>
  );
};

export default BillingPage;
