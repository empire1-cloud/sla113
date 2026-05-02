"""
Billing API Routes
Handles subscription management, checkout, and webhooks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional
from pydantic import BaseModel
from time import time

from core.dependencies import get_current_user, get_current_team, get_client_info
from services.billing_service import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_event,
    get_team_billing,
    get_available_plans,
    BillingError,
    STRIPE_AVAILABLE,
)
from services.usage_service import get_team_usage_with_limits
from database import teams_collection, users_collection
from bson import ObjectId


router = APIRouter(prefix="/billing", tags=["Billing"])

# Cache for plans (static data, 10 minute TTL)
_plans_cache = {"data": None, "timestamp": 0}
PLANS_CACHE_TTL = 600  # 10 minutes


class CheckoutRequest(BaseModel):
    plan: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class PortalRequest(BaseModel):
    return_url: Optional[str] = None


@router.get("/status")
async def get_billing_status(user: dict = Depends(get_current_user)):
    """Get billing configuration status."""
    return {
        "stripe_configured": STRIPE_AVAILABLE,
        "team_id": user.get("team_id"),
    }


@router.get("/plans")
async def list_plans():
    """Get available subscription plans (cached)."""
    global _plans_cache
    
    now = time()
    
    # Return cached data if fresh
    if _plans_cache["data"] and (now - _plans_cache["timestamp"]) < PLANS_CACHE_TTL:
        return {"plans": _plans_cache["data"]}
    
    # Fetch fresh data
    plans = get_available_plans()
    _plans_cache = {"data": plans, "timestamp": now}
    
    return {"plans": plans}


@router.get("/team")
async def get_team_billing_info(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Get billing information for current team."""
    team = await get_current_team(request, user)
    team_id = team.get("_id")
    
    try:
        billing = await get_team_billing(team_id)
        usage = await get_team_usage_with_limits(team_id)
        
        return {
            "billing": billing,
            "usage": usage,
        }
    except BillingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/checkout-session")
async def create_checkout(
    request: Request,
    data: CheckoutRequest,
    user: dict = Depends(get_current_user),
):
    """Create a Stripe checkout session for subscription upgrade."""
    team_id = user.get("team_id")
    user_id = user["_id"]
    
    if not team_id:
        raise HTTPException(status_code=400, detail="No team selected")
    
    # Verify user is owner/admin
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Get owner email
    user_doc = await users_collection().find_one({"_id": ObjectId(user_id)})
    owner_email = user_doc["email"] if user_doc else ""
    
    try:
        result = await create_checkout_session(
            team_id=team_id,
            plan=data.plan,
            owner_email=owner_email,
            team_name=team["name"],
            user_id=user_id,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
        )
        return result
    except BillingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/portal-session")
async def create_portal(
    request: Request,
    data: PortalRequest,
    user: dict = Depends(get_current_user),
):
    """Create a Stripe customer portal session."""
    team_id = user.get("team_id")
    user_id = user["_id"]
    
    if not team_id:
        raise HTTPException(status_code=400, detail="No team selected")
    
    team = await teams_collection().find_one({"_id": ObjectId(team_id)})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    user_doc = await users_collection().find_one({"_id": ObjectId(user_id)})
    owner_email = user_doc["email"] if user_doc else ""
    
    try:
        result = await create_portal_session(
            team_id=team_id,
            owner_email=owner_email,
            team_name=team["name"],
            user_id=user_id,
            return_url=data.return_url,
        )
        return result
    except BillingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    
    try:
        result = await handle_webhook_event(payload, stripe_signature or "")
        return result
    except BillingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/usage")
async def get_usage(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Get current usage for the team."""
    team = await get_current_team(request, user)
    team_id = team.get("_id")
    
    return await get_team_usage_with_limits(team_id)
