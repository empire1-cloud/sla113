"""
Execution Logger Service

Logs all engine calls and pipeline runs with timestamps, inputs, outputs, and duration.
Stores logs in memory with optional file persistence.
"""

import os
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from threading import Lock
import asyncio

LOG_FILE = "/app/backend/execution_logs.json"
MAX_LOGS = 1000  # Keep last 1000 logs in memory


class ExecutionLog(BaseModel):
    id: str
    timestamp: str
    engine: str
    endpoint: str
    method: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int
    status: str  # "success", "error"
    source: str  # "api", "pipeline"
    pipeline_id: Optional[str] = None


class ExecutionLogger:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logs: List[ExecutionLog] = []
        self._log_lock = Lock()
        self._load_logs()
    
    def _load_logs(self):
        """Load logs from file if exists."""
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r') as f:
                    data = json.load(f)
                    self.logs = [ExecutionLog(**log) for log in data[-MAX_LOGS:]]
        except Exception as e:
            print(f"Error loading logs: {e}")
            self.logs = []
    
    def _save_logs(self):
        """Save logs to file."""
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump([log.model_dump() for log in self.logs[-MAX_LOGS:]], f)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def log(
        self,
        engine: str,
        endpoint: str,
        method: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: int = 0,
        source: str = "api",
        pipeline_id: Optional[str] = None
    ) -> ExecutionLog:
        """Log an execution."""
        log_entry = ExecutionLog(
            id=f"{engine}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            engine=engine,
            endpoint=endpoint,
            method=method,
            input_data=input_data,
            output_data=output_data,
            error=error,
            duration_ms=duration_ms,
            status="success" if error is None else "error",
            source=source,
            pipeline_id=pipeline_id
        )
        
        with self._log_lock:
            self.logs.append(log_entry)
            # Keep only last MAX_LOGS
            if len(self.logs) > MAX_LOGS:
                self.logs = self.logs[-MAX_LOGS:]
            self._save_logs()
        
        return log_entry
    
    def get_logs(
        self,
        engine: Optional[str] = None,
        status: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get logs with optional filtering."""
        filtered = self.logs.copy()
        
        # Apply filters
        if engine:
            filtered = [l for l in filtered if engine.lower() in l.engine.lower()]
        
        if status:
            filtered = [l for l in filtered if l.status == status]
        
        if source:
            filtered = [l for l in filtered if l.source == source]
        
        if search:
            search_lower = search.lower()
            filtered = [
                l for l in filtered 
                if search_lower in l.engine.lower() 
                or search_lower in str(l.input_data).lower()
                or search_lower in l.endpoint.lower()
            ]
        
        # Sort by timestamp descending (newest first)
        filtered.sort(key=lambda x: x.timestamp, reverse=True)
        
        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        
        return {
            "logs": [l.model_dump() for l in paginated],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.logs:
            return {
                "total_executions": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_duration_ms": 0,
                "engines": {},
                "recent_activity": []
            }
        
        success_count = len([l for l in self.logs if l.status == "success"])
        error_count = len([l for l in self.logs if l.status == "error"])
        avg_duration = sum(l.duration_ms for l in self.logs) / len(self.logs)
        
        # Count by engine
        engine_counts = {}
        for log in self.logs:
            engine_counts[log.engine] = engine_counts.get(log.engine, 0) + 1
        
        # Recent activity (last 24 hours, grouped by hour)
        now = datetime.now(timezone.utc)
        recent = {}
        for log in self.logs:
            try:
                log_time = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
                hours_ago = int((now - log_time).total_seconds() / 3600)
                if hours_ago < 24:
                    recent[hours_ago] = recent.get(hours_ago, 0) + 1
            except:
                pass
        
        return {
            "total_executions": len(self.logs),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": round(success_count / len(self.logs) * 100, 1) if self.logs else 0,
            "avg_duration_ms": round(avg_duration, 0),
            "engines": engine_counts,
            "recent_activity": [{"hour": h, "count": c} for h, c in sorted(recent.items())]
        }
    
    def clear_logs(self) -> int:
        """Clear all logs. Returns count of cleared logs."""
        with self._log_lock:
            count = len(self.logs)
            self.logs = []
            self._save_logs()
        return count


# Global logger instance
def get_logger() -> ExecutionLogger:
    return ExecutionLogger()
