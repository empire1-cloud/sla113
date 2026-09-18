const ADMIN_TOKEN_KEY = 'admin_token'
const ADMIN_ROLE_KEY = 'admin_role'

export type Sla113Role = 'operator_standard' | 'operator_advanced' | 'executive' | 'engineer_platform'

export function getSla113AdminToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(ADMIN_TOKEN_KEY)
}

export function getSla113AdminRole(): Sla113Role {
  if (typeof window === 'undefined') return 'operator_advanced'
  const storedRole = localStorage.getItem(ADMIN_ROLE_KEY) as Sla113Role | null
  return storedRole || 'operator_advanced'
}

export function setSla113Session(token: string, role: Sla113Role): void {
  if (typeof window === 'undefined') return

  localStorage.setItem(ADMIN_TOKEN_KEY, token)
  localStorage.setItem(ADMIN_ROLE_KEY, role)

  const secure = window.location.protocol === 'https:' ? ';Secure' : ''
  document.cookie = `${ADMIN_TOKEN_KEY}=${encodeURIComponent(token)};Path=/;Max-Age=604800;SameSite=Lax${secure}`
  document.cookie = `${ADMIN_ROLE_KEY}=${encodeURIComponent(role)};Path=/;Max-Age=604800;SameSite=Lax${secure}`
}

export function clearSla113Session(): void {
  if (typeof window === 'undefined') return

  localStorage.removeItem(ADMIN_TOKEN_KEY)
  localStorage.removeItem(ADMIN_ROLE_KEY)

  document.cookie = `${ADMIN_TOKEN_KEY}=;Path=/;Max-Age=0;SameSite=Lax`
  document.cookie = `${ADMIN_ROLE_KEY}=;Path=/;Max-Age=0;SameSite=Lax`
}

export function getSla113AdminHeaders(): HeadersInit {
  const token = getSla113AdminToken()
  const role = getSla113AdminRole()

  return {
    'Content-Type': 'application/json',
    ...(token ? { 'X-SLA113-Key': token } : {}),
    'X-SLA113-Role': role,
  }
}