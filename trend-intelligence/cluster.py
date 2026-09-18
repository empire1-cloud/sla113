"""Signal clustering and scoring engine.

Groups raw signals into themes, scores confidence, ranks by relevance.
"""

from __future__ import annotations

import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from sources import Signal


@dataclass
class Cluster:
    id: str
    name: str
    signals: List[Signal] = field(default_factory=list)
    signal_count: int = 0
    source_count: int = 0
    avg_sentiment: Optional[float] = None
    score: float = 0.0
    keywords: List[str] = field(default_factory=list)


class ClusterEngine:
    """Groups signals by keyword overlap, scores clusters by volume and source diversity."""

    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "can", "shall", "to",
        "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where",
        "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "about",
        "up", "it", "its", "this", "that", "these", "those",
        "and", "but", "or", "if", "because", "while", "what",
        "which", "who", "whom",
    }

    def __init__(self, similarity_threshold: float = 0.3):
        self.threshold = similarity_threshold

    def _tokenize(self, text: str) -> Set[str]:
        words = re.findall(r"[a-z][a-z0-9_]{2,}", text.lower())
        return {w for w in words if w not in self.STOP_WORDS and len(w) > 2}

    def _jaccard(self, a: Set[str], b: Set[str]) -> float:
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def cluster(self, signals: List[Signal]) -> List[Cluster]:
        if not signals:
            return []

        tokenized = [(s, self._tokenize(s.title + " " + s.snippet)) for s in signals]

        assignments: Dict[int, int] = {}
        cluster_map: Dict[int, List[int]] = {}

        for i, (_, tokens_a) in enumerate(tokenized):
            best_cluster = -1
            best_score = 0.0
            for cid, members in cluster_map.items():
                for mi in members:
                    _, tokens_b = tokenized[mi]
                    sim = self._jaccard(tokens_a, tokens_b)
                    if sim > best_score:
                        best_score = sim
                        best_cluster = cid
            if best_score >= self.threshold:
                assignments[i] = best_cluster
                cluster_map[best_cluster].append(i)
            else:
                cid = len(cluster_map)
                assignments[i] = cid
                cluster_map[cid] = [i]

        clusters: Dict[int, Cluster] = {}
        for cid, members in cluster_map.items():
            cluster_signals = [signals[i] for i in members]
            sources = Counter(s.source for s in cluster_signals)
            sentiments = [s.sentiment for s in cluster_signals if s.sentiment is not None]

            # Collect keywords from all titles
            all_tokens = Counter()
            for s in cluster_signals:
                all_tokens.update(self._tokenize(s.title))
            keywords = [w for w, _ in all_tokens.most_common(10)]

            # Generate cluster name from top keywords
            name = ", ".join(keywords[:3]) if keywords else f"Cluster {cid + 1}"

            score = (
                len(cluster_signals) * 10
                + len(sources) * 25
                + (sum(sentiments) / len(sentiments) * 10 if sentiments else 0)
            )

            clusters[cid] = Cluster(
                id=f"cluster_{cid}",
                name=name.capitalize(),
                signals=cluster_signals,
                signal_count=len(cluster_signals),
                source_count=len(sources),
                avg_sentiment=sum(sentiments) / len(sentiments) if sentiments else None,
                score=round(score, 2),
                keywords=keywords,
            )

        return sorted(clusters.values(), key=lambda c: c.score, reverse=True)

    def score_clusters(self, clusters: List[Cluster]) -> List[Cluster]:
        for c in clusters:
            # Base score from signal volume
            volume_score = min(c.signal_count * 10, 50)
            # Source diversity bonus
            diversity = min(c.source_count * 15, 30)
            # Sentiment boost
            sentiment_boost = (
                (c.avg_sentiment or 0) * 10 if c.avg_sentiment else 0
            )
            c.score = round(volume_score + diversity + sentiment_boost, 2)
        return sorted(clusters, key=lambda c: c.score, reverse=True)


def format_brief(
    clusters: List[Cluster],
    total_signals: int,
    source_counts: Dict[str, int],
) -> str:
    """Generate a markdown brief from clustered signals."""
    lines = [
        "# Trend Intelligence Brief",
        "",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Signals collected:** {total_signals}",
        f"**Sources:** {', '.join(f'{k}={v}' for k, v in sorted(source_counts.items()))}",
        f"**Clusters found:** {len(clusters)}",
        "",
        "---",
        "",
    ]

    for i, cluster in enumerate(clusters, 1):
        lines.append(f"## {i}. {cluster.name}")
        lines.append("")
        lines.append(f"- Score: {cluster.score}")
        lines.append(f"- Signals: {cluster.signal_count} from {cluster.source_count} sources")
        if cluster.avg_sentiment is not None:
            sentiment_label = "positive" if cluster.avg_sentiment > 0.3 else "negative" if cluster.avg_sentiment < -0.3 else "neutral"
            lines.append(f"- Sentiment: {sentiment_label} ({cluster.avg_sentiment:.2f})")
        lines.append(f"- Keywords: {', '.join(cluster.keywords[:5])}")
        lines.append("")
        lines.append("### Signals")
        for sig in cluster.signals[:10]:
            lines.append(f"- [{sig.title}]({sig.url}) — *{sig.source}*")
        if len(cluster.signals) > 10:
            lines.append(f"  *... and {len(cluster.signals) - 10} more*")
        lines.append("")

    return "\n".join(lines)
