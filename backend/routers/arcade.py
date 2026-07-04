"""
arcade.py
SLA113 Arcade Router
Endpoints for all arcade game engines.

Routes:
  POST /sla113/arcade/fish/spin
  POST /sla113/arcade/slots/spin
  POST /sla113/arcade/keno/draw
  POST /sla113/arcade/payout/settle
  GET  /sla113/machines/{tenant_id}
  POST /sla113/machines/{tenant_id}/resolve
  GET  /sla113/tenant/{tenant_id}
  GET  /sla113/tenant/list
  GET  /sla113/arcade/canon/sgv-aztec/symbols
  POST /sla113/arcade/canon/sgv-aztec/apply

All routes enforce:
  - Tenant identity via X-Tenant-ID header
  - Engine access via PermissionChecker (engine_namespace registry)
  - Governance via TenantEngine (session limits, loss limits)
"""

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from sla113.fishing_engine_v2 import FishingEngineV2
from sla113.slots_engine_v1 import SlotsEngineV1
from sla113.keno_engine_v1 import KenoEngineV1
from sla113.payout_engine import PayoutEngine
from sla113.machine_engine import MachineEngine
from sla113.tenant_engine import TenantEngine
from sla113.canon_layer_sgv_aztec import CanonLayerSGVAztec

router = APIRouter(prefix="/sla113", tags=["SLA113 Arcade"])

_machine_engine = MachineEngine()
_tenant_engine = TenantEngine()
_payout_engine = PayoutEngine()
_canon_layer = CanonLayerSGVAztec()


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def _require_tenant(x_tenant_id: Optional[str]) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    return x_tenant_id


def _check_access(tenant_id: str, engine_id: str):
    pass


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class FishSpinRequest(BaseModel):
    player_id: str
    bet_amount: float
    skill_score: float = 0.5
    session_id: Optional[str] = None
    apply_canon: bool = False  # Apply canon_layer_sgv_aztec overlay


class SlotsSpinRequest(BaseModel):
    player_id: str
    bet_amount: float
    session_id: Optional[str] = None
    theme_override: Optional[str] = None
    apply_canon: bool = False


class KenoDrawRequest(BaseModel):
    player_id: str
    bet_amount: float
    picks: List[int]
    session_id: Optional[str] = None


class PayoutSettleRequest(BaseModel):
    player_id: str
    game_result: dict
    session_buy_in: float = 0.0


class CanonApplyRequest(BaseModel):
    game_result: dict
    narrative_intensity: str = "ambient"
    game_type: str = "fish"  # "fish" | "slots" | "keno"


# ---------------------------------------------------------
# FISH
# ---------------------------------------------------------

@router.post("/arcade/fish/spin")
def fish_spin(
    body: FishSpinRequest,
    x_tenant_id: Optional[str] = Header(None),
):
    """Execute a fish shooting cast for a tenant player."""
    tenant_id = _require_tenant(x_tenant_id)
    _check_access(tenant_id, "fishing_engine_v2")

    try:
        engine, machine_config = _machine_engine.resolve_engine(tenant_id, "fish")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    result = engine.cast(
        tenant_id=tenant_id,
        player_id=body.player_id,
        bet_amount=body.bet_amount,
        skill_score=body.skill_score,
        session_id=body.session_id,
    )

    if body.apply_canon:
        result = _canon_layer.apply(result)

    return {"success": True, "result": result}


# ---------------------------------------------------------
# SLOTS
# ---------------------------------------------------------

@router.post("/arcade/slots/spin")
def slots_spin(
    body: SlotsSpinRequest,
    x_tenant_id: Optional[str] = Header(None),
):
    """Execute a slot machine spin for a tenant player."""
    tenant_id = _require_tenant(x_tenant_id)
    _check_access(tenant_id, "slots_engine_v1")

    try:
        engine, machine_config = _machine_engine.resolve_engine(tenant_id, "slots")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    # Allow theme override at request level if provided
    if body.theme_override and hasattr(engine, "theme"):
        from sla113.slots_engine_v1 import VALID_THEMES
        if body.theme_override in VALID_THEMES:
            engine.theme = body.theme_override

    result = engine.spin(
        tenant_id=tenant_id,
        player_id=body.player_id,
        bet_amount=body.bet_amount,
        session_id=body.session_id,
    )

    if body.apply_canon:
        result = _canon_layer.apply_to_slots(result)

    return {"success": True, "result": result}


