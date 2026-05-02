"""
Lyrica Micro-Royalty Ledger — VICS Protocol.

Fractional USD routing with atomic MongoDB upserts.
No middlemen. No labels. Direct creator-to-wallet.

Territory multipliers:
  US=1.0, EU=0.85, LATAM=0.6, APAC=0.7

Base rate: $0.004/stream (industry standard).

Flip It Protocol: Child tracks only minted if fractional micro-royalties
are atomically guaranteed to parent contributors.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

BASE_RATE_USD = 0.004

TERRITORY_MULTIPLIERS = {
    "US": 1.0,
    "EU": 0.85,
    "LATAM": 0.6,
    "APAC": 0.7,
    "GLOBAL": 0.75,
}


def calculate_micro_royalty(
    track_id: str,
    streams: int,
    territory: str = "US",
    splits: Optional[dict] = None,
) -> dict:
    """
    Calculate fractional USD distribution across contributors.
    Returns ledger entries ready for MongoDB commit.
    """
    t_mult = TERRITORY_MULTIPLIERS.get(territory, 0.5)
    gross_royalty = streams * BASE_RATE_USD * t_mult

    if not splits:
        splits = {"creator": 1.0}

    total_fraction = sum(splits.values())
    if abs(total_fraction - 1.0) > 0.001:
        raise ValueError(f"Split fractions must sum to 1.0, got {total_fraction}")

    ledger_entries = []
    for contributor_id, fraction in splits.items():
        net_payout = gross_royalty * fraction
        ledger_entries.append({
            "entry_id": str(uuid.uuid4()),
            "track_id": track_id,
            "contributor_id": contributor_id,
            "fraction": fraction,
            "accumulated_usd": round(net_payout, 6),
            "territory": territory,
            "territory_multiplier": t_mult,
            "streams": streams,
            "base_rate": BASE_RATE_USD,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return {
        "track_id": track_id,
        "gross_royalty_usd": round(gross_royalty, 6),
        "territory": territory,
        "territory_multiplier": t_mult,
        "streams": streams,
        "contributors": len(splits),
        "ledger_entries": ledger_entries,
    }


async def commit_to_mongodb(ledger_result: dict, db) -> dict:
    """
    Atomic upsert of royalty entries to MongoDB.
    Uses $inc for accumulated_usd to support incremental stream updates.
    """
    committed = 0
    for entry in ledger_result["ledger_entries"]:
        await db.royalty_ledger.update_one(
            {
                "contributor_id": entry["contributor_id"],
                "track_id": entry["track_id"],
            },
            {
                "$inc": {"accumulated_usd": entry["accumulated_usd"]},
                "$set": {
                    "fraction": entry["fraction"],
                    "territory": entry["territory"],
                    "status": entry["status"],
                    "last_stream_logged": datetime.now(timezone.utc).isoformat(),
                },
                "$setOnInsert": {
                    "entry_id": entry["entry_id"],
                    "created_at": entry["created_at"],
                },
            },
            upsert=True,
        )
        committed += 1

    logger.info(
        "[VICS] Ledger committed: $%.2f across %d creators for %s",
        ledger_result["gross_royalty_usd"],
        committed,
        ledger_result["track_id"],
    )

    return {
        "committed": committed,
        "track_id": ledger_result["track_id"],
        "gross_usd": ledger_result["gross_royalty_usd"],
    }


def validate_flip_it(parent_dna_tag: str, child_splits: dict, parent_splits: dict) -> dict:
    """
    Flip It Protocol validation.
    Child track can only be minted if parent contributors get their cut.
    """
    for parent_id, parent_fraction in parent_splits.items():
        if parent_id not in child_splits:
            return {
                "valid": False,
                "reason": f"Parent contributor '{parent_id}' not found in child splits",
                "required_minimum": parent_fraction * 0.15,
            }

        child_fraction = child_splits[parent_id]
        minimum_required = parent_fraction * 0.15
        if child_fraction < minimum_required:
            return {
                "valid": False,
                "reason": f"Contributor '{parent_id}' gets {child_fraction:.4f} but minimum is {minimum_required:.4f} (15% of parent share)",
                "required_minimum": minimum_required,
            }

    return {
        "valid": True,
        "parent_dna_tag": parent_dna_tag,
        "message": "Flip It protocol satisfied. Child track cleared for minting.",
    }
