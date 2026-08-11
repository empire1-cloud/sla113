# Unified Login Credentials

## 🎯 One Login for All Universes

**IMPORTANT**: The Empire1 ecosystem uses a **unified authentication system**. This means:
- ✅ Create ONE account → access ALL universes
- ✅ Same email/password works across Empire1, SLA113, Lyrica3, and Arcade
- ✅ Login once → your session works everywhere
- ✅ Designed for solo builders with accessibility needs (one-hand operation friendly)

## Test Account (Development)

- **Email**: `newuser@example.com`
- **Password**: `NewPass123!`
- **Access**: All universes (Empire1, SLA113, Lyrica3, Arcade)

## Quick Access

### Empire 1 Dashboard
- **URL**: `/` or `/dashboard`
- **Auth Required**: Yes (login required)
- **Purpose**: Main creator dashboard, onboarding, billing, settings

### SLA113 Operator Dashboard  
- **URL**: `/sla113`
- **Auth Required**: No (publicly accessible for preview)
- **Note**: Full features require Empire1 login

### Lyrica 3 (Music Universe)
- **URL**: `/lyrica3` (future)
- **Auth Required**: Yes (uses same Empire1 login)
- **Credentials**: Same as above

### Arcade (Game Portal)
- **URL**: `/arcade` (future)
- **Auth Required**: Yes (uses same Empire1 login)
- **Credentials**: Same as above

## Creating Your Own Account

1. Navigate to `/signup` or click "Sign Up" on the login page
2. Enter your email and create a password (min 8 chars, requires uppercase, lowercase, number)
3. Your account is created across ALL universes automatically
4. Use the same credentials to access Empire1, Lyrica3, Arcade, etc.

## Password Management Tips

For solo builders with accessibility needs:
- 💡 Save credentials in your browser's password manager
- 💡 Use a password manager like 1Password, LastPass, or Bitwarden
- 💡 Enable browser auto-fill for one-click login
- 💡 The system keeps you logged in for 7 days with refresh tokens

## API Access

The same authentication system powers the API:
1. Login via `POST /api/auth/login` with email/password
2. Receive `access_token` (15 min) and `refresh_token` (7 days)
3. Use access token in `Authorization: Bearer {token}` header
4. Refresh token automatically before expiry

## Production Deployment

When deploying, you'll create your actual admin account:
```bash
# First user signup becomes the system admin
curl -X POST https://sla113.southernlifestyle.org/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "YourSecurePassword123!",
    "first_name": "Your",
    "last_name": "Name"
  }'
```

This account will work across all production universes automatically.
