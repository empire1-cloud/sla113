"""
API Keys Routes
Manage API keys for teams.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List

from core.dependencies import get_current_user, get_client_info
from core.engine_context import get_engine_context, EngineContext
from services.api_key_service import (
    create_api_key,
    list_api_keys,
    revoke_api_key,
    APIKeyError,
)
from services.usage_service import UsageLimitError


router = APIRouter(tags=["API Keys"])


class CreateAPIKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    created_at: str
    last_used_at: str | None
    created_by: str | None


class APIKeyCreatedResponse(BaseModel):
    id: str
    name: str
    key: str  # Only shown once!
    key_prefix: str
    created_at: str


@router.post("/teams/{team_id}/api-keys", response_model=APIKeyCreatedResponse)
async def create_key(
    team_id: str,
    data: CreateAPIKeyRequest,
    request: Request,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Create a new API key for the team.
    The raw key is only shown once - make sure to save it!
    """
    ctx.require_admin()
    
    if ctx.team_id != team_id:
        raise HTTPException(status_code=403, detail="Not authorized for this team")
    
    try:
        client_info = await get_client_info(request)
        result = await create_api_key(
            team_id=team_id,
            name=data.name,
            user_id=ctx.user_id,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except UsageLimitError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except APIKeyError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/teams/{team_id}/api-keys", response_model=List[APIKeyResponse])
async def list_keys(
    team_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """List all API keys for the team."""
    ctx.require_read()
    
    if ctx.team_id != team_id:
        raise HTTPException(status_code=403, detail="Not authorized for this team")
    
    return await list_api_keys(team_id)


@router.delete("/teams/{team_id}/api-keys/{key_id}")
async def revoke_key(
    team_id: str,
    key_id: str,
    request: Request,
    ctx: EngineContext = Depends(get_engine_context),
):
    """Revoke an API key."""
    ctx.require_admin()
    
    if ctx.team_id != team_id:
        raise HTTPException(status_code=403, detail="Not authorized for this team")
    
    try:
        client_info = await get_client_info(request)
        result = await revoke_api_key(
            team_id=team_id,
            key_id=key_id,
            user_id=ctx.user_id,
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent"),
        )
        return result
    except APIKeyError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
