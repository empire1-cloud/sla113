# Changelog

All notable changes to the Hybrid Intelligence Core project.

## [2.1.0] - 2026-02-09 (Phase D-Lite: Launch Polish)

### Added
- **Settings Sidebar** - Consistent navigation sidebar across all settings pages
- **System Status Banner** - Admin-only banner showing unconfigured external services
- **Loading States** - Reusable `PageLoading`, `LoadingState`, `InlineLoading` components
- **Empty States** - `EmptyState`, `NoAPIKeysFound`, `NoActivityFound`, `NoBillingData` components
- **Error Messages** - Standardized error handling with user-friendly messages
- **System Status API** - `GET /api/system/status` endpoint with service configuration status
- **Health Check API** - `GET /api/system/health` endpoint for uptime monitoring
- **API Caching** - 10-minute cache for `/api/billing/plans`, 1-minute cache for OAuth providers

### Changed
- Updated all settings pages to use consistent card styling
- Improved form validation with disabled states during submission
- Added mock mode banner to Billing page when Stripe not configured
- Enhanced toast notifications for success/error states

### Fixed
- Consistent breadcrumbs and page titles across settings
- Better loading state feedback on all data-fetching pages

---

## [2.0.0] - 2026-02-09 (Phase C-Lite: Minimal Governance)

### Added
- **Team Activity Log** - `GET /api/teams/{team_id}/activity` endpoint
- **Admin Overview** - `GET /api/admin/overview` endpoint (SystemAdmin only)
- **Admin Overview Page** - System stats dashboard at `/admin/overview`
- Navigation links for Billing and API Keys in user dropdown

---

## [1.9.0] - 2026-02-09 (Macro Phase B: Billing & Usage)

### Added
- **Stripe Billing Integration** - Checkout sessions, portal sessions, webhooks
- **Usage Tracking** - Execution limits by plan tier
- **API Key Management** - Create, list, revoke API keys with secure hashing
- **Billing Page** - `/billing` with plans, usage meters, upgrade buttons
- **API Keys Page** - `/settings/api-keys` with creation modal

---

## [1.8.0] - 2026-02-09 (Macro Phase A: Identity & Access)

### Added
- **Password Reset** - Token-based reset flow with email
- **OAuth 2.0** - Google and GitHub social login
- **Session Management** - List sessions, revoke individual/all sessions
- Enhanced security headers and password validation

---

## [1.7.0] - 2026-02-09 (Phase 7: Team Invitations)

### Added
- **Team Invitations** - Email-based invite system
- **Invite Modal** - UI for sending invites with role selection
- **Accept Invite Page** - Token validation and acceptance flow
- **Pending Invites List** - Manage and revoke pending invitations

---

## [1.6.0] - 2026-02-09 (Phase 6: Profile & RBAC)

### Added
- **Profile Page** - User settings, password change, session management
- **RoleGate Component** - Role-based UI visibility controls
- Removed legacy non-auth routes

---

## [1.5.0] - 2026-02-09 (Phase 5: Frontend Integration)

### Added
- **AuthContext** - Global authentication state management
- **ProtectedRoute** - Route guard for authenticated pages
- **AppHeader** - Global navigation with team switcher
- **TeamSwitcher** - Dropdown for switching teams
- Login and Signup pages with full validation

---

## [1.0.0 - 1.4.0] - 2026-02-09 (Foundation Phases)

### Added
- Multi-tenant database models (Users, Teams, Memberships)
- JWT authentication with access/refresh tokens
- Team creation and management
- 19 specialized AI engines
- Pipeline Composer with templates
- Execution History with team-scoping
- Analytics Dashboard with real-time charts
