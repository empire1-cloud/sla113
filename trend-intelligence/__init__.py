"""Trend Intelligence — public API"""

from sources import Signal, Source, SOURCES, default_topics
from cluster import ClusterEngine, Cluster, format_brief
from pipeline import TrendPipeline, PipelineRun
from bridge import Last30DaysBridge
from kg_integration import KGBridge

__all__ = [
    "Signal", "Source", "SOURCES", "default_topics",
    "ClusterEngine", "Cluster", "format_brief",
    "TrendPipeline", "PipelineRun",
    "Last30DaysBridge",
    "KGBridge",
]
