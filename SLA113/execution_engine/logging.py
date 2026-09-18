"""Structured logging and tracing for the Execution Engine and Runtime."""

from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional

_trace_id: ContextVar[str] = ContextVar("trace_id", default="")
_span_id: ContextVar[str] = ContextVar("span_id", default="")

_logger = logging.getLogger("sla113.execution")


def configure(level: int = logging.INFO, format: Optional[str] = None):
    fmt = format or "%(asctime)s [%(levelname)s] %(message)s"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    _logger.addHandler(handler)
    _logger.setLevel(level)
    _logger.propagate = False


def new_trace() -> str:
    tid = uuid.uuid4().hex[:16]
    _trace_id.set(tid)
    return tid


def new_span() -> str:
    sid = uuid.uuid4().hex[:12]
    _span_id.set(sid)
    return sid


def get_trace_id() -> str:
    return _trace_id.get()


def get_span_id() -> str:
    return _span_id.get()


def _event(kind: str, data: Dict[str, Any]):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "trace_id": get_trace_id(),
        "span_id": get_span_id(),
        **data,
    }
    _logger.info(json.dumps(entry, default=str))


def workflow_start(workflow_id: str, inputs: Dict[str, Any]):
    tid = new_trace()
    _event("workflow.start", {"workflow_id": workflow_id, "trace_id": tid})


def workflow_end(workflow_id: str, success: bool, duration_ms: float, error: Optional[str] = None):
    _event("workflow.end", {
        "workflow_id": workflow_id, "success": success,
        "duration_ms": round(duration_ms, 1), "error": error,
    })


def node_start(node_id: str, capability: str, service: str):
    sid = new_span()
    _event("node.start", {"node_id": node_id, "capability": capability, "service": service})


def node_end(node_id: str, success: bool, duration_ms: float, error: Optional[str] = None):
    _event("node.end", {
        "node_id": node_id, "success": success,
        "duration_ms": round(duration_ms, 1), "error": error,
    })


def provider_select(capability: str, provider_id: str, preference: Optional[str] = None):
    _event("provider.select", {
        "capability": capability, "provider_id": provider_id, "preference": preference,
    })


def cache_hit(provider_id: str, capability: str):
    _event("cache.hit", {"provider_id": provider_id, "capability": capability})


def cache_miss(provider_id: str, capability: str):
    _event("cache.miss", {"provider_id": provider_id, "capability": capability})


def lifecycle_transition(provider_id: str, from_state: str, to_state: str):
    _event("lifecycle.transition", {
        "provider_id": provider_id, "from": from_state, "to": to_state,
    })


def request(capability: str, provider_id: str, status: str, latency_ms: float, error: Optional[str] = None):
    _event("request", {
        "capability": capability, "provider_id": provider_id,
        "status": status, "latency_ms": round(latency_ms, 1), "error": error,
    })


class Timer:
    """Context manager for timing blocks."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.duration_ms = (time.perf_counter() - self.start) * 1000

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self.start) * 1000
