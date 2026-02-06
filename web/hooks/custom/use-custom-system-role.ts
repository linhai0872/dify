/**
 * [CUSTOM] Hook for getting current user's system role for multi-workspace permission control.
 */

import type { SystemRole } from '@/models/custom/admin'
import { useQuery } from '@tanstack/react-query'
import { get } from '@/service/base'

const NAME_SPACE = 'custom'

type CurrentUserSystemRoleResponse = {
  system_role: SystemRole
  multi_workspace_permission_enabled: boolean
}

export const customQueryKeys = {
  currentSystemRole: [NAME_SPACE, 'current-system-role'] as const,
}

/**
 * Fetch current user's system role.
 * Returns 'user' if feature is disabled or request fails.
 */
export const useCurrentSystemRole = () => {
  return useQuery<CurrentUserSystemRoleResponse>({
    queryKey: customQueryKeys.currentSystemRole,
    queryFn: () => get<CurrentUserSystemRoleResponse>('/custom/me/system-role'),
    retry: false,
    // Fail silently - returns null if feature is disabled (404)
    throwOnError: false,
  })
}

/**
 * Hook to check if current user is a system admin.
 */
export const useIsSystemAdmin = () => {
  const { data, isLoading } = useCurrentSystemRole()

  return {
    isSystemAdmin: data?.system_role === 'system_admin',
    isFeatureEnabled: data?.multi_workspace_permission_enabled ?? false,
    isLoading,
  }
}

/**
 * Hook to check if current user is a super admin (alias for useIsSystemAdmin).
 * @deprecated Use useIsSystemAdmin instead
 */
export const useIsSuperAdmin = () => {
  const { isSystemAdmin, isFeatureEnabled, isLoading } = useIsSystemAdmin()

  return {
    isSuperAdmin: isSystemAdmin,
    isFeatureEnabled,
    isLoading,
  }
}

/**
 * Hook to check if current user is a tenant manager.
 */
export const useIsTenantManager = () => {
  const { data, isLoading } = useCurrentSystemRole()

  return {
    isTenantManager: data?.system_role === 'tenant_manager',
    isFeatureEnabled: data?.multi_workspace_permission_enabled ?? false,
    isLoading,
  }
}

/**
 * Hook to check if current user can create workspaces.
 * Both system_admin and tenant_manager can create workspaces.
 */
export const useCanCreateWorkspace = () => {
  const { data, isLoading } = useCurrentSystemRole()

  const canCreate = data?.system_role === 'system_admin' || data?.system_role === 'tenant_manager'

  return {
    canCreateWorkspace: canCreate,
    isFeatureEnabled: data?.multi_workspace_permission_enabled ?? false,
    isLoading,
  }
}
