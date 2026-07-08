"""
Nemotron Timing Engine — Grid Alignment & Temporal Physics.

Calculates beat grids, downbeat positions, and swing vectors.
Provides the temporal foundation for the Prosody Engine and Combinator.
All operations at 48kHz with sub-millisecond precision.
"""

import math
from typing import Dict, Any, List, Optional


class BeatGrid:
    """A rigid BPM grid with configurable swing vectors."""

    def __init__(self, bpm: float, beats_per_bar: int = 4,
                 subdivisions: int = 16, swing: float = 0.0):
        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.subdivisions = subdivisions
        self.swing = swing
        self.ms_per_beat = 60000.0 / bpm
        self.ms_per_sub = self.ms_per_beat / (subdivisions / beats_per_bar)
        self._grid: List[Dict[str, Any]] = []

    @property
    def grid(self) -> List[Dict[str, Any]]:
        return self._grid

    def build(self, bars: int = 4) -> List[Dict[str, Any]]:
        """Generate the beat grid for N bars."""
        self._grid = []
        for bar_idx in range(bars):
            for step in range(self.subdivisions):
                beat_idx = step % 4
                is_downbeat = step == 0
                is_on_beat = step % 4 == 0

                raw_time_ms = (
                    bar_idx * self.beats_per_bar * self.ms_per_beat
                    + step * (self.ms_per_sub)
                )

                if beat_idx == 2:
                    raw_time_ms += self.ms_per_sub * self.swing
                elif beat_idx == 4:
                    raw_time_ms -= self.ms_per_sub * self.swing * 0.5

                self._grid.append({
                    "bar": bar_idx + 1,
                    "step": step,
                    "beat": (step % 4) + 1,
                    "is_downbeat": is_downbeat,
                    "is_on_beat": is_on_beat,
                    "time_ms": round(raw_time_ms, 4),
                    "sample_48khz": int(raw_time_ms * 48.0),
                })
        return self._grid


class TimingEngine:
    """Nemotron's temporal physics — grid alignment, transient detection, vocal snapping."""

    @classmethod
    def build_grid(cls, bpm: float, bars: int = 4,
                   subdivisions: int = 16, swing: float = 0.0) -> BeatGrid:
        """Create a beat grid at the given BPM."""
        grid = BeatGrid(bpm, subdivisions=subdivisions, swing=swing)
        grid.build(bars)
        return grid

    @classmethod
    def snap_to_grid(cls, time_ms: float, grid: BeatGrid) -> Dict[str, Any]:
        """Snap a transient to the nearest grid position."""
        if not grid.grid:
            return {"snapped_time_ms": time_ms, "offset_ms": 0.0}

        nearest = min(grid.grid, key=lambda g: abs(g["time_ms"] - time_ms))
        offset = time_ms - nearest["time_ms"]

        return {
            "original_time_ms": time_ms,
            "snapped_time_ms": nearest["time_ms"],
            "offset_ms": round(offset, 4),
            "bar": nearest["bar"],
            "step": nearest["step"],
            "is_downbeat": nearest["is_downbeat"],
        }

    @classmethod
    def calculate_late_pocket(cls, bpm: float, drag_ms: float = 15.0) -> Dict[str, Any]:
        """Calculate late-pocket timing offsets for human groove."""
        ms_per_16th = 60000.0 / bpm / 4.0

        return {
            "bpm": bpm,
            "ms_per_16th": round(ms_per_16th, 2),
            "snare_drag_ms": drag_ms,
            "snare_drag_percent": round((drag_ms / ms_per_16th) * 100, 1),
            "hihat_swing_ms": round(drag_ms * 0.33, 2),
            "kick_placement": "on_grid",
            "feel": f"Snares drag {drag_ms}ms behind the grid for late-pocket swing",
        }

    @classmethod
    def micro_timing_correction(cls, timeline: List[Dict[str, Any]],
                                 bpm: float) -> List[Dict[str, Any]]:
        """Apply micro-timing corrections to a prosody timeline."""
        grid = cls.build_grid(bpm)
        corrected = []

        for entry in timeline:
            if "time_ms" in entry:
                snap = cls.snap_to_grid(entry["time_ms"], grid)
                corrected.append({
                    **entry,
                    "original_time_ms": entry["time_ms"],
                    "time_ms": snap["snapped_time_ms"],
                    "timing_offset_ms": snap["offset_ms"],
                })
            else:
                corrected.append(entry)

        return corrected
