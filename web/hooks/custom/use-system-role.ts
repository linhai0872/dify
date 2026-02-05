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
 * Returns 'normal' if feature is disabled or request fails.
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
 * Hook to check if current user is a super admin.
 */
export const useIsSuperAdmin = () => {
  const { data, isLoading } = useCurrentSystemRole()

  return {
    isSuperAdmin: data?.system_role === 'super_admin',
    isFeatureEnabled: data?.multi_workspace_permission_enabled ?? false,
    isLoading,
  }
}
