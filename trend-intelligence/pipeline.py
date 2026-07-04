"""Daily trend intelligence pipeline.

Orchestrates signal collection → clustering → scoring → storage → reporting.
Runs on a configurable schedule (default: daily).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from bridge import Last30DaysBridge
from cluster import ClusterEngine, format_brief
from sources import Signal, default_topics, enabled_sources


@dataclass
class PipelineRun:
    id: str
    started_at: float
    ended_at: float
    topics_researched: int = 0
    signals_collected: int = 0
    clusters_found: int = 0
    brief_path: Optional[str] = None
    status: str = "running"
    error: Optional[str] = None


class TrendPipeline:
    def __init__(
        self,
        data_dir: str | Path,
        topics: Optional[List[str]] = None,
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bridge = Last30DaysBridge()
        self.cluster_engine = ClusterEngine()
        self.topics = topics or default_topics()

    def run(self, days: int = 7, max_signals_per_topic: int = 30) -> PipelineRun:
        run_id = f"trend_{int(time.time())}"
        run = PipelineRun(id=run_id, started_at=time.time())

        try:
            all_signals: List[Signal] = []
            source_counts: Dict[str, int] = {}

            for topic in self.topics:
                result = self.bridge.research(
                    topic=topic,
                    days=days,
                    max_signals=max_signals_per_topic,
                )
                if result.get("success"):
                    signals = result.get("signals", [])
                    all_signals.extend(signals)
                    for sig in signals:
                        source_counts[sig.source] = source_counts.get(sig.source, 0) + 1

            run.signals_collected = len(all_signals)
            run.topics_researched = len(self.topics)

            # Cluster
            clusters = self.cluster_engine.cluster(all_signals)
            clusters = self.cluster_engine.score_clusters(clusters)
            run.clusters_found = len(clusters)

            # Generate brief
            brief = format_brief(clusters, len(all_signals), source_counts)
            brief_path = self.data_dir / f"{run_id}-brief.md"
            brief_path.write_text(brief)
            run.brief_path = str(brief_path)

            # Also save as JSON
            json_path = self.data_dir / f"{run_id}-signals.json"
            with json_path.open("w") as f:
                json.dump({
                    "run_id": run_id,
                    "started_at": run.started_at,
                    "signal_count": len(all_signals),
                    "cluster_count": len(clusters),
                    "source_counts": source_counts,
                    "clusters": [
                        {
                            "name": c.name,
                            "score": c.score,
                            "signal_count": c.signal_count,
                            "source_count": c.source_count,
                            "keywords": c.keywords,
                        }
                        for c in clusters
                    ],
                }, f, indent=2)

            # Update latest symlink
            latest = self.data_dir / "latest-brief.md"
            if latest.exists():
                latest.unlink()
            latest.symlink_to(brief_path.name)

            run.status = "completed"
            run.ended_at = time.time()

        except Exception as e:
            run.status = "failed"
            run.error = str(e)
            run.ended_at = time.time()

        return run

    def latest_brief(self) -> Optional[str]:
        latest = self.data_dir / "latest-brief.md"
        if latest.exists():
            return latest.read_text()
        return None

    def run_history(self, limit: int = 10) -> List[Dict]:
        """List recent runs by scanning brief files."""
        runs = []
        for f in sorted(self.data_dir.glob("trend_*-brief.md"), reverse=True)[:limit]:
            runs.append({
                "file": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            })
        return runs
