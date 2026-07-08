"""System config — HYBRID_AI shim."""

def get_system_info():
    return {
        "version": "1.0.0-hybrid",
        "environment": "production",
        "providers": {"local": True},
        "model": "gemma-4-26b-a4b",
    }