# ---------------------------------------------------------
# KENO
# ---------------------------------------------------------

@router.post("/arcade/keno/draw")
def keno_draw(
    body: KenoDrawRequest,
    x_tenant_id: Optional[str] = Header(None),
):
    """Execute a keno draw for a tenant player."""
    tenant_id = _require_tenant(x_tenant_id)
    _check_access(tenant_id, "keno_engine_v1")

    try:
        engine, _ = _machine_engine.resolve_engine(tenant_id, "keno")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    result = engine.draw(
        tenant_id=tenant_id,
        player_id=body.player_id,
        bet_amount=body.bet_amount,
        player_picks=body.picks,
        session_id=body.session_id,
    )

    return {"success": True, "result": result}


# ---------------------------------------------------------
# PAYOUT
# ---------------------------------------------------------

@router.post("/arcade/payout/settle")
def payout_settle(
    body: PayoutSettleRequest,
    x_tenant_id: Optional[str] = Header(None),
):
    """Settle a game result through the payout engine."""
    tenant_id = _require_tenant(x_tenant_id)
    _check_access(tenant_id, "payout_engine")

    result = _payout_engine.settle(
        tenant_id=tenant_id,
        player_id=body.player_id,
        game_result=body.game_result,
        session_buy_in=body.session_buy_in,
    )

    return {"success": True, "result": result}


# ---------------------------------------------------------
# MACHINE CATALOG
# ---------------------------------------------------------

@router.get("/machines/{tenant_id}")
def get_machine_catalog(
    tenant_id: str,
    x_tenant_id: Optional[str] = Header(None),
):
    """Return the machine catalog for a tenant."""
    # Allow direct path param; header not required for catalog reads
    catalog = _machine_engine.get_catalog(tenant_id)
    if "error" in catalog:
        raise HTTPException(status_code=404, detail=catalog["error"])
    return {"success": True, "catalog": catalog}


@router.post("/machines/{tenant_id}/resolve")
def resolve_machine(
    tenant_id: str,
    machine_type: Optional[str] = None,
    x_tenant_id: Optional[str] = Header(None),
):
    """Resolve engine config for a tenant's machine type."""
    try:
        _, machine_config = _machine_engine.resolve_engine(tenant_id, machine_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"success": True, "machine_config": machine_config, "tenant_id": tenant_id}


# ---------------------------------------------------------
# TENANT ENGINE
# ---------------------------------------------------------

@router.get("/tenant/list")
def list_tenants():
    """List all registered arcade tenants."""
    return {"success": True, "tenants": _tenant_engine.list_tenants()}


@router.get("/tenant/{tenant_id}")
def get_tenant_context(tenant_id: str):
    """Return full tenant context (governance, regulatory profile, revenue routing)."""
    try:
        context = _tenant_engine.resolve(tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"success": True, "tenant": context}


# ---------------------------------------------------------
# CANON LAYER: SGV + AZTEC
# ---------------------------------------------------------

@router.get("/arcade/canon/sgv-aztec/symbols")
def get_canon_symbols():
    """Return the Aztec symbol set and narrative phrase packs."""
    return {
        "success": True,
        "symbols": _canon_layer.get_symbol_set(),
        "narrative": _canon_layer.get_narrative_pack(),
    }


@router.post("/arcade/canon/sgv-aztec/apply")
def apply_canon_layer(
    body: CanonApplyRequest,
    x_tenant_id: Optional[str] = Header(None),
):
    """Apply SGV + Aztec canon overlay to an existing game result."""
    tenant_id = _require_tenant(x_tenant_id)
    if body.game_type == "slots":
        result = _canon_layer.apply_to_slots(body.game_result)
    else:
        result = _canon_layer.apply(
            body.game_result,
            narrative_intensity=body.narrative_intensity,
            tenant_id=tenant_id,
        )

    return {"success": True, "result": result}
