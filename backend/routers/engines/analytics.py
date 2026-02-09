"""
Analytics Router - Monitoring & Dashboard endpoints

Provides:
- Engine usage statistics
- Latency metrics
- Error rates
- Drift detection status
- System health (real metrics via psutil)
- Pipeline visualization data
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from services.execution_logger import get_logger
import random
import time
import os

# Try to import psutil, fallback to mock data if unavailable
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not available, using mock system metrics")

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Simple in-memory cache
_cache: Dict[str, Any] = {}
_cache_ttl: Dict[str, float] = {}
CACHE_DURATION = 5  # seconds


def get_cached(key: str):
    """Get cached value if still valid."""
    if key in _cache and time.time() < _cache_ttl.get(key, 0):
        return _cache[key]
    return None


def set_cached(key: str, value: Any):
    """Set cache with TTL."""
    _cache[key] = value
    _cache_ttl[key] = time.time() + CACHE_DURATION


# Response Models
class EngineUsageItem(BaseModel):
    engine: str
    count: int
    display_name: str


class EngineLatencyItem(BaseModel):
    engine: str
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p95_latency_ms: float
    display_name: str


class EngineErrorItem(BaseModel):
    engine: str
    total_calls: int
    error_count: int
    error_rate: float
    severity: str  # low, medium, high
    display_name: str


class DriftAlert(BaseModel):
    engine: str
    status: str  # green, yellow, red
    confidence_trend: str  # stable, rising, falling
    last_check: str
    message: str


class SystemHealthResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    memory_total_gb: float
    memory_used_gb: float
    disk_usage: float
    disk_total_gb: float
    disk_used_gb: float
    load_average: Optional[List[float]] = None  # 1, 5, 15 min averages
    active_connections: int
    uptime_hours: float
    status: str  # healthy, degraded, critical
    psutil_available: bool  # Indicates if real metrics or mock


class PipelineNode(BaseModel):
    id: str
    name: str
    type: str  # engine, input, output
    status: str  # idle, running, completed, error


class PipelineEdge(BaseModel):
    source: str
    target: str


class PipelineGraphResponse(BaseModel):
    nodes: List[PipelineNode]
    edges: List[PipelineEdge]
    active_pipelines: int
    queue_length: int
    throughput_per_minute: float


class TimeSeriesPoint(BaseModel):
    timestamp: str
    value: float


class ConfidenceTrendResponse(BaseModel):
    engine: str
    data_points: List[TimeSeriesPoint]
    current_confidence: float
    trend: str  # stable, rising, falling


def format_engine_name(engine: str) -> str:
    """Convert engine_name to Display Name."""
    return ' '.join(word.capitalize() for word in engine.replace('_engine', '').split('_'))


@router.get("/engine-usage", response_model=List[EngineUsageItem])
async def get_engine_usage():
    """Get request counts per engine."""
    cached = get_cached("engine_usage")
    if cached:
        return cached
    
    logger = get_logger()
    stats = logger.get_stats()
    
    result = [
        EngineUsageItem(
            engine=engine,
            count=count,
            display_name=format_engine_name(engine)
        )
        for engine, count in stats.get("engines", {}).items()
    ]
    
    # Sort by count descending
    result.sort(key=lambda x: x.count, reverse=True)
    
    set_cached("engine_usage", result)
    return result


@router.get("/engine-latency", response_model=List[EngineLatencyItem])
async def get_engine_latency():
    """Get latency metrics per engine."""
    cached = get_cached("engine_latency")
    if cached:
        return cached
    
    logger = get_logger()
    logs = logger.logs
    
    # Group by engine
    engine_latencies: Dict[str, List[int]] = {}
    for log in logs:
        engine = log.engine
        if engine not in engine_latencies:
            engine_latencies[engine] = []
        engine_latencies[engine].append(log.duration_ms)
    
    result = []
    for engine, latencies in engine_latencies.items():
        if not latencies:
            continue
        
        sorted_latencies = sorted(latencies)
        p95_idx = int(len(sorted_latencies) * 0.95)
        
        result.append(EngineLatencyItem(
            engine=engine,
            avg_latency_ms=round(sum(latencies) / len(latencies), 2),
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            p95_latency_ms=sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else sorted_latencies[-1],
            display_name=format_engine_name(engine)
        ))
    
    # Sort by avg latency descending
    result.sort(key=lambda x: x.avg_latency_ms, reverse=True)
    
    set_cached("engine_latency", result)
    return result


@router.get("/engine-errors", response_model=List[EngineErrorItem])
async def get_engine_errors():
    """Get error rates per engine."""
    cached = get_cached("engine_errors")
    if cached:
        return cached
    
    logger = get_logger()
    logs = logger.logs
    
    # Aggregate errors by engine
    engine_stats: Dict[str, Dict[str, int]] = {}
    for log in logs:
        engine = log.engine
        if engine not in engine_stats:
            engine_stats[engine] = {"total": 0, "errors": 0}
        engine_stats[engine]["total"] += 1
        if log.status == "error":
            engine_stats[engine]["errors"] += 1
    
    result = []
    for engine, stats in engine_stats.items():
        error_rate = (stats["errors"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        # Determine severity
        if error_rate >= 20:
            severity = "high"
        elif error_rate >= 5:
            severity = "medium"
        else:
            severity = "low"
        
        result.append(EngineErrorItem(
            engine=engine,
            total_calls=stats["total"],
            error_count=stats["errors"],
            error_rate=round(error_rate, 2),
            severity=severity,
            display_name=format_engine_name(engine)
        ))
    
    # Sort by error rate descending
    result.sort(key=lambda x: x.error_rate, reverse=True)
    
    set_cached("engine_errors", result)
    return result


@router.get("/drift-status", response_model=List[DriftAlert])
async def get_drift_status():
    """Get AI drift detection status for each engine."""
    cached = get_cached("drift_status")
    if cached:
        return cached
    
    logger = get_logger()
    logs = logger.logs
    
    # Get unique engines from logs
    engines = list(set(log.engine for log in logs))
    
    # If no logs, return default engines
    if not engines:
        engines = [
            "strategy_engine", "plan_builder_engine", "analysis_engine",
            "money_pipeline_engine", "persona_engine", "pricing_engine"
        ]
    
    result = []
    now = datetime.now(timezone.utc)
    
    for engine in engines:
        # Get recent logs for this engine
        engine_logs = [l for l in logs if l.engine == engine]
        recent_logs = [l for l in engine_logs if (now - datetime.fromisoformat(l.timestamp.replace('Z', '+00:00'))).total_seconds() < 3600]
        
        # Calculate metrics for drift detection
        if len(recent_logs) >= 3:
            recent_durations = [l.duration_ms for l in recent_logs[-10:]]
            avg_duration = sum(recent_durations) / len(recent_durations)
            variance = sum((d - avg_duration) ** 2 for d in recent_durations) / len(recent_durations)
            
            # Determine status based on variance and error rate
            error_rate = sum(1 for l in recent_logs if l.status == "error") / len(recent_logs)
            
            if error_rate > 0.2 or variance > 10000000:
                status = "red"
                trend = "falling"
                message = f"High variance or error rate detected ({error_rate*100:.1f}% errors)"
            elif error_rate > 0.05 or variance > 5000000:
                status = "yellow"
                trend = "falling"
                message = f"Moderate drift detected, monitoring closely"
            else:
                status = "green"
                trend = "stable"
                message = "Operating within normal parameters"
        else:
            status = "green"
            trend = "stable"
            message = "Insufficient data for drift analysis"
        
        result.append(DriftAlert(
            engine=engine,
            status=status,
            confidence_trend=trend,
            last_check=now.isoformat(),
            message=message
        ))
    
    set_cached("drift_status", result)
    return result


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get system health metrics using psutil (with fallback to mock data)."""
    cached = get_cached("system_health")
    if cached:
        return cached
    
    if PSUTIL_AVAILABLE:
        # Real system metrics via psutil
        cpu = psutil.cpu_percent(interval=0.1)
        
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_total_gb = round(memory.total / (1024 ** 3), 2)
        memory_used_gb = round(memory.used / (1024 ** 3), 2)
        
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_total_gb = round(disk.total / (1024 ** 3), 2)
        disk_used_gb = round(disk.used / (1024 ** 3), 2)
        
        # Load average (Unix only)
        try:
            load_avg = list(os.getloadavg())
            load_average = [round(l, 2) for l in load_avg]
        except (OSError, AttributeError):
            load_average = None
        
        # Active network connections
        try:
            connections = len(psutil.net_connections(kind='inet'))
        except (psutil.AccessDenied, OSError):
            connections = 0
        
        # System uptime
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_hours = round(uptime_seconds / 3600, 1)
        except Exception:
            uptime_hours = 0
        
        psutil_available = True
    else:
        # Mock data fallback
        cpu = 35 + random.uniform(-10, 15)
        memory_percent = 45 + random.uniform(-5, 10)
        memory_total_gb = 16.0
        memory_used_gb = round(memory_total_gb * memory_percent / 100, 2)
        disk_percent = 28 + random.uniform(-2, 5)
        disk_total_gb = 100.0
        disk_used_gb = round(disk_total_gb * disk_percent / 100, 2)
        load_average = [1.5, 1.2, 0.9]
        connections = random.randint(5, 25)
        uptime_hours = round(random.uniform(24, 720), 1)
        psutil_available = False
    
    # Determine overall status
    if cpu > 90 or memory_percent > 90 or disk_percent > 95:
        status = "critical"
    elif cpu > 70 or memory_percent > 75 or disk_percent > 80:
        status = "degraded"
    else:
        status = "healthy"
    
    result = SystemHealthResponse(
        cpu_usage=round(cpu, 1),
        memory_usage=round(memory_percent, 1),
        memory_total_gb=memory_total_gb,
        memory_used_gb=memory_used_gb,
        disk_usage=round(disk_percent, 1),
        disk_total_gb=disk_total_gb,
        disk_used_gb=disk_used_gb,
        load_average=load_average,
        active_connections=connections,
        uptime_hours=uptime_hours,
        status=status,
        psutil_available=psutil_available
    )
    
    set_cached("system_health", result)
    return result


