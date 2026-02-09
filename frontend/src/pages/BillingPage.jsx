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
  
  const [data, setData] = useState(null);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);

  const fetchBillingData = useCallback(async () => {
    if (!currentTeam) return;
    
    setLoading(true);
    try {
      const billingRes = await authAxios().get('/billing/team');
      const plansRes = await authAxios().get('/billing/plans');
      
      setData(billingRes.data);
      setPlans(plansRes.data.plans || []);
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
      const res = await authAxios().post('/billing/checkout-session', { plan: planKey });
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (e) {
      toast.error('Failed to create checkout session');
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
      toast.error('Failed to open billing portal');
    }
  };

  if (loading || !data) {
    return (
      <div className="page-container" data-testid="billing-loading">
        <div className="page-loading">
          <div className="spinner"></div>
          <p>Loading billing information...</p>
        </div>
      </div>
    );
  }

  const billing = data.billing || {};
  const usage = data.usage || {};
  const teamName = currentTeam ? currentTeam.name : '';

  return (
    <div className="page-container" data-testid="billing-page">
      <header className="page-header">
        <h1>Billing & Usage</h1>
        <p className="subtitle">{teamName}</p>
      </header>

      <div className="billing-grid">
        <section className="billing-card" data-testid="current-plan">
          <div className="card-header">
            <h2>Current Plan</h2>
            <span className="status-badge badge-success">{billing.status || 'Active'}</span>
          </div>
          <div className="plan-details">
            <div className="plan-name">{billing.plan_name || 'Free'}</div>
          </div>
          <AdminOnly>
            {billing.stripe_configured && billing.plan !== 'free' && (
              <button className="btn-secondary manage-btn" onClick={handleManageBilling}>
                Manage Billing
              </button>
            )}
          </AdminOnly>
        </section>

        <section className="billing-card" data-testid="usage-card">
          <div className="card-header">
            <h2>Current Usage</h2>
          </div>
          <div className="usage-meters">
            <div className="usage-meter">
              <div className="meter-header">
                <span className="meter-label">Executions</span>
                <span className="meter-value">
                  {usage.usage ? usage.usage.executions_count : 0} / {usage.limits ? usage.limits.executions_per_month : 100}
                </span>
              </div>
              <div className="meter-bar">
                <div className="meter-fill" style={{ width: `${usage.percentages ? usage.percentages.executions : 0}%` }} />
              </div>
            </div>
          </div>
        </section>

        <AdminOnly>
          <section className="billing-card plans-card" data-testid="plans-section">
            <div className="card-header">
              <h2>Available Plans</h2>
            </div>
            <div className="plans-grid">
              {plans.map((plan) => (
                <div key={plan.key} className="plan-card" data-testid={`plan-${plan.key}`}>
                  <h3>{plan.name}</h3>
                  <div className="plan-card-limits">
                    <span>{plan.limits.executions_per_month === -1 ? 'Unlimited' : plan.limits.executions_per_month} executions/mo</span>
                  </div>
                  {billing.plan !== plan.key && plan.has_price && billing.stripe_configured && (
                    <button className="btn-primary" onClick={() => handleUpgrade(plan.key)} disabled={upgrading}>
                      Upgrade
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
