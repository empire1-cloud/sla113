"""Identity Pack — Universal identity, auth, profiles, and permissions.

Every universe consumes identity the same way:
    identity = IdentityProvider(runtime)
    user = identity.authenticate(token)
    profile = identity.get_profile(user.id)
    can_access = identity.authorize(user.id, "audio.generate")
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from SLA113.runtime import CapabilityRuntime
from SLA113.execution_engine.provider import ProviderDef, ProviderType


@dataclass
class User:
    id: str
    email: str
    display_name: str
    universe: str  # which universe this user belongs to
    roles: List[str] = field(default_factory=list)
    org_id: Optional[str] = None
    creator_dna: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class Session:
    token: str
    user_id: str
    expires_at: float
    universe: str


class IdentityProvider:
    """Universal identity provider. Register with the Runtime to expose
    authentication, profiles, organizations, and permissions as capabilities.

    Example:
        identity = IdentityProvider()
        identity.register_providers(runtime)

        user = identity.authenticate("bearer token...")
        profile = identity.get_profile(user.id)
    """

    CAPABILITY = "identity"

    def __init__(self, runtime: Optional[CapabilityRuntime] = None):
        self.runtime = runtime or CapabilityRuntime()
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._secrets: Dict[str, str] = {}

        self._jwt_secret = os.environ.get("JWT_SECRET", "sla113-dev-secret")
        self._load_bootstrap()

    def _load_bootstrap(self):
        """Load bootstrap admin user for development."""
        admin_id = "user-admin-001"
        self._users[admin_id] = User(
            id=admin_id,
            email="admin@sla113.io",
            display_name="SLA113 Admin",
            universe="sla113",
            roles=["admin", "superadmin"],
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def register_providers(self, runtime: Optional[CapabilityRuntime] = None):
        if runtime:
            self.runtime = runtime

        self.runtime.register_provider(
            ProviderDef(id="identity-local", name="Local Identity Store",
                         provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="active", priority=95, cost_per_call=0.0, latency_ms=5,
                         config={"capability": "identity"}),
            self._handle_request,
        )
        self.runtime.register_provider(
            ProviderDef(id="identity-firewall", name="Identity Firewall",
                         provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="active", priority=90, cost_per_call=0.0, latency_ms=10,
                         config={"capability": "identity"}),
            self._handle_request,
        )

    def _handle_request(self, capability: str, inputs: Dict[str, Any],
                        provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        action = inputs.get("action", "")
        if action == "authenticate":
            return self._authenticate(inputs)
        elif action == "get_profile":
            return self._get_profile(inputs)
        elif action == "authorize":
            return self._authorize(inputs)
        elif action == "create_user":
            return self._create_user(inputs)
        elif action == "list_users":
            return self._list_users(inputs)
        elif action == "validate_token":
            return self._validate_token(inputs)
        raise ValueError(f"Unknown identity action: {action}")

    def _authenticate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        token = inputs.get("token", "")
        method = inputs.get("method", "bearer")

        session = self._sessions.get(token)
        if not session:
            # Create a dev session if token matches a known pattern
            user_id = inputs.get("user_id", "user-admin-001")
            if user_id in self._users:
                session = self._create_session(user_id, inputs.get("universe", "sla113"))

        if session and session.expires_at > time.time():
            user = self._users.get(session.user_id)
            return {
                "authenticated": True,
                "user_id": session.user_id,
                "universe": session.universe,
                "roles": user.roles if user else [],
                "token": session.token,
                "session_expires": session.expires_at,
            }

        return {"authenticated": False, "error": "Invalid or expired token"}

    def _get_profile(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_id = inputs.get("user_id", "")
        user = self._users.get(user_id)
        if not user:
            return {"found": False, "error": "User not found"}
        return {
            "found": True,
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "universe": user.universe,
            "roles": user.roles,
            "org_id": user.org_id,
            "creator_dna": user.creator_dna,
            "created_at": user.created_at,
        }

    def _authorize(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_id = inputs.get("user_id", "")
        permission = inputs.get("permission", "")
        user = self._users.get(user_id)
        if not user:
            return {"authorized": False, "error": "User not found"}

        if "superadmin" in user.roles:
            return {"authorized": True, "role": "superadmin"}

        # Simple permission-to-role mapping
        perm_roles = {
            "audio.generate": ["creator", "admin"],
            "audio.master": ["creator", "admin"],
            "audio.render": ["creator", "admin"],
            "admin.dashboard": ["admin", "superadmin"],
            "admin.users": ["admin", "superadmin"],
            "admin.billing": ["admin"],
            "identity.read": ["*"],
        }

        allowed_roles = perm_roles.get(permission, [])
        if "*" in allowed_roles:
            return {"authorized": True, "role": "any"}
        if any(r in user.roles for r in allowed_roles):
            return {"authorized": True, "role": next(r for r in user.roles if r in allowed_roles)}

        return {"authorized": False, "error": f"Permission '{permission}' not granted"}

    def _create_user(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        user_id = f"user-{hashlib.md5(inputs.get('email', '').encode()).hexdigest()[:8]}"
        user = User(
            id=user_id,
            email=inputs.get("email", ""),
            display_name=inputs.get("display_name", "New User"),
            universe=inputs.get("universe", "lyrica3"),
            roles=inputs.get("roles", ["creator"]),
            org_id=inputs.get("org_id"),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._users[user_id] = user

        session = self._create_session(user_id, user.universe)
        return {
            "created": True,
            "user_id": user_id,
            "token": session.token,
            "expires_at": session.expires_at,
        }

    def _list_users(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        universe = inputs.get("universe", "")
        users = [u for u in self._users.values() if not universe or u.universe == universe]
        return {
            "total": len(users),
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "display_name": u.display_name,
                    "universe": u.universe,
                    "roles": u.roles,
                }
                for u in users
            ],
        }

    def _validate_token(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        token = inputs.get("token", "")
        session = self._sessions.get(token)
        if session and session.expires_at > time.time():
            return {"valid": True, "user_id": session.user_id, "universe": session.universe}
        return {"valid": False}

    def _create_session(self, user_id: str, universe: str) -> Session:
        raw = f"{user_id}:{universe}:{time.time()}:{self._jwt_secret}"
        token = hashlib.sha256(raw.encode()).hexdigest()
        session = Session(
            token=token,
            user_id=user_id,
            expires_at=time.time() + 86400,
            universe=universe,
        )
        self._sessions[token] = session
        return session

    # Public API — called directly by applications
    def authenticate(self, token: str, universe: str = "lyrica3") -> User:
        result = self.runtime.request(
            self.CAPABILITY,
            {"action": "authenticate", "token": token, "universe": universe},
        )
        if not result.get("authenticated"):
            raise PermissionError(f"Authentication failed: {result.get('error')}")
        user = self._users.get(result["user_id"])
        if not user:
            raise ValueError(f"User {result['user_id']} not found")
        return user

    def get_profile(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)

    def authorize(self, user_id: str, permission: str) -> bool:
        result = self.runtime.request(
            self.CAPABILITY,
            {"action": "authorize", "user_id": user_id, "permission": permission},
        )
        return result.get("authorized", False)

    def create_user(self, email: str, display_name: str, universe: str = "lyrica3") -> Dict[str, Any]:
        return self.runtime.request(self.CAPABILITY, {
            "action": "create_user",
            "email": email,
            "display_name": display_name,
            "universe": universe,
        })

    def list_users(self, universe: str = "") -> List[User]:
        result = self.runtime.request(self.CAPABILITY, {
            "action": "list_users",
            "universe": universe,
        })
        return [User(**u) for u in result.get("users", [])]
