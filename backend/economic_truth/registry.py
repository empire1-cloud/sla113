"""Registry that makes economic coverage explicit and measurable."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class EconomicSurface:
    name: str
    action_type: str
    governed: bool
    owner: str


class CoverageRegistry:
    def __init__(self, surfaces: Iterable[EconomicSurface] = ()) -> None:
        self._surfaces = {surface.name: surface for surface in surfaces}

    def register(self, surface: EconomicSurface) -> None:
        self._surfaces[surface.name] = surface

    def report(self) -> dict:
        surfaces = list(self._surfaces.values())
        governed = [item for item in surfaces if item.governed]
        uncovered = [item.name for item in surfaces if not item.governed]
        return {
            "total_surfaces": len(surfaces),
            "governed_surfaces": len(governed),
            "coverage_percent": 100.0 if not surfaces else round(100 * len(governed) / len(surfaces), 2),
            "uncovered_surfaces": uncovered,
            "claim_allowed": bool(surfaces) and not uncovered,
        }

    def assert_complete(self) -> None:
        report = self.report()
        if not report["claim_allowed"]:
            raise RuntimeError(f"Economic truth coverage incomplete: {report['uncovered_surfaces']}")
