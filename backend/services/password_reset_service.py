"""
Password Reset Service
Handles forgot password and reset token management.
"""

import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from bson import ObjectId

from database import users_collection, get_database
from services.email_service import send_email, APP_NAME, APP_URL
from services.audit_service import create_audit_log


class PasswordResetError(Exception):
    """Custom exception for password reset errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def password_reset_tokens_collection():
    """Get password reset tokens collection."""
    return get_database().password_reset_tokens


def generate_reset_token() -> tuple[str, str]:
    """Generate a secure reset token and its hash."""
    token = secrets.token_urlsafe(36)  # 48 bytes base64
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


async def check_rate_limit(email: str, ip_address: Optional[str]) -> bool:
    """
    Check if rate limit is exceeded.
    Limit: 3 requests per email per hour, 10 requests per IP per hour.
    Returns True if request is allowed.
    """
    collection = password_reset_tokens_collection()
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    
    # Check email rate limit
    email_count = await collection.count_documents({
        "email": email.lower(),
        "created_at": {"$gte": one_hour_ago}
    })
    if email_count >= 3:
        return False
    
    # Check IP rate limit
    if ip_address:
        ip_count = await collection.count_documents({
            "ip_address": ip_address,
            "created_at": {"$gte": one_hour_ago}
        })
        if ip_count >= 10:
            return False
    
    return True


async def request_password_reset(
    email: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict:
    """
    Request a password reset.
    - Checks if user exists
    - Enforces rate limiting
    - Creates reset token (15 min expiry)
    - Sends reset email
    
    Always returns success message to prevent email enumeration.
    """
    email_lower = email.lower()
    
    # Check rate limit
    if not await check_rate_limit(email_lower, ip_address):
        raise PasswordResetError("Too many reset requests. Please try again later.", 429)
    
    # Find user
    user = await users_collection().find_one({"email": email_lower, "is_active": True})
    
    now = datetime.now(timezone.utc)
    
    # Always create a token record for rate limiting purposes
    token, token_hash = generate_reset_token()
    
    token_doc = {
        "email": email_lower,
        "token_hash": token_hash,
        "created_at": now,
        "expires_at": now + timedelta(minutes=15),
        "used_at": None,
        "ip_address": ip_address,
        "user_id": str(user["_id"]) if user else None,
    }
    
    await password_reset_tokens_collection().insert_one(token_doc)
    
    # If user exists, send email
    if user:
        user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
        await send_reset_email(email_lower, user_name, token)
        
        # Audit log
        await create_audit_log(
            user_id=str(user["_id"]),
            action="auth.password_reset_request",
            details={"email": email_lower},
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    return {
        "message": "If an account exists with that email, you will receive password reset instructions.",
        "expires_in_minutes": 15,
    }


async def validate_reset_token(token: str) -> Optional[Dict]:
    """
    Validate a password reset token.
    Returns token document if valid, None otherwise.
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    
    token_doc = await password_reset_tokens_collection().find_one({
        "token_hash": token_hash,
    })
    
    if not token_doc:
        return None
    
    # Check if already used
    if token_doc.get("used_at"):
        return None
    
    # Check expiry
    expires_at = token_doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            return None
    
    # Check if user exists
    if not token_doc.get("user_id"):
        return None
    
    return token_doc


async def confirm_password_reset(
    token: str,
    new_password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Dict:
    """
    Confirm password reset with token and new password.
    - Validates token
    - Updates user password
    - Marks token as used
    - Revokes all user sessions
    """
    from core.security import hash_password
    
    token_doc = await validate_reset_token(token)
    
    if not token_doc:
        raise PasswordResetError("Invalid or expired reset token", 400)
    
    user_id = token_doc["user_id"]
    now = datetime.now(timezone.utc)
    
    # Update user password
    new_password_hash = hash_password(new_password)
    result = await users_collection().update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": new_password_hash, "updated_at": now}}
    )
    
    if result.matched_count == 0:
        raise PasswordResetError("User not found", 404)
    
    # Mark token as used
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    await password_reset_tokens_collection().update_one(
        {"token_hash": token_hash},
        {"$set": {"used_at": now}}
    )
    
    # Revoke all user sessions for security
    from database import sessions_collection
    await sessions_collection().update_many(
        {"user_id": user_id, "is_active": True},
        {"$set": {"is_active": False, "revoked_at": now}}
    )
    
    # Audit log
    await create_audit_log(
        user_id=user_id,
        action="auth.password_reset_complete",
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    return {
        "message": "Password has been reset successfully. Please log in with your new password.",
    }


def get_reset_email_html(user_name: str, reset_url: str) -> str:
    """Generate HTML content for password reset email."""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #0f0f0f; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f0f0f; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1a1a2e; border-radius: 12px; overflow: hidden;">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #ff6b6b, #ee5253); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #fff; font-size: 24px; font-weight: 700;">
                                🔐 Password Reset
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px; color: #ffffff; font-size: 20px; font-weight: 600;">
                                Hi {user_name},
                            </h2>
                            
                            <p style="margin: 0 0 20px; color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                We received a request to reset your password for your <strong style="color: #00d4aa;">{APP_NAME}</strong> account.
                            </p>
                            
                            <p style="margin: 0 0 20px; color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                Click the button below to set a new password:
                            </p>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #ff6b6b, #ee5253); color: #fff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Reset My Password
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 10px; color: #666666; font-size: 14px;">
                                Or copy and paste this link in your browser:
                            </p>
                            <p style="margin: 0 0 20px; color: #4d9fff; font-size: 14px; word-break: break-all;">
                                {reset_url}
                            </p>
                            
                            <div style="background-color: #252536; border-radius: 8px; padding: 15px; margin-top: 20px;">
                                <p style="margin: 0; color: #ff6b6b; font-size: 13px;">
                                    ⏰ This link expires in <strong>15 minutes</strong>
                                </p>
                            </div>
                            
                            <p style="margin: 20px 0 0; color: #666666; font-size: 14px;">
                                If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #151520; padding: 20px 30px; text-align: center;">
                            <p style="margin: 0; color: #666666; font-size: 13px;">
                                This is an automated message from {APP_NAME}. Please do not reply.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


async def send_reset_email(email: str, user_name: str, token: str) -> Optional[dict]:
    """Send password reset email."""
    reset_url = f"{APP_URL}/reset-password?token={token}"
    
    html_content = get_reset_email_html(user_name, reset_url)
    
    return await send_email(
        to_email=email,
        subject=f"Reset your {APP_NAME} password",
        html_content=html_content,
    )
