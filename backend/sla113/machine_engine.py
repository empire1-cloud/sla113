"""
machine_engine.py
SLA113 Arcade — Machine Engine
Routes tenant → machine_type → engine class.

Reads machine_catalog from Build Spec tenant config.
Enforces: tenants can only access machine types their catalog enables.
Handles theme resolution per tenant (machine_theme_slots, etc.)

Tenant machine catalogs (from Build Spec):
  tenant_casino_vegas:  fish=true, slots=true, keno=true,  custom=false
  tenant_arcade_london: fish=true, slots=true, keno=false, custom=true
  tenant_gaming_sydney: fish=true, slots=true, keno=true,  custom=true
"""

from typing import Optional
from .fishing_engine_v2 import FishingEngineV2
from .slots_engine_v1 import SlotsEngineV1
from .keno_engine_v1 import KenoEngineV1

# Machine catalog derived from Build Spec tenants section
TENANT_MACHINE_CATALOG = {
    "tenant_casino_vegas": {
        "fish":   {"enabled": True,  "theme": None,          "rtp_override": 0.95},
        "slots":  {"enabled": True,  "theme": "gold_rush",   "rtp_override": 0.95},
        "keno":   {"enabled": True,  "theme": None,          "rtp_override": 0.95},
        "custom": {"enabled": False, "theme": None,          "rtp_override": None},
        "default": "slots",
    },
    "tenant_arcade_london": {
        "fish":   {"enabled": True,  "theme": None,           "rtp_override": 0.94},
        "slots":  {"enabled": True,  "theme": "space_odyssey","rtp_override": 0.94},
        "keno":   {"enabled": False, "theme": None,           "rtp_override": None},
        "custom": {"enabled": True,  "theme": None,           "rtp_override": 0.94},
        "default": "fish",
    },
    "tenant_gaming_sydney": {
        "fish":   {"enabled": True,  "theme": None,          "rtp_override": 0.96},
        "slots":  {"enabled": True,  "theme": "wild_west",   "rtp_override": 0.96},
        "keno":   {"enabled": True,  "theme": None,          "rtp_override": 0.96},
        "custom": {"enabled": True,  "theme": None,          "rtp_override": 0.96},
        "default": "slots",
    },
    # Legacy EMPIRE 1 internal tenants (existing sla113_constants entries)
    "southern_lyfestyle_arcade": {
        "fish":   {"enabled": True,  "theme": None, "rtp_override": 0.94},
        "slots":  {"enabled": False, "theme": None, "rtp_override": None},
        "keno":   {"enabled": False, "theme": None, "rtp_override": None},
        "custom": {"enabled": False, "theme": None, "rtp_override": None},
        "default": "fish",
    },
    "horror_arcade": {
        "fish":   {"enabled": False, "theme": None, "rtp_override": None},
        "slots":  {"enabled": True,  "theme": None, "rtp_override": 0.95},
        "keno":   {"enabled": False, "theme": None, "rtp_override": None},
        "custom": {"enabled": True,  "theme": None, "rtp_override": 0.94},
        "default": "slots",
    },
    "anime_arcade": {
        "fish":   {"enabled": True,  "theme": None, "rtp_override": 0.94},
        "slots":  {"enabled": True,  "theme": None, "rtp_override": 0.95},
        "keno":   {"enabled": False, "theme": None, "rtp_override": None},
        "custom": {"enabled": True,  "theme": None, "rtp_override": 0.94},
        "default": "slots",
    },
}

MACHINE_TYPE_MAP = {
    "fish": FishingEngineV2,
    "slots": SlotsEngineV1,
    "keno": KenoEngineV1,
}


class MachineEngine:
    ENGINE_ID = "machine_engine"
    ENGINE_TYPE = "arcade"
    VERSION = "1.0.0"

    def get_catalog(self, tenant_id: str) -> dict:
        """Return the machine catalog for a tenant."""
        catalog = TENANT_MACHINE_CATALOG.get(tenant_id)
        if not catalog:
            return {"error": f"No machine catalog found for tenant: {tenant_id}"}
        return {
            "tenant_id": tenant_id,
            "machines": {
                k: v for k, v in catalog.items() if k != "default"
            },
            "default_machine_type": catalog.get("default"),
        }

    def resolve_engine(
        self,
        tenant_id: str,
        machine_type: Optional[str] = None,
    ) -> tuple:
        """
        Resolve and instantiate the correct engine for a tenant + machine_type.
        Returns (engine_instance, machine_config) or raises ValueError.
        machine_type defaults to the tenant's default if not specified.
        """
        catalog = TENANT_MACHINE_CATALOG.get(tenant_id)
        if not catalog:
            raise ValueError(f"Unknown tenant: {tenant_id}")

        machine_type = machine_type or catalog.get("default", "slots")

        machine_config = catalog.get(machine_type)
        if not machine_config:
            raise ValueError(f"Machine type '{machine_type}' not in catalog for tenant '{tenant_id}'")

        if not machine_config.get("enabled", False):
            raise ValueError(
                f"Machine type '{machine_type}' is not enabled for tenant '{tenant_id}'"
            )

        engine_class = MACHINE_TYPE_MAP.get(machine_type)
        if not engine_class:
            raise ValueError(f"No engine implementation for machine type: {machine_type}")

        rtp = machine_config.get("rtp_override") or 0.95
        theme = machine_config.get("theme")

        # Instantiate with tenant-specific config
        if machine_type == "slots" and theme:
            engine = engine_class(rtp=rtp, theme=theme)
        elif machine_type in ("fish", "keno"):
            engine = engine_class(rtp=rtp)
        else:
            engine = engine_class(rtp=rtp)

        return engine, machine_config
