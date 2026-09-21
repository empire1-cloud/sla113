"""Deterministic game mathematics. No LLM is trusted for numeric truth.

Theoretical RTP is computed exactly from the paytable and hit weights. A
fixed-seed Monte Carlo run is a secondary reproducibility check. Neither is
regulatory certification.

RTP here is per resolved target event (one wager per target hit), not per shot
fired: miss rate is not modelled yet.
"""
from __future__ import annotations

import bisect
import hashlib
import json
import math
import random
from typing import Any, Dict

from .models import DEFAULT_WEIGHTS

TARGET_TOLERANCE = 0.0025  # 0.25 percentage points


def probabilities(spec: Any) -> Dict[str, float]:
    raw = dict(spec.hit_weights) if spec.hit_weights is not None else {k: DEFAULT_WEIGHTS[k] for k in spec.paytable}
    total = sum(raw.values())
    return {k: raw[k] / total for k in spec.paytable}


def verify_math(spec: Any) -> Dict[str, Any]:
    paytable = {k: float(v) for k, v in spec.paytable.items()}
    weights = probabilities(spec)
    theoretical_rtp = sum(weights[k] * paytable[k] for k in paytable)

    seed_material = json.dumps({"paytable": paytable, "weights": weights, "seed": spec.seed}, sort_keys=True)
    seed = spec.seed if spec.seed is not None else int(hashlib.sha256(seed_material.encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)

    keys = list(paytable)
    cumulative, acc = [], 0.0
    for k in keys:
        acc += weights[k]
        cumulative.append(acc)
    cumulative[-1] = 1.0  # guard against float drift

    rounds = int(spec.shots_per_round)
    total = total_sq = 0.0
    hits = {k: 0 for k in keys}
    for _ in range(rounds):
        k = keys[bisect.bisect_left(cumulative, rng.random())]
        p = paytable[k]
        hits[k] += 1
        total += p
        total_sq += p * p
    simulated_rtp = total / rounds
    stddev = math.sqrt(max(0.0, total_sq / rounds - simulated_rtp ** 2))

    tolerance = max(0.01, 4.0 * stddev / math.sqrt(rounds))
    target_delta = abs(theoretical_rtp - float(spec.target_rtp))
    sim_ok = abs(simulated_rtp - theoretical_rtp) <= tolerance
    target_ok = target_delta <= TARGET_TOLERANCE

    return {
        "model": "weighted_target_payout_v2",
        "rtp_basis": "per resolved target event (miss rate not modelled)",
        "theoretical_rtp": round(theoretical_rtp, 8),
        "theoretical_rtp_percent": round(theoretical_rtp * 100, 5),
        "target_rtp": float(spec.target_rtp),
        "target_rtp_percent": round(float(spec.target_rtp) * 100, 5),
        "target_delta": round(target_delta, 8),
        "target_tolerance": TARGET_TOLERANCE,
        "target_matches_model": target_ok,
        "simulation_rounds": rounds,
        "simulation_seed": seed,
        "simulated_rtp": round(simulated_rtp, 8),
        "simulated_rtp_percent": round(simulated_rtp * 100, 5),
        "simulation_stddev": round(stddev, 8),
        "simulation_tolerance": round(tolerance, 8),
        "simulation_within_tolerance": sim_ok,
        "simulation_hits": hits,
        "probabilities": weights,
        "paytable": paytable,
        "verification_status": "verified" if (target_ok and sim_ok) else "review_required",
        "regulatory_certification": False,
        "proof_hash": hashlib.sha256(
            json.dumps({"weights": weights, "paytable": paytable, "rtp": theoretical_rtp}, sort_keys=True).encode()
        ).hexdigest(),
    }
