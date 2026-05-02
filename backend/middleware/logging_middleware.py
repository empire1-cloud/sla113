"""
Middleware to automatically log all engine API calls.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json
from typing import Callable

from services.execution_logger import get_logger


# Endpoints to log (engine endpoints only)
LOGGED_ENDPOINTS = [
    "/api/strategy",
    "/api/plan",
    "/api/analyze",
    "/api/opportunities",
    "/api/evaluate",
    "/api/pricing",
    "/api/blueprint",
    "/api/persona",
    "/api/anime/character",
    "/api/anime/lore",
    "/api/anime/story",
    "/api/art-direction",
    "/api/money-pipeline",
    "/api/pipeline/compose",
    "/api/core/execute",
    "/api/route"
]


def get_engine_from_path(path: str) -> str:
    """Extract engine name from path."""
    path_to_engine = {
        "/api/strategy": "strategy_engine",
        "/api/plan": "plan_builder_engine",
        "/api/analyze": "analysis_engine",
        "/api/opportunities": "opportunity_mapper_engine",
        "/api/evaluate": "evaluator_engine",
        "/api/pricing": "pricing_engine",
        "/api/blueprint": "blueprint_engine",
        "/api/persona": "persona_engine",
        "/api/anime/character": "anime_character_engine",
        "/api/anime/lore": "anime_lore_engine",
        "/api/anime/story": "anime_story_engine",
        "/api/art-direction": "art_direction_engine",
        "/api/money-pipeline": "money_pipeline_engine",
        "/api/pipeline/compose": "pipeline_composer_engine",
        "/api/core/execute": "hybrid_intelligence_core",
        "/api/route": "routing_engine"
    }
    
    for endpoint, engine in path_to_engine.items():
        if path.startswith(endpoint):
            return engine
    return "unknown"


class ExecutionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is an endpoint we should log
        path = request.url.path
        method = request.method
        
        should_log = method == "POST" and any(path.startswith(ep) for ep in LOGGED_ENDPOINTS)
        
        if not should_log:
            return await call_next(request)
        
        # Get request body
        body = await request.body()
        try:
            input_data = json.loads(body) if body else {}
        except:
            input_data = {"raw": body.decode()[:500] if body else ""}
        
        # Reconstruct request with body (since we consumed it)
        async def receive():
            return {"type": "http.request", "body": body}
        
        request = Request(request.scope, receive)
        
        # Execute request and measure time
        start_time = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Get response body for logging
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Parse response
        output_data = None
        error = None
        status = "success"
        
        try:
            if response.status_code >= 400:
                status = "error"
                error = response_body.decode()[:500]
            else:
                output_data = json.loads(response_body)
        except:
            if response.status_code >= 400:
                error = "Failed to parse error response"
        
        # Log the execution
        logger = get_logger()
        engine = get_engine_from_path(path)
        
        # Truncate large outputs for storage
        if output_data and len(json.dumps(output_data)) > 10000:
            output_data = {"_truncated": True, "summary": str(output_data)[:1000]}
        
        logger.log(
            engine=engine,
            endpoint=path,
            method=method,
            input_data=input_data,
            output_data=output_data,
            error=error,
            duration_ms=duration_ms,
            source="api"
        )
        
        # Return reconstructed response
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
