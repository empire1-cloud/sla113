# royalty_ledger.py
# Empire-1 | Lyrica3 | Soulfire Engine
# Role: Micro-royalty ledger + DNA tag steward (VICS-compatible)

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
import uuid

@dataclass
class LedgerEvent:
    event_id: str
    track_id: str
    creator_id: str
    split_map: Dict[str, float]
    dna_tag: str
    event_type: str  # e.g. "BLUEPRINT_COMMIT", "RENDER_COMMIT"
    timestamp: str
    metadata: Dict[str, Any]

class RoyaltyLedger:
    def __init__(self):
        # In-memory for now; replace with DB or file-backed store later
        self._events: List[LedgerEvent] = []

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    def _new_event_id(self) -> str:
        return str(uuid.uuid4())

    def commit_event(
        self,
        track_id: str,
        creator_id: str,
        split_map: Dict[str, float],
        dna_tag: str,
        event_type: str,
        metadata: Dict[str, Any] | None = None,
    ) -> LedgerEvent:
        if metadata is None:
            metadata = {}

        event = LedgerEvent(
            event_id=self._new_event_id(),
            track_id=track_id,
            creator_id=creator_id,
            split_map=split_map,
            dna_tag=dna_tag,
            event_type=event_type,
            timestamp=self._now(),
            metadata=metadata,
        )
        self._events.append(event)
        return event

    def list_events(self, track_id: str | None = None) -> List[Dict[str, Any]]:
        if track_id is None:
            return [asdict(e) for e in self._events]
        return [asdict(e) for e in self._events if e.track_id == track_id]

    def latest_for_track(self, track_id: str) -> Dict[str, Any] | None:
        events = [e for e in self._events if e.track_id == track_id]
        if not events:
            return None
        return asdict(sorted(events, key=lambda e: e.timestamp)[-1])