"""Signal source definitions for Trend Intelligence.

Each source defines how to collect signals, what metadata to extract,
and how to score relevance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Signal:
    id: str
    source: str
    title: str
    url: str
    snippet: str
    published_at: str
    collected_at: float
    relevance_score: float = 0.0
    sentiment: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Source:
    name: str
    description: str
    enabled: bool = True
    weight: float = 1.0
    max_signals: int = 50
    ttl_hours: int = 24  # How often to re-collect


SOURCES: Dict[str, Source] = {
    "reddit": Source(
        name="reddit",
        description="Reddit posts and comments — r/machinelearning, r/artificial, r/startups, etc.",
        weight=1.0,
        max_signals=50,
    ),
    "hackernews": Source(
        name="hackernews",
        description="Hacker News front page and /newest",
        weight=1.2,
        max_signals=30,
    ),
    "github": Source(
        name="github",
        description="GitHub trending repos, notable releases",
        weight=1.5,
        max_signals=30,
    ),
    "x_twitter": Source(
        name="x_twitter",
        description="X/Twitter posts from key accounts and topics",
        weight=1.0,
        max_signals=50,
    ),
    "youtube": Source(
        name="youtube",
        description="YouTube videos from tech/creator channels",
        weight=0.8,
        max_signals=20,
    ),
    "news": Source(
        name="news",
        description="Tech news — TechCrunch, The Verge, Ars Technica, etc.",
        weight=1.2,
        max_signals=30,
    ),
    "papers": Source(
        name="papers",
        description="arXiv and academic papers",
        weight=1.3,
        max_signals=20,
    ),
    "polymarket": Source(
        name="polymarket",
        description="Prediction market trends",
        weight=0.7,
        max_signals=10,
    ),
    "producthunt": Source(
        name="producthunt",
        description="Product Hunt launches and upvotes",
        weight=0.8,
        max_signals=20,
    ),
    "yc_launches": Source(
        name="yc_launches",
        description="YC company launches and updates",
        weight=1.0,
        max_signals=15,
    ),
}


def source_config(name: str) -> Optional[Source]:
    return SOURCES.get(name)


def enabled_sources() -> Dict[str, Source]:
    return {k: v for k, v in SOURCES.items() if v.enabled}


def default_topics() -> List[str]:
    return [
        "AI / ML",
        "creator economy",
        "music technology",
        "audio AI",
        "startups",
        "venture capital",
        "open source",
        "developer tools",
        "content creation",
        "competitive intelligence",
    ]