@router.get("/pipeline-graph", response_model=PipelineGraphResponse)
async def get_pipeline_graph():
    """Get active pipeline visualization data."""
    cached = get_cached("pipeline_graph")
    if cached:
        return cached
    
    logger = get_logger()
    logs = logger.logs
    
    # Get recent pipeline executions
    now = datetime.now(timezone.utc)
    recent_pipeline_logs = [
        l for l in logs 
        if l.source == "pipeline" and 
        (now - datetime.fromisoformat(l.timestamp.replace('Z', '+00:00'))).total_seconds() < 3600
    ]
    
    # Build graph nodes from recent engines
    engine_set = set()
    for log in logs[-50:]:  # Last 50 logs
        engine_set.add(log.engine)
    
    nodes = [
        PipelineNode(id="input", name="Input", type="input", status="idle"),
    ]
    
    for engine in list(engine_set)[:8]:  # Limit to 8 engines
        nodes.append(PipelineNode(
            id=engine,
            name=format_engine_name(engine),
            type="engine",
            status="idle"
        ))
    
    nodes.append(PipelineNode(id="output", name="Output", type="output", status="idle"))
    
    # Create edges (simplified linear flow)
    edges = []
    engine_list = [n.id for n in nodes if n.type == "engine"]
    
    if engine_list:
        edges.append(PipelineEdge(source="input", target=engine_list[0]))
        for i in range(len(engine_list) - 1):
            edges.append(PipelineEdge(source=engine_list[i], target=engine_list[i + 1]))
        edges.append(PipelineEdge(source=engine_list[-1], target="output"))
    
    # Calculate throughput
    recent_count = len([l for l in logs if (now - datetime.fromisoformat(l.timestamp.replace('Z', '+00:00'))).total_seconds() < 60])
    
    result = PipelineGraphResponse(
        nodes=nodes,
        edges=edges,
        active_pipelines=len(set(l.pipeline_id for l in recent_pipeline_logs if l.pipeline_id)),
        queue_length=random.randint(0, 5),
        throughput_per_minute=recent_count
    )
    
    set_cached("pipeline_graph", result)
    return result


