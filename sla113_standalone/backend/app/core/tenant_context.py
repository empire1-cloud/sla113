"""Tenant Context — Subdomain-based tenant resolution.

Resolves `tenant-id.sla113.example.com` to a Tenant object and attaches it
to `request.state.tenant`. All tenant-scoped routers depend on this.

If no subdomain is present (e.g., bare domain or `www.`), the request is
treated as the platform root (master admin or public landing).
"""
from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import get_database
from app.core.config import get_settings
import logging
import time

logger = logging.getLogger(__name__)

_TENANT_CACHE = {}
_CACHE_TTL = 60


def _tenant_cache_key(subdomain: str) -> str:
    return f"tenant:{subdomain}"


async def resolve_tenant(request: Request) -> dict | None:
    host = request.headers.get("host", "").split(":")[0]
    settings = get_settings()
    platform_domain = settings.PLATFORM_DOMAIN

    suffix = f".{platform_domain}"
    if not host.endswith(suffix) or host == platform_domain or host.startswith("www."):
        return None

    subdomain = host[: -len(suffix)]
    if not subdomain or "." in subdomain:
        return None

    cache_key = _tenant_cache_key(subdomain)
    cached = _TENANT_CACHE.get(cache_key)
    if cached and (time.time() - cached["ts"]) < settings.TENANT_CACHE_TTL:
        return cached["tenant"]

    db = get_database()
    tenant = await db["sla113_tenants"].find_one(
        {"subdomain": subdomain},
        {"_id": 0},
    )
    if tenant:
        _TENANT_CACHE[cache_key] = {"tenant": tenant, "ts": time.time()}
    return tenant


async def get_current_tenant(request: Request) -> dict:
    tenant = await resolve_tenant(request)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found for this subdomain")
    if tenant.get("status") == "provisioning":
        raise HTTPException(status_code=503, detail="Tenant is still provisioning. Please try again shortly.")
    if tenant.get("status") == "suspended":
        raise HTTPException(status_code=403, detail="Tenant account is suspended.")
    request.state.tenant = tenant
    return tenant


def require_master_admin(request: Request):
    """Guard for master admin endpoints.

    ⚠️ KNOWN GAP (solo-founder pilot phase):
    - Single shared MASTER_API_KEY env var — not rotatable per-user.
    - No audit trail of who used it or when.
    - If leaked, full platform control is exposed until the env var is
      rotated (which invalidates the legitimate user too).
    - Upgrade path: replace with per-admin JWTs + session logging
      before handing admin access to anyone else.
    """
    settings = get_settings()
    auth = request.headers.get("Authorization", "")
    if not settings.MASTER_API_KEY:
        raise HTTPException(status_code=501, detail="Master API key not configured on server")
    if auth != f"Bearer {settings.MASTER_API_KEY}":
        raise HTTPException(status_code=403, detail="Invalid or missing master API key")
    return True


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Resolves tenant from subdomain and attaches to request.state."""

    async def dispatch(self, request: Request, call_next):
        request.state.tenant = await resolve_tenant(request)
        response = await call_next(request)
        return response
