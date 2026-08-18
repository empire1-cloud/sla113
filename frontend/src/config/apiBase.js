const DEFAULT_PRODUCTION_API = 'https://sla113-monieqs-projects.vercel.app';

const trimSlash = (value = '') => value.trim().replace(/\/+$/, '');

/**
 * Resolve the SLA113 API origin once for the browser bundle.
 *
 * Production defaults to the canonical SLA113 Vercel backend. An explicit
 * REACT_APP_BACKEND_URL may override it. Local development keeps the
 * configured value (or localhost:8000).
 */
export function resolveApiBase() {
  const configured = trimSlash(process.env.REACT_APP_BACKEND_URL || '');

  if (typeof window === 'undefined') {
    return configured || DEFAULT_PRODUCTION_API;
  }

  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);

  if (isLocal) {
    return configured || 'http://localhost:8000';
  }

  return configured || DEFAULT_PRODUCTION_API;
}

export const API_BASE = resolveApiBase();
export const API_ROOT = `${API_BASE}/api`;
