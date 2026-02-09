/**
 * RoleGate Component
 * Conditionally renders children based on user's role
 */

import { useAuth } from '../context/AuthContext';

/**
 * RoleGate - Controls visibility based on team role
 * 
 * @param {string|string[]} allowedRoles - Role(s) that can see the content
 * @param {string} teamRole - 'owner' | 'admin' | 'member' - uses currentTeam role by default
 * @param {React.ReactNode} children - Content to conditionally render
 * @param {React.ReactNode} fallback - Optional content to show if role check fails
 */
export const TeamRoleGate = ({ 
  allowedRoles, 
  children, 
  fallback = null 
}) => {
  const { currentTeam } = useAuth();
  
  if (!currentTeam) return fallback;
  
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  const userRole = currentTeam.role;
  
  // Owner has all permissions
  if (userRole === 'owner') return children;
  
  // Check if user's role is in allowed roles
  if (roles.includes(userRole)) return children;
  
  return fallback;
};

/**
 * SystemRoleGate - Controls visibility based on system-wide role
 * 
 * @param {string|string[]} allowedRoles - System role(s) that can see the content
 * @param {React.ReactNode} children - Content to conditionally render
 * @param {React.ReactNode} fallback - Optional content to show if role check fails
 */
export const SystemRoleGate = ({ 
  allowedRoles, 
  children, 
  fallback = null 
}) => {
  const { user } = useAuth();
  
  if (!user) return fallback;
  
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  const systemRole = user.system_role || 'user';
  
  if (roles.includes(systemRole)) return children;
  
  return fallback;
};

/**
 * OwnerOnly - Shorthand for content only visible to team owners
 */
export const OwnerOnly = ({ children, fallback = null }) => (
  <TeamRoleGate allowedRoles={['owner']} fallback={fallback}>
    {children}
  </TeamRoleGate>
);

/**
 * AdminOnly - Shorthand for content visible to team admins and owners
 */
export const AdminOnly = ({ children, fallback = null }) => (
  <TeamRoleGate allowedRoles={['admin', 'owner']} fallback={fallback}>
    {children}
  </TeamRoleGate>
);

/**
 * SystemAdminOnly - Shorthand for content only visible to system admins
 */
export const SystemAdminOnly = ({ children, fallback = null }) => (
  <SystemRoleGate allowedRoles={['admin']} fallback={fallback}>
    {children}
  </SystemRoleGate>
);

export default TeamRoleGate;
