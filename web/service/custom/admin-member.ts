/**
 * [CUSTOM] Admin workspace member management API service for multi-workspace permission control.
 */

import type { CommonResponse } from '@/models/common'
import type {
  AdminMemberListResponse,
  AdminWorkspaceListResponse,
  AvailableUsersResponse,
  WorkspaceRole,
  WorkspaceRoleOption,
} from '@/models/custom/admin'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { del, get, post, put } from '../base'

const NAME_SPACE = 'custom-admin'

export const customAdminMemberQueryKeys = {
  workspaces: (params?: { page?: number, limit?: number, search?: string }) =>
    [NAME_SPACE, 'workspaces', params] as const,
  members: (workspaceId: string) => [NAME_SPACE, 'workspace-members', workspaceId] as const,
  availableUsers: (workspaceId: string, search?: string) =>
    [NAME_SPACE, 'available-users', workspaceId, search] as const,
  workspaceRoles: [NAME_SPACE, 'workspace-roles'] as const,
}

/**
 * Fetch all workspaces for admin (with member count).
 */
export const useAdminWorkspaces = (params?: {
  page?: number
  limit?: number
  search?: string
}) => {
  return useQuery<AdminWorkspaceListResponse>({
    queryKey: customAdminMemberQueryKeys.workspaces(params),
    queryFn: () =>
      get<AdminWorkspaceListResponse>('/custom/admin/workspaces', {
        params: {
          page: params?.page || 1,
          limit: params?.limit || 20,
          search: params?.search || '',
        },
      }),
  })
}

/**
 * Fetch workspace members.
 */
export const useWorkspaceMembers = (workspaceId: string, enabled = true) => {
  return useQuery<AdminMemberListResponse>({
    queryKey: customAdminMemberQueryKeys.members(workspaceId),
    queryFn: () =>
      get<AdminMemberListResponse>(`/custom/admin/workspaces/${workspaceId}/members`),
    enabled: !!workspaceId && enabled,
  })
}

/**
 * Fetch available users that can be added to a workspace.
 */
export const useAvailableUsers = (workspaceId: string, search?: string, enabled = true) => {
  return useQuery<AvailableUsersResponse>({
    queryKey: customAdminMemberQueryKeys.availableUsers(workspaceId, search),
    queryFn: () =>
      get<AvailableUsersResponse>(`/custom/admin/workspaces/${workspaceId}/available-users`, {
        params: { search: search || '' },
      }),
    enabled: !!workspaceId && enabled,
  })
}

/**
 * Fetch available workspace roles.
 */
export const useWorkspaceRoles = () => {
  return useQuery<{ roles: WorkspaceRoleOption[] }>({
    queryKey: customAdminMemberQueryKeys.workspaceRoles,
    queryFn: () => get<{ roles: WorkspaceRoleOption[] }>('/custom/admin/workspace-roles'),
  })
}

/**
 * Add member to workspace.
 */
export const useAddWorkspaceMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      workspaceId,
      userId,
      role,
    }: {
      workspaceId: string
      userId: string
      role: WorkspaceRole
    }) =>
      post<CommonResponse>(`/custom/admin/workspaces/${workspaceId}/members`, {
        body: { user_id: userId, role },
      }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: customAdminMemberQueryKeys.members(variables.workspaceId),
      })
      queryClient.invalidateQueries({
        queryKey: [NAME_SPACE, 'available-users', variables.workspaceId],
      })
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'workspaces'] })
    },
  })
}

/**
 * Update member role in workspace.
 */
export const useUpdateMemberRole = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      workspaceId,
      userId,
      role,
    }: {
      workspaceId: string
      userId: string
      role: WorkspaceRole
    }) =>
      put<CommonResponse>(`/custom/admin/workspaces/${workspaceId}/members/${userId}`, {
        body: { role },
      }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: customAdminMemberQueryKeys.members(variables.workspaceId),
      })
    },
  })
}

/**
 * Remove member from workspace.
 */
export const useRemoveWorkspaceMember = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ workspaceId, userId }: { workspaceId: string, userId: string }) =>
      del<CommonResponse>(`/custom/admin/workspaces/${workspaceId}/members/${userId}`),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: customAdminMemberQueryKeys.members(variables.workspaceId),
      })
      queryClient.invalidateQueries({
        queryKey: [NAME_SPACE, 'available-users', variables.workspaceId],
      })
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'workspaces'] })
    },
  })
}

/**
 * Create a new workspace.
 */
export const useCreateWorkspace = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ name }: { name: string }) =>
      post<CommonResponse & { data: { id: string, name: string } }>('/custom/admin/workspaces', {
        body: { name },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'workspaces'] })
    },
  })
}

/**
 * Delete a workspace.
 */
export const useDeleteWorkspace = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ workspaceId }: { workspaceId: string }) =>
      del<CommonResponse>(`/custom/admin/workspaces/${workspaceId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [NAME_SPACE, 'workspaces'] })
    },
  })
}
