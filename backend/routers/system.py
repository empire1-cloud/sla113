"""
System API Routes
Provides system status and configuration information.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from typing import Optional
import os
from functools import lru_cache
from time import time

from services.billing_service import STRIPE_AVAILABLE
from services.oauth_service import is_oauth_configured

router = APIRouter(prefix="/system", tags=["System"])

# Cache for system status (5 minutes TTL)
_status_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 300  # 5 minutes


def get_app_version():
    """Get application version from environment or default."""
    return os.environ.get("APP_VERSION", "2.0.0")


def is_email_configured():
    """Check if email service is properly configured."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    # Check if it's a real key (not placeholder)
    return bool(api_key and not api_key.startswith("re_placeholder"))


@router.get("/status")
async def get_system_status():
    """
    Get system configuration status.
    Returns which external services are enabled/configured.
    
    Useful for:
    - Admin dashboards to show configuration warnings
    - Health monitoring
    - Feature flag checking
    """
    global _status_cache
    
    now = time()
    
    # Return cached data if fresh
    if _status_cache["data"] and (now - _status_cache["timestamp"]) < CACHE_TTL:
        return _status_cache["data"]
    
    # Build fresh status
    status = {
        "version": get_app_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "email_enabled": is_email_configured(),
            "stripe_enabled": STRIPE_AVAILABLE,
            "oauth_enabled": {
                "google": is_oauth_configured("google"),
                "github": is_oauth_configured("github"),
            },
        },
        "mode": "production" if all([
            is_email_configured(),
            STRIPE_AVAILABLE,
            is_oauth_configured("google") or is_oauth_configured("github"),
        ]) else "development",
    }
    
    # Cache the result
    _status_cache = {"data": status, "timestamp": now}
    
    return status


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns minimal info for uptime monitoring.
    """
    return {
        "status": "healthy",
        "version": get_app_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