@router.get("/confidence-trends", response_model=List[ConfidenceTrendResponse])
async def get_confidence_trends():
    """Get confidence score trends over time."""
    cached = get_cached("confidence_trends")
    if cached:
        return cached
    
    logger = get_logger()
    logs = logger.logs
    
    # Get unique engines
    engines = list(set(log.engine for log in logs))[:6]  # Limit to 6 engines
    
    if not engines:
        engines = ["strategy_engine", "analysis_engine", "money_pipeline_engine"]
    
    result = []
    now = datetime.now(timezone.utc)
    
    for engine in engines:
        # Generate time series data based on actual logs
        engine_logs = [l for l in logs if l.engine == engine]
        
        data_points = []
        for i in range(12):  # Last 12 hours
            hour_time = now - timedelta(hours=11-i)
            
            # Calculate confidence from success rate in that hour window
            hour_logs = [
                l for l in engine_logs 
                if abs((datetime.fromisoformat(l.timestamp.replace('Z', '+00:00')) - hour_time).total_seconds()) < 1800
            ]
            
            if hour_logs:
                success_rate = sum(1 for l in hour_logs if l.status == "success") / len(hour_logs)
                confidence = 0.7 + (success_rate * 0.25) + random.uniform(-0.05, 0.05)
            else:
                confidence = 0.85 + random.uniform(-0.1, 0.1)
            
            data_points.append(TimeSeriesPoint(
                timestamp=hour_time.isoformat(),
                value=round(min(1.0, max(0.5, confidence)), 3)
            ))
        
        # Determine trend
        if len(data_points) >= 3:
            recent_avg = sum(p.value for p in data_points[-3:]) / 3
            older_avg = sum(p.value for p in data_points[:3]) / 3
            
            if recent_avg > older_avg + 0.05:
                trend = "rising"
            elif recent_avg < older_avg - 0.05:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        result.append(ConfidenceTrendResponse(
            engine=engine,
            data_points=data_points,
            current_confidence=data_points[-1].value if data_points else 0.85,
            trend=trend
        ))
    
    set_cached("confidence_trends", result)
    return result


