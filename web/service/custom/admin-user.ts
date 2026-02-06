/**
 * [CUSTOM] Admin user management API service for multi-workspace permission control.
 */

import type { CommonResponse } from '@/models/common'
import type {
  AdminUserDetailResponse,
  AdminUserListResponse,
  CustomFeatureFlagsResponse,
  SystemRole,
  SystemRoleOption,
} from '@/models/custom/admin'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { del, get, post, put } from '../base'

const NAME_SPACE = 'custom-admin'

export const customAdminQueryKeys = {
  featureFlags: [NAME_SPACE, 'feature-flags'] as const,
  users: (params?: { page?: number, limit?: number, search?: string, system_role?: string, status?: string }) =>
    [NAME_SPACE, 'users', params] as const,
  user: (userId: string) => [NAME_SPACE, 'user', userId] as const,
  systemRoles: [NAME_SPACE, 'system-roles'] as const,
}

/**
 * Fetch custom feature flags.
 */
export const useCustomFeatureFlags = () => {
  return useQuery<CustomFeatureFlagsResponse>({
    queryKey: customAdminQueryKeys.featureFlags,
    queryFn: () => get<CustomFeatureFlagsResponse>('/custom/feature-flags'),
  })
}

/**
 * Fetch admin user list with pagination and filters.
 */
export const useAdminUsers = (params?: {
  page?: number
  limit?: number
  search?: string
  system_role?: string
  status?: string
}) => {
  return useQuery<AdminUserListResponse>({
    queryKey: customAdminQueryKeys.users(params),
    queryFn: () =>
      get<AdminUserListResponse>('/custom/admin/users', {
        params: {
          page: params?.page || 1,
          limit: params?.limit || 20,
          search: params?.search || '',
          system_role: params?.system_role || '',
          status: params?.status || '',
        },
      }),
  })
}

/**
 * Fetch admin user detail.
 */
export const useAdminUser = (userId: string, enabled = true) => {
  return useQuery<AdminUserDetailResponse>({
    queryKey: customAdminQueryKeys.user(userId),
    queryFn: () => get<AdminUserDetailResponse>(`/custom/admin/users/${userId}`),
    enabled: !!userId && enabled,
  })
}

/**
 * Fetch available system roles.
 */
export const useSystemRoles = () => {
  return useQuery<{ roles: SystemRoleOption[] }>({
    queryKey: customAdminQueryKeys.systemRoles,
    queryFn: () => get<{ roles: SystemRoleOption[] }>('/custom/admin/system-roles'),
  })
}

/**
 * Create a new user account.
 */
export const useCreateUser = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      name,
      email,
      password,
      systemRole,
    }: {
      name: string
      email: string
      password: string
      systemRole?: SystemRole
    }) =>
      post<CommonResponse & { data: { id: string, name: string, email: string } }>(
        '/custom/admin/users',
        {
          body: {
            name,
            email,
            password,
            system_role: systemRole || 'user',
          },
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'users'] })
    },
  })
}

/**
 * Update user system role.
 */
export const useUpdateUserSystemRole = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, role }: { userId: string, role: SystemRole }) =>
      put<CommonResponse>(`/custom/admin/users/${userId}/role`, { body: { system_role: role } }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'users'] })
      queryClient.invalidateQueries({
        queryKey: customAdminQueryKeys.user(variables.userId),
      })
    },
  })
}

/**
 * Update user status (active/banned).
 */
export const useUpdateUserStatus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ userId, status }: { userId: string, status: 'active' | 'banned' }) =>
      put<CommonResponse>(`/custom/admin/users/${userId}/status`, { body: { status } }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'users'] })
      queryClient.invalidateQueries({
        queryKey: customAdminQueryKeys.user(variables.userId),
      })
    },
  })
}

/**
 * Delete user account.
 */
export const useDeleteUser = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (userId: string) => del<CommonResponse>(`/custom/admin/users/${userId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'users'] })
    },
  })
}

/**
 * Batch action on users (enable/disable/delete).
 */
export const useBatchUserAction = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      userIds,
      action,
    }: {
      userIds: string[]
      action: 'enable' | 'disable' | 'delete'
    }) =>
      post<CommonResponse & { processed: number, failed: number, errors: Array<{ id: string, error: string }> }>(
        '/custom/admin/users/batch',
        {
          body: {
            user_ids: userIds,
            action,
          },
        },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'users'] })
    },
  })
}
