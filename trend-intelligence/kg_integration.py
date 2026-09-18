"""Knowledge Graph integration for Trend Intelligence.

Pushes trend signals, clusters, and competitors into the Knowledge Graph
as entities and relationships.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

from cluster import Cluster
from sources import Signal


class KGBridge:
    """Bridges trend intelligence results into the Knowledge Graph.

    This is a write-only adapter. It expects a Knowledge Graph store
    with create_entity and create_relationship methods.
    """

    def __init__(self, graph_store):
        self.store = graph_store

    def ingest_signals(self, signals: List[Signal], run_id: str) -> int:
        count = 0
        for sig in signals:
            entity_id = f"trend_{sig.id}"
            self.store.create_entity(
                entity_id,
                sig.title[:200],
                "Trend",
                properties={
                    "source": sig.source,
                    "url": sig.url,
                    "snippet": sig.snippet[:500],
                    "published_at": sig.published_at,
                    "relevance": sig.relevance_score,
                    "sentiment": sig.sentiment,
                    "tags": sig.tags,
                    "run_id": run_id,
                },
            )
            count += 1
        return count

    def ingest_clusters(self, clusters: List[Cluster], run_id: str) -> int:
        count = 0
        for cluster in clusters:
            entity_id = f"trend_cluster_{run_id}_{cluster.id}"
            self.store.create_entity(
                entity_id,
                f"Trend: {cluster.name}",
                "Trend",
                properties={
                    "score": cluster.score,
                    "signal_count": cluster.signal_count,
                    "source_count": cluster.source_count,
                    "keywords": cluster.keywords,
                    "avg_sentiment": cluster.avg_sentiment,
                    "run_id": run_id,
                },
            )
            # Link signals to clusters
            for sig in cluster.signals:
                sig_id = f"trend_{sig.id}"
                self.store.create_relationship(
                    entity_id,
                    sig_id,
                    "contains",
                    properties={"weight": sig.relevance_score},
                )
            count += 1
        return count

    def track_competitor(self, name: str, category: str, signals: List[Signal]) -> Optional[str]:
        """Create or update a competitor entity from trend signals mentioning them."""
        entity_id = f"competitor_{name.lower().replace(' ', '_')}"
        existing = self.store.get_entity(entity_id)
        if existing:
            self.store.update_entity(
                entity_id,
                properties={
                    **existing.properties,
                    "category": category,
                    "last_mentioned": time.time(),
                    "mention_count": existing.properties.get("mention_count", 0) + len(signals),
                    "recent_signals": [s.title[:100] for s in signals[:5]],
                },
            )
        else:
            self.store.create_entity(
                entity_id,
                name,
                "Competitor",
                properties={
                    "category": category,
                    "first_seen": time.time(),
                    "mention_count": len(signals),
                },
            )

        for sig in signals:
            sig_id = f"trend_{sig.id}"
            self.store.create_relationship(entity_id, sig_id, "mentioned_in")

        return entity_id
