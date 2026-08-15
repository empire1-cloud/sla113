const DEFAULT_PRODUCTION_API = 'https://sla113-backend-339698334666.us-central1.run.app';

const trimSlash = (value = '') => value.trim().replace(/\/+$/, '');

/**
 * Resolve the SLA113 API origin once for the browser bundle.
 *
 * Production used to be built with REACT_APP_BACKEND_URL pointing at the
 * frontend's own custom domain. That made /api/auth/* requests hit the static
 * frontend instead of FastAPI and surfaced only "Signup failed".
 *
 * Prefer an explicit non-self origin. If production is missing the env var or
 * it points back at the frontend itself, fail over to the deployed Cloud Run
 * API. Local development keeps the configured value (or localhost:8000).
 */
export function resolveApiBase() {
  const configured = trimSlash(process.env.REACT_APP_BACKEND_URL || '');

  if (typeof window === 'undefined') {
    return configured || DEFAULT_PRODUCTION_API;
  }

  const currentOrigin = trimSlash(window.location.origin);
  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);

  if (isLocal) {
    return configured || 'http://localhost:8000';
  }

  if (configured && configured !== currentOrigin) {
    return configured;
  }

  return DEFAULT_PRODUCTION_API;
}

export const API_BASE = resolveApiBase();
export const API_ROOT = `${API_BASE}/api`;