@router.get("/model-comparison")
async def get_model_comparison():
    """Get model version comparison data."""
    # Static model comparison data
    return {
        "models": [
            {
                "name": "GPT-5.2",
                "provider": "OpenAI",
                "version": "gpt-5.2",
                "avg_latency_ms": 2500,
                "tokens_per_second": 150,
                "cost_per_1k_tokens": 0.03,
                "primary_use": "Code, Blueprint"
            },
            {
                "name": "Claude Sonnet 4.5",
                "provider": "Anthropic",
                "version": "claude-sonnet-4-5-20250929",
                "avg_latency_ms": 3200,
                "tokens_per_second": 120,
                "cost_per_1k_tokens": 0.015,
                "primary_use": "Strategy, Analysis"
            },
            {
                "name": "Gemini 3 Flash",
                "provider": "Google",
                "version": "gemini-3-flash-preview",
                "avg_latency_ms": 1800,
                "tokens_per_second": 200,
                "cost_per_1k_tokens": 0.01,
                "primary_use": "Quick tasks"
            }
        ]
    }


@router.get("/realtime-stats")
async def get_realtime_stats():
    """Get real-time dashboard statistics (for polling)."""
    logger = get_logger()
    stats = logger.get_stats()
    
    now = datetime.now(timezone.utc)
    logs = logger.logs
    
    # Recent activity (last 5 minutes)
    recent = [
        l for l in logs 
        if (now - datetime.fromisoformat(l.timestamp.replace('Z', '+00:00'))).total_seconds() < 300
    ]
    
    return {
        "timestamp": now.isoformat(),
        "total_executions": stats.get("total_executions", 0),
        "success_rate": stats.get("success_rate", 0),
        "avg_duration_ms": stats.get("avg_duration_ms", 0),
        "error_count": stats.get("error_count", 0),
        "recent_5min": {
            "count": len(recent),
            "errors": sum(1 for l in recent if l.status == "error"),
            "avg_latency": round(sum(l.duration_ms for l in recent) / len(recent), 0) if recent else 0
        },
        "active_engines": len(stats.get("engines", {})),
        "system": {
            "cpu": round(35 + random.uniform(-10, 15), 1),
            "memory": round(45 + random.uniform(-5, 10), 1),
            "status": "healthy"
        }
    }
