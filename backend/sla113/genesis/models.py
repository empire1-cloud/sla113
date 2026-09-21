"""Typed contracts for Genesis Engine generation jobs."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

# Default fish-shooter model. Theoretical RTP of these two tables together:
# 0.55*0.25 + 0.30*0.75 + 0.10*2.0 + 0.05*8.05 = 0.965 (96.5%).
DEFAULT_PAYTABLE: Dict[str, float] = {"small": 0.25, "medium": 0.75, "large": 2.0, "boss": 8.05}
DEFAULT_WEIGHTS: Dict[str, float] = {"small": 0.55, "medium": 0.30, "large": 0.10, "boss": 0.05}


class GameSpec(BaseModel):
    name: str = Field(default="Genesis Game", min_length=1, max_length=80)
    game_type: str = "fish_shooter"
    theme: str = "Southern Aztec arcade"
    target_platform: str = "web"
    width: int = Field(default=1280, ge=320, le=4096)
    height: int = Field(default=720, ge=240, le=4096)
    fps: int = Field(default=60, ge=30, le=120)
    fish_count: int = Field(default=8, ge=1, le=100)
    # Payout multiplier per target, in units of one wager.
    paytable: Dict[str, float] = Field(default_factory=lambda: dict(DEFAULT_PAYTABLE))
    # Relative frequency of each target. Normalized to probabilities. When
    # omitted, the canonical fish weights are used for keys that have one.
    hit_weights: Optional[Dict[str, float]] = None
    target_rtp: float = Field(default=0.965, gt=0.0, lt=1.0)
    shots_per_round: int = Field(default=10000, ge=100, le=2_000_000)
    seed: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_tables(self) -> "GameSpec":
        if not self.paytable:
            raise ValueError("paytable must contain at least one target")
        if len(self.paytable) > 32:
            raise ValueError("paytable supports at most 32 targets")
        for key, value in self.paytable.items():
            if value < 0:
                raise ValueError(f"paytable[{key!r}] must be >= 0")
        if self.hit_weights is not None:
            missing = set(self.paytable) - set(self.hit_weights)
            extra = set(self.hit_weights) - set(self.paytable)
            if missing or extra:
                raise ValueError(
                    f"hit_weights keys must match paytable keys (missing={sorted(missing)}, extra={sorted(extra)})"
                )
            if any(w < 0 for w in self.hit_weights.values()) or sum(self.hit_weights.values()) <= 0:
                raise ValueError("hit_weights must be non-negative and sum to more than 0")
        else:
            unknown = set(self.paytable) - set(DEFAULT_WEIGHTS)
            if unknown:
                raise ValueError(
                    f"hit_weights is required for targets without a canonical weight: {sorted(unknown)}"
                )
        return self


class GenerateRequest(BaseModel):
    spec: GameSpec = Field(default_factory=GameSpec)
    include_audio: bool = True
    include_vision: bool = True
    include_build: bool = True


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    stages_completed: List[str]
    manifest: Dict[str, Any]
    verification: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    build: Dict[str, Any]
