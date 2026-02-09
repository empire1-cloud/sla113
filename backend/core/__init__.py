"""Core package initialization."""

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    generate_invite_token,
    generate_reset_token,
    generate_slug,
    get_token_expiry_seconds,
    get_refresh_token_expiry,
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

from .dependencies import (
    get_current_user,
    get_optional_user,
    get_current_team,
    get_user_and_team,
    require_team_role,
    require_system_admin,
    get_client_info,
)

__all__ = [
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "hash_token",
    "generate_invite_token",
    "generate_reset_token",
    "generate_slug",
    "get_token_expiry_seconds",
    "get_refresh_token_expiry",
    "JWT_SECRET_KEY",
    "JWT_ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",
    
    # Dependencies
    "get_current_user",
    "get_optional_user",
    "get_current_team",
    "get_user_and_team",
    "require_team_role",
    "require_system_admin",
    "get_client_info",
]
