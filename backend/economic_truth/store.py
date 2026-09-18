"""Persistence adapters for actions, immutable receipts, graph edges and coverage."""

from __future__ import annotations

import copy
from typing import Any, Optional


class DuplicateEconomicAction(RuntimeError):
    pass


class MemoryEconomicTruthStore:
    def __init__(self) -> None:
        self.actions: dict[str, dict[str, Any]] = {}
        self.idempotency: dict[tuple[str, str], str] = {}
        self.receipts: dict[str, dict[str, Any]] = {}
        self.external_events: dict[tuple[str, str], str] = {}
        self.surfaces: dict[str, dict[str, Any]] = {}

    async def initialize(self) -> None:
        return None

    async def create_action(self, action: dict[str, Any]) -> dict[str, Any]:
        key = (action["organization_id"], action["idempotency_key"])
        if key in self.idempotency:
            return copy.deepcopy(self.actions[self.idempotency[key]])
        self.idempotency[key] = action["action_id"]
        self.actions[action["action_id"]] = copy.deepcopy(action)
        return copy.deepcopy(action)

    async def get_action(self, action_id: str) -> Optional[dict[str, Any]]:
        value = self.actions.get(action_id)
        return copy.deepcopy(value) if value else None

    async def save_action(self, action: dict[str, Any]) -> None:
        self.actions[action["action_id"]] = copy.deepcopy(action)

    async def save_receipt(self, receipt: dict[str, Any]) -> None:
        self.receipts.setdefault(receipt["receipt_id"], copy.deepcopy(receipt))

    async def get_receipt(self, receipt_id: str) -> Optional[dict[str, Any]]:
        value = self.receipts.get(receipt_id)
        return copy.deepcopy(value) if value else None

    async def latest_receipt(self, organization_id: str) -> Optional[dict[str, Any]]:
        values = [r for r in self.receipts.values() if r["organization_id"] == organization_id]
        return copy.deepcopy(max(values, key=lambda r: r["issued_at"])) if values else None

    async def list_receipts(self, organization_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        values = [copy.deepcopy(r) for r in self.receipts.values() if r["organization_id"] == organization_id]
        return sorted(values, key=lambda r: r["issued_at"], reverse=True)[:limit]

    async def claim_external_event(self, source: str, external_id: str, action_id: str) -> Optional[str]:
        key = (source, external_id)
        existing = self.external_events.get(key)
        if existing:
            return existing
        self.external_events[key] = action_id
        return None

    async def upsert_surface(self, surface: dict[str, Any]) -> None:
        self.surfaces[surface["surface_id"]] = copy.deepcopy(surface)

    async def list_surfaces(self) -> list[dict[str, Any]]:
        return [copy.deepcopy(v) for v in self.surfaces.values()]


class MongoEconomicTruthStore:
    def __init__(self, database: Any) -> None:
        self.db = database

    async def initialize(self) -> None:
        await self.db.economic_actions.create_index(
            [("organization_id", 1), ("idempotency_key", 1)], unique=True
        )
        await self.db.economic_receipts.create_index("receipt_id", unique=True)
        await self.db.economic_receipts.create_index([("organization_id", 1), ("issued_at", -1)])
        await self.db.economic_external_events.create_index(
            [("source", 1), ("external_id", 1)], unique=True
        )
        await self.db.economic_surfaces.create_index("surface_id", unique=True)

    async def create_action(self, action: dict[str, Any]) -> dict[str, Any]:
        try:
            await self.db.economic_actions.insert_one(copy.deepcopy(action))
            return action
        except Exception as exc:
            if getattr(exc, "code", None) != 11000:
                raise
            existing = await self.db.economic_actions.find_one(
                {"organization_id": action["organization_id"], "idempotency_key": action["idempotency_key"]},
                {"_id": 0},
            )
            if not existing:
                raise
            return existing

    async def get_action(self, action_id: str) -> Optional[dict[str, Any]]:
        return await self.db.economic_actions.find_one({"action_id": action_id}, {"_id": 0})

    async def save_action(self, action: dict[str, Any]) -> None:
        await self.db.economic_actions.replace_one({"action_id": action["action_id"]}, action, upsert=False)

    async def save_receipt(self, receipt: dict[str, Any]) -> None:
        await self.db.economic_receipts.update_one(
            {"receipt_id": receipt["receipt_id"]}, {"$setOnInsert": receipt}, upsert=True
        )

    async def get_receipt(self, receipt_id: str) -> Optional[dict[str, Any]]:
        return await self.db.economic_receipts.find_one({"receipt_id": receipt_id}, {"_id": 0})

    async def latest_receipt(self, organization_id: str) -> Optional[dict[str, Any]]:
        return await self.db.economic_receipts.find_one(
            {"organization_id": organization_id}, {"_id": 0}, sort=[("issued_at", -1)]
        )

    async def list_receipts(self, organization_id: str, limit: int = 1000) -> list[dict[str, Any]]:
        return await self.db.economic_receipts.find(
            {"organization_id": organization_id}, {"_id": 0}
        ).sort("issued_at", -1).limit(limit).to_list(limit)

    async def claim_external_event(self, source: str, external_id: str, action_id: str) -> Optional[str]:
        try:
            await self.db.economic_external_events.insert_one(
                {"source": source, "external_id": external_id, "action_id": action_id}
            )
            return None
        except Exception as exc:
            if getattr(exc, "code", None) != 11000:
                raise
            row = await self.db.economic_external_events.find_one(
                {"source": source, "external_id": external_id}, {"_id": 0, "action_id": 1}
            )
            return row["action_id"] if row else action_id

    async def upsert_surface(self, surface: dict[str, Any]) -> None:
        await self.db.economic_surfaces.update_one(
            {"surface_id": surface["surface_id"]}, {"$set": surface}, upsert=True
        )

    async def list_surfaces(self) -> list[dict[str, Any]]:
        return await self.db.economic_surfaces.find({}, {"_id": 0}).to_list(1000)
