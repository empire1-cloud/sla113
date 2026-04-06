"""
Email Service
Handles sending transactional emails using Resend API.
"""

import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Check if Resend is available
RESEND_AVAILABLE = False
try:
    import resend
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        RESEND_AVAILABLE = True
        logger.info("Resend email service initialized")
    else:
        logger.warning("RESEND_API_KEY not set - email service disabled")
except ImportError:
    logger.warning("resend package not installed - email service disabled")


SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")
APP_NAME = "Hybrid Intelligence"
APP_URL = os.environ.get("FRONTEND_URL", "https://genesis-engine-4.preview.emergentagent.com")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> Optional[dict]:
    """
    Send an email using Resend API.
    Returns email ID on success, None on failure.
    """
    if not RESEND_AVAILABLE:
        logger.warning(f"Email service disabled - would have sent to {to_email}: {subject}")
        return {"id": "mock_email_id", "status": "mocked"}
    
    params = {
        "from": f"{APP_NAME} <{SENDER_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {email.get('id')}")
        return email
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return None


def get_invite_email_html(
    team_name: str,
    inviter_name: str,
    role: str,
    invite_url: str,
    expires_in_days: int = 7,
) -> str:
    """Generate HTML content for team invite email."""
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
                        <td style="background: linear-gradient(135deg, #00d4aa, #00a885); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #000; font-size: 24px; font-weight: 700;">
                                🧠 {APP_NAME}
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px; color: #ffffff; font-size: 22px; font-weight: 600;">
                                You've been invited to join a team!
                            </h2>
                            
                            <p style="margin: 0 0 20px; color: #a0a0a0; font-size: 16px; line-height: 1.6;">
                                <strong style="color: #00d4aa;">{inviter_name}</strong> has invited you to join 
                                <strong style="color: #ffffff;">{team_name}</strong> as a <strong style="color: #4d9fff;">{role}</strong>.
                            </p>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{invite_url}" style="display: inline-block; background: linear-gradient(135deg, #00d4aa, #00a885); color: #000; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                                            Accept Invitation
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 10px; color: #666666; font-size: 14px;">
                                Or copy and paste this link in your browser:
                            </p>
                            <p style="margin: 0 0 20px; color: #4d9fff; font-size: 14px; word-break: break-all;">
                                {invite_url}
                            </p>
                            
                            <div style="background-color: #252536; border-radius: 8px; padding: 15px; margin-top: 20px;">
                                <p style="margin: 0; color: #ff6b6b; font-size: 13px;">
                                    ⏰ This invitation expires in <strong>{expires_in_days} days</strong>
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #151520; padding: 20px 30px; text-align: center;">
                            <p style="margin: 0; color: #666666; font-size: 13px;">
                                If you didn't expect this invitation, you can safely ignore this email.
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


async def send_invite_email(
    to_email: str,
    team_name: str,
    inviter_name: str,
    role: str,
    token: str,
) -> Optional[dict]:
    """
    Send a team invite email.
    Returns email response on success, None on failure.
    """
    invite_url = f"{APP_URL}/invite/accept?token={token}"
    
    html_content = get_invite_email_html(
        team_name=team_name,
        inviter_name=inviter_name,
        role=role,
        invite_url=invite_url,
    )
    
    return await send_email(
        to_email=to_email,
        subject=f"You've been invited to join {team_name} on {APP_NAME}",
        html_content=html_content,
    )
