"""
Engine execution wrapper with auth and team context.
Provides decorators and utilities for protecting engine routes.
"""

import time
from functools import wraps
from typing import Callable, Any, Optional
from fastapi import Request, HTTPException, Depends

from core.dependencies import get_current_user, get_current_team
from services.execution_logger_db import log_execution


class EngineContext:
    """Context object passed to engine functions with auth and team info."""
    
    def __init__(
        self,
        user: dict,
        team: dict,
        request: Request,
    ):
        self.user = user
        self.team = team
        self.request = request
        self.user_id = user["_id"]
        self.team_id = str(team["_id"]) if "_id" in team else team.get("id", team.get("team_id"))
        self.user_role = team.get("user_role", "member")
    
    @property
    def can_write(self) -> bool:
        """Check if user has write permissions (owner, admin, or member)."""
        return self.user_role in ["owner", "admin", "member"]
    
    @property
    def can_admin(self) -> bool:
        """Check if user has admin permissions."""
        return self.user_role in ["owner", "admin"]
    
    def require_write(self):
        """Raise exception if user doesn't have write permission."""
        if not self.can_write:
            raise HTTPException(
                status_code=403,
                detail="You need member, admin, or owner role to perform this action"
            )
    
    def require_admin(self):
        """Raise exception if user doesn't have admin permission."""
        if not self.can_admin:
            raise HTTPException(
                status_code=403,
                detail="You need admin or owner role to perform this action"
            )


async def get_engine_context(
    request: Request,
    user: dict = Depends(get_current_user),
) -> EngineContext:
    """
    Dependency that provides engine context with auth and team.
    Use this in protected engine routes.
    """
    team = await get_current_team(request, user)
    return EngineContext(user=user, team=team, request=request)


async def log_engine_call(
    ctx: EngineContext,
    engine: str,
    input_data: dict,
    output_data: Optional[dict] = None,
    error_message: Optional[str] = None,
    duration_ms: int = 0,
    source: str = "api",
    pipeline_id: Optional[str] = None,
):
    """Log an engine execution with team context."""
    await log_execution(
        team_id=ctx.team_id,
        user_id=ctx.user_id,
        engine=engine,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message,
        duration_ms=duration_ms,
        source=source,
        pipeline_id=pipeline_id,
        endpoint=str(ctx.request.url.path),
        method=ctx.request.method,
    )


class EngineExecutor:
    """
    Wrapper for executing engine calls with automatic logging and error handling.
    
    Usage:
        async with EngineExecutor(ctx, "strategy_engine", input_data) as executor:
            result = await some_engine_call(input_data)
            executor.set_output(result)
            return result
    """
    
    def __init__(
        self,
        ctx: EngineContext,
        engine: str,
        input_data: dict,
        source: str = "api",
        pipeline_id: Optional[str] = None,
    ):
        self.ctx = ctx
        self.engine = engine
        self.input_data = input_data
        self.source = source
        self.pipeline_id = pipeline_id
        self.output_data = None
        self.error_message = None
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        if exc_val:
            self.error_message = str(exc_val)
        
        await log_engine_call(
            ctx=self.ctx,
            engine=self.engine,
            input_data=self.input_data,
            output_data=self.output_data,
            error_message=self.error_message,
            duration_ms=duration_ms,
            source=self.source,
            pipeline_id=self.pipeline_id,
        )
        
        # Don't suppress exceptions
        return False
    
    def set_output(self, output: dict):
        """Set the output data for logging."""
        self.output_data = output
