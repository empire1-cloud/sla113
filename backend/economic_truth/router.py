"""FastAPI surface for the Economic Truth lifecycle and Receipt Graph."""

from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from core.dependencies import get_current_user
from .domain import EconomicTruthError


class FlexiblePayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class ProposalPayload(FlexiblePayload):
    action_type: str
    organization_id: str
    actor_id: str
    charter_id: str
    policy_id: str
    idempotency_key: str
    intent_token_id: str | None = None
    target: dict[str, Any] = Field(default_factory=dict)
    economic_value: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, Any] = Field(default_factory=dict)


def create_economic_truth_router(service_provider) -> APIRouter:
    router = APIRouter(prefix="/economic-truth", tags=["Economic Truth"])

    def service():
        return service_provider()

    def require_write_key(x_economic_truth_key: str | None = Header(None)) -> None:
        expected = os.getenv("ECONOMIC_TRUTH_INGEST_KEY", "").strip()
        if not expected:
            raise HTTPException(status_code=503, detail="Economic Truth ingestion is not configured")
        if not x_economic_truth_key or not hmac.compare_digest(expected, x_economic_truth_key):
            raise HTTPException(status_code=401, detail="Invalid Economic Truth credentials")

    @router.post("/actions", dependencies=[])
    async def propose(payload: ProposalPayload, x_economic_truth_key: str | None = Header(None)):
        require_write_key(x_economic_truth_key)
        try:
            return await service().propose(payload.model_dump())
        except EconomicTruthError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/actions/{action_id}/authorize")
    async def authorize(action_id: str, payload: FlexiblePayload, x_economic_truth_key: str | None = Header(None)):
        require_write_key(x_economic_truth_key)
        try:
            return await service().authorize(action_id, payload.model_dump())
        except EconomicTruthError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/actions/{action_id}/outcome")
    async def outcome(action_id: str, payload: FlexiblePayload, x_economic_truth_key: str | None = Header(None)):
        require_write_key(x_economic_truth_key)
        body = payload.model_dump()
        try:
            return await service().record_outcome(action_id, body, refused=bool(body.pop("refused", False)))
        except EconomicTruthError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/actions/{action_id}/verify")
    async def verify(action_id: str, payload: FlexiblePayload, x_economic_truth_key: str | None = Header(None)):
        require_write_key(x_economic_truth_key)
        try:
            return await service().verify(action_id, payload.model_dump())
        except EconomicTruthError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/actions/{action_id}/reverse")
    async def reverse(action_id: str, payload: FlexiblePayload, x_economic_truth_key: str | None = Header(None)):
        require_write_key(x_economic_truth_key)
        try:
            return await service().reverse(action_id, payload.model_dump())
        except EconomicTruthError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/receipts/{receipt_id}")
    async def receipt(receipt_id: str):
        value = await service().store.get_receipt(receipt_id)
        if not value:
            raise HTTPException(status_code=404, detail="Receipt not found")
        return {"receipt": value, "verified": await service().verify_envelope(value)}

    @router.post("/verify-envelope")
    async def verify_envelope(payload: FlexiblePayload):
        body = payload.model_dump()
        return {"verified": await service().verify_envelope(body), "receipt_id": body.get("receipt_id")}

    @router.get("/graph/{organization_id}")
    async def graph(organization_id: str, user: dict = Depends(get_current_user)):
        if str(user.get("team_id")) != organization_id and user.get("system_role") != "admin":
            raise HTTPException(status_code=403, detail="Receipt Graph belongs to another organization")
        return await service().graph(organization_id)

    @router.get("/metrics/{organization_id}")
    async def metrics(organization_id: str, user: dict = Depends(get_current_user)):
        if str(user.get("team_id")) != organization_id and user.get("system_role") != "admin":
            raise HTTPException(status_code=403, detail="Metrics belong to another organization")
        return await service().metrics(organization_id)

    @router.get("/coverage")
    async def coverage():
        return await service().coverage()

    return router
