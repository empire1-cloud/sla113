/**
 * Billing Page
 * Manage subscription, view usage, and upgrade plans
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { AdminOnly } from '../components/RoleGate';
import { toast } from 'sonner';

const BillingPage = () => {
  const { authAxios, currentTeam } = useAuth();
  
  const [billing, setBilling] = useState(null);
  const [usage, setUsage] = useState(null);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);

  const fetchBillingData = useCallback(async () => {
    if (!currentTeam) return;
    
    setLoading(true);
    try {
      const [billingRes, plansRes] = await Promise.all([
        authAxios().get('/billing/team'),
        authAxios().get('/billing/plans'),
      ]);
      
      setBilling(billingRes.data.billing);
      setUsage(billingRes.data.usage);
      setPlans(plansRes.data.plans);
    } catch (e) {
      console.error('Failed to fetch billing:', e);
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
      const res = await authAxios().post('/billing/checkout-session', {
        plan: planKey,
      });
      
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to create checkout session');
    } finally {
      setUpgrading(false);
    }
  };

  const handleManageBilling = async () => {
    try {
      const res = await authAxios().post('/billing/portal-session', {});
      
      if (res.data.portal_url) {
        window.location.href = res.data.portal_url;
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to open billing portal');
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      active: { class: 'badge-success', text: 'Active' },
      trialing: { class: 'badge-info', text: 'Trial' },
      past_due: { class: 'badge-warning', text: 'Past Due' },
      canceled: { class: 'badge-danger', text: 'Canceled' },
    };
    return badges[status] || { class: '', text: status };
  };

  if (loading) {
    return (
      <div className="page-container" data-testid="billing-loading">
        <div className="page-loading">
          <div className="spinner"></div>
          <p>Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container" data-testid="billing-page">
      <header className="page-header">
        <h1>Billing & Usage</h1>
        <p className="subtitle">{currentTeam?.name}</p>
      </header>

      <div className="billing-grid">
        {/* Current Plan Card */}
        <section className="billing-card current-plan-card" data-testid="current-plan">
          <div className="card-header">
            <h2>Current Plan</h2>
            {billing?.status && (
              <span className={`status-badge ${getStatusBadge(billing.status).class}`}>
                {getStatusBadge(billing.status).text}
              </span>
            )}
          </div>
          
          <div className="plan-details">
            <div className="plan-name">{billing?.plan_name || 'Free'}</div>
            {billing?.current_period_end && (
              <p className="plan-renewal">
                Renews on {formatDate(billing.current_period_end)}
              </p>
            )}
            
            <div className="plan-features">
              {billing?.features?.map((feature, i) => (
                <div key={i} className="feature-item">
                  <span className="feature-check">✓</span>
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>
          
          <AdminOnly>
            {billing?.stripe_configured && billing?.plan !== 'free' && (
              <button
                className="btn-secondary manage-btn"
                onClick={handleManageBilling}
                data-testid="manage-billing-btn"
              >
                Manage Billing
              </button>
            )}
          </AdminOnly>
        </section>

        {/* Usage Card */}
        <section className="billing-card usage-card" data-testid="usage-card">
          <div className="card-header">
            <h2>Current Usage</h2>
            <span className="usage-period">This billing period</span>
          </div>
          
          {usage && (
            <div className="usage-meters">
              <div className="usage-meter" data-testid="executions-usage">
                <div className="meter-header">
                  <span className="meter-label">Executions</span>
                  <span className="meter-value">
                    {usage.usage?.executions_count || 0}
                    {usage.limits?.executions_per_month > 0 && (
                      <span className="meter-limit">
                        / {usage.limits.executions_per_month.toLocaleString()}
                      </span>
                    )}
                    {usage.limits?.executions_per_month === -1 && (
                      <span className="meter-limit">/ Unlimited</span>
                    )}
                  </span>
                </div>
                <div className="meter-bar">
                  <div
                    className={`meter-fill ${usage.over_limit?.executions ? 'over-limit' : ''}`}
                    style={{ width: `${Math.min(100, usage.percentages?.executions || 0)}%` }}
                  />
                </div>
                {usage.over_limit?.executions && (
                  <p className="limit-warning">Limit reached - please upgrade</p>
                )}
              </div>
              
              <div className="usage-stats">
                <div className="stat-item">
                  <span className="stat-label">Team Members</span>
                  <span className="stat-value">
                    {usage.limits?.team_members === -1 ? 'Unlimited' : `Max ${usage.limits?.team_members}`}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">API Keys</span>
                  <span className="stat-value">
                    {usage.limits?.api_keys === -1 ? 'Unlimited' : `Max ${usage.limits?.api_keys}`}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Pipelines</span>
                  <span className="stat-value">
                    {usage.limits?.pipelines === -1 ? 'Unlimited' : `Max ${usage.limits?.pipelines}`}
                  </span>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Available Plans */}
        <AdminOnly>
          <section className="billing-card plans-card" data-testid="plans-section">
            <div className="card-header">
              <h2>Available Plans</h2>
            </div>
            
            <div className="plans-grid">
              {plans.map((plan) => (
                <div
                  key={plan.key}
                  className={`plan-card ${billing?.plan === plan.key ? 'current' : ''}`}
                  data-testid={`plan-${plan.key}`}
                >
                  <div className="plan-card-header">
                    <h3>{plan.name}</h3>
                    {billing?.plan === plan.key && (
                      <span className="current-badge">Current</span>
                    )}
                  </div>
                  
                  <div className="plan-card-limits">
                    <div className="limit-item">
                      <span className="limit-value">
                        {plan.limits.executions_per_month === -1 
                          ? 'Unlimited' 
                          : plan.limits.executions_per_month.toLocaleString()}
                      </span>
                      <span className="limit-label">executions/mo</span>
                    </div>
                    <div className="limit-item">
                      <span className="limit-value">
                        {plan.limits.team_members === -1 ? '∞' : plan.limits.team_members}
                      </span>
                      <span className="limit-label">team members</span>
                    </div>
                  </div>
                  
                  <div className="plan-card-features">
                    {plan.features.map((feature, i) => (
                      <div key={i} className="feature-item">
                        <span className="feature-check">✓</span>
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  {plan.key !== billing?.plan && plan.has_price && billing?.stripe_configured && (
                    <button
                      className="btn-primary upgrade-btn"
                      onClick={() => handleUpgrade(plan.key)}
                      disabled={upgrading}
                      data-testid={`upgrade-${plan.key}`}
                    >
                      {upgrading ? 'Processing...' : `Upgrade to ${plan.name}`}
                    </button>
                  )}
                  
                  {plan.key === 'enterprise' && !plan.has_price && (
                    <button className="btn-secondary contact-btn">
                      Contact Sales
                    </button>
                  )}
                </div>
              ))}
            </div>
          </section>
        </AdminOnly>
      </div>
    </div>
  );
};

export default BillingPage;
