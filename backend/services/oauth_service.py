"""
OAuth Service
Handles OAuth2 authentication with Google and GitHub.
"""

import os
import secrets
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple
from urllib.parse import urlencode
from bson import ObjectId

from database import (
    users_collection,
    sessions_collection,
    teams_collection,
    team_memberships_collection,
)
from core.security import (
    create_access_token,
    create_refresh_token,
    generate_slug,
    get_token_expiry_seconds,
    get_refresh_token_expiry,
)
from services.audit_service import create_audit_log
from services.email_service import APP_URL


class OAuthError(Exception):
    """Custom exception for OAuth errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# OAuth Configuration
OAUTH_CONFIGS = {
    "google": {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "profile_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["email", "profile"],
    },
    "github": {
        "client_id": os.environ.get("GITHUB_CLIENT_ID", ""),
        "client_secret": os.environ.get("GITHUB_CLIENT_SECRET", ""),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "profile_url": "https://api.github.com/user",
        "email_url": "https://api.github.com/user/emails",
        "scopes": ["read:user", "user:email"],
    },
}


def get_oauth_config(provider: str) -> Dict:
    """Get OAuth configuration for a provider."""
    config = OAUTH_CONFIGS.get(provider.lower())
    if not config:
        raise OAuthError(f"Unknown OAuth provider: {provider}", 400)
    return config


def is_oauth_configured(provider: str) -> bool:
    """Check if OAuth provider is properly configured."""
    config = OAUTH_CONFIGS.get(provider.lower(), {})
    return bool(config.get("client_id") and config.get("client_secret"))


def get_redirect_uri(provider: str) -> str:
    """Get OAuth redirect URI for a provider."""
    return f"{APP_URL}/api/auth/oauth/{provider}/callback"


def generate_oauth_state() -> str:
    """Generate a secure state parameter for CSRF protection."""
    return secrets.token_urlsafe(32)


def get_authorization_url(provider: str, state: str) -> str:
    """Generate the OAuth authorization URL."""
    config = get_oauth_config(provider)
    
    params = {
        "client_id": config["client_id"],
        "redirect_uri": get_redirect_uri(provider),
        "state": state,
        "response_type": "code",
    }
    
    if provider == "google":
        params["scope"] = " ".join(config["scopes"])
        params["access_type"] = "offline"
        params["prompt"] = "consent"
    elif provider == "github":
        params["scope"] = " ".join(config["scopes"])
    
    return f"{config['auth_url']}?{urlencode(params)}"


async def exchange_code_for_tokens(provider: str, code: str) -> Dict:
    """Exchange authorization code for access tokens."""
    config = get_oauth_config(provider)
    
    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": code,
        "redirect_uri": get_redirect_uri(provider),
    }
    
    if provider == "google":
        data["grant_type"] = "authorization_code"
    
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            config["token_url"],
            data=data,
            headers=headers,
            timeout=30.0,
        )
        
        if response.status_code != 200:
            raise OAuthError(f"Failed to exchange code: {response.text}", 400)
        
        return response.json()


async def get_google_profile(access_token: str) -> Dict:
    """Fetch user profile from Google."""
    config = get_oauth_config("google")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            config["profile_url"],
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30.0,
        )
        
        if response.status_code != 200:
            raise OAuthError("Failed to fetch Google profile", 400)
        
        data = response.json()
        
        return {
            "provider": "google",
            "provider_id": data["id"],
            "email": data["email"],
            "email_verified": data.get("verified_email", False),
            "first_name": data.get("given_name", ""),
            "last_name": data.get("family_name", ""),
            "avatar_url": data.get("picture"),
        }


async def get_github_profile(access_token: str) -> Dict:
    """Fetch user profile from GitHub."""
    config = get_oauth_config("github")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        # Get profile
        response = await client.get(
            config["profile_url"],
            headers=headers,
            timeout=30.0,
        )
        
        if response.status_code != 200:
            raise OAuthError("Failed to fetch GitHub profile", 400)
        
        profile = response.json()
        
        # Get email (might be private)
        email = profile.get("email")
        
        if not email:
            # Fetch emails separately
            email_response = await client.get(
                config["email_url"],
                headers=headers,
                timeout=30.0,
            )
            
            if email_response.status_code == 200:
                emails = email_response.json()
                # Find primary email
                for e in emails:
                    if e.get("primary"):
                        email = e["email"]
                        break
                # Fallback to first email
                if not email and emails:
                    email = emails[0]["email"]
        
        if not email:
            raise OAuthError("Could not retrieve email from GitHub. Please make email public.", 400)
        
        # Parse name
        name = profile.get("name", "") or ""
        name_parts = name.split(" ", 1)
        first_name = name_parts[0] if name_parts else profile.get("login", "")
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        return {
            "provider": "github",
            "provider_id": str(profile["id"]),
            "email": email,
            "email_verified": True,  # GitHub emails are verified
            "first_name": first_name,
            "last_name": last_name,
            "avatar_url": profile.get("avatar_url"),
        }


async def get_oauth_profile(provider: str, access_token: str) -> Dict:
    """Get user profile from OAuth provider."""
    if provider == "google":
        return await get_google_profile(access_token)
    elif provider == "github":
        return await get_github_profile(access_token)
    else:
        raise OAuthError(f"Unknown provider: {provider}", 400)


async def handle_oauth_callback(
    provider: str,
    code: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict:
    """
    Handle OAuth callback.
    - Exchanges code for tokens
    - Fetches user profile
    - Creates or updates user
    - Returns auth tokens
    """
    # Exchange code for tokens
    tokens = await exchange_code_for_tokens(provider, code)
    access_token = tokens.get("access_token")
    
    if not access_token:
        raise OAuthError("Failed to get access token", 400)
    
    # Get user profile
    profile = await get_oauth_profile(provider, access_token)
    email = profile["email"].lower()
    
    now = datetime.now(timezone.utc)
    
    # Check if user exists by email
    existing_user = await users_collection().find_one({"email": email})
    
    if existing_user:
        user_id = str(existing_user["_id"])
        
        # Check if OAuth provider is already linked
        oauth_providers = existing_user.get("oauth_providers", [])
        provider_linked = any(p["provider"] == provider for p in oauth_providers)
        
        if not provider_linked:
            # Link OAuth provider to existing account
            oauth_providers.append({
                "provider": provider,
                "provider_id": profile["provider_id"],
                "linked_at": now,
            })
            
            await users_collection().update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        "oauth_providers": oauth_providers,
                        "last_login_at": now,
                        "avatar_url": profile.get("avatar_url"),
                    }
                }
            )
        else:
            # Just update last login
            await users_collection().update_one(
                {"_id": existing_user["_id"]},
                {"$set": {"last_login_at": now}}
            )
        
        # Get existing team
        membership = await team_memberships_collection().find_one({
            "user_id": user_id,
            "is_active": True
        })
        
        team = None
        if membership:
            team = await teams_collection().find_one({"_id": ObjectId(membership["team_id"])})
        
        # Audit log
        await create_audit_log(
            user_id=user_id,
            action=f"auth.oauth_login.{provider}",
            team_id=str(team["_id"]) if team else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
    else:
        # Create new user
        user_doc = {
            "email": email,
            "password_hash": None,  # No password for OAuth-only users
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
            "system_role": "user",
            "oauth_providers": [{
                "provider": provider,
                "provider_id": profile["provider_id"],
                "linked_at": now,
            }],
            "email_verified": profile.get("email_verified", True),
            "avatar_url": profile.get("avatar_url"),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login_at": now,
        }
        
        user_result = await users_collection().insert_one(user_doc)
        user_id = str(user_result.inserted_id)
        
        # Create personal team
        team_name = f"{profile['first_name']}'s Team"
        team_doc = {
            "name": team_name,
            "slug": generate_slug(team_name),
            "type": "personal",
            "owner_id": user_id,
            "settings": {
                "allow_member_invites": False,
                "default_member_role": "member",
                "require_2fa": False,
            },
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        
        team_result = await teams_collection().insert_one(team_doc)
        team_id = str(team_result.inserted_id)
        
        # Create membership
        membership_doc = {
            "user_id": user_id,
            "team_id": team_id,
            "role": "owner",
            "invited_by": None,
            "invited_at": None,
            "joined_at": now,
            "is_active": True,
        }
        
        await team_memberships_collection().insert_one(membership_doc)
        
        team = {**team_doc, "_id": team_result.inserted_id}
        
        # Audit log
        await create_audit_log(
            user_id=user_id,
            action=f"auth.oauth_signup.{provider}",
            team_id=team_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    # Create JWT tokens
    jwt_access_token = create_access_token(user_id)
    jwt_refresh_token, refresh_token_hash = create_refresh_token(user_id)
    
    # Store session
    session_doc = {
        "user_id": user_id,
        "refresh_token_hash": refresh_token_hash,
        "device_info": f"OAuth ({provider})",
        "ip_address": ip_address,
        "user_agent": user_agent,
        "created_at": now,
        "expires_at": get_refresh_token_expiry(),
        "last_used_at": now,
        "revoked_at": None,
        "is_active": True,
    }
    
    await sessions_collection().insert_one(session_doc)
    
    # Get user for response
    user = await users_collection().find_one({"_id": ObjectId(user_id)})
    
    # Get team for response
    current_team = None
    if team:
        membership = await team_memberships_collection().find_one({
            "user_id": user_id,
            "team_id": str(team["_id"]),
            "is_active": True
        })
        if membership:
            current_team = {
                "id": str(team["_id"]),
                "name": team["name"],
                "slug": team["slug"],
                "type": team["type"],
                "role": membership["role"],
            }
    
    return {
        "access_token": jwt_access_token,
        "refresh_token": jwt_refresh_token,
        "token_type": "bearer",
        "expires_in": get_token_expiry_seconds(),
        "user": {
            "id": user_id,
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "system_role": user.get("system_role", "user"),
            "email_verified": user.get("email_verified", True),
            "is_active": True,
            "created_at": user["created_at"].isoformat(),
            "last_login_at": now.isoformat(),
            "has_oauth": True,
            "avatar_url": user.get("avatar_url"),
        },
        "current_team": current_team,
    }
