"""
lyrica_router.py — SLA113 Universe 1 (Lyrica3) router stub
Routes requests destined for Lyrica3 universe to the correct sub-universe mode.
Full implementation lives in Empire-1/middleware.ts (Next.js edge) and
Lyrica3-pro/backend/server.py (API routing).
"""

LYRICA3_DOMAINS = [
    "lyrica3.com",
    "www.lyrica3.com",
    "api.lyrica3.com",
    "sluniversal.lyrica3.com",
]


def resolve_mode(host: str) -> str:
    """Return the Lyrica3 app mode for a given hostname."""
    if host.startswith("sluniversal."):
        return "universal"
    return "sonance"  # default mode
