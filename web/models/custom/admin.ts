/**
 * [CUSTOM] Type definitions for multi-workspace permission control admin features.
 */

/**
 * System-level role for multi-workspace permission control.
 * - super_admin: Can view all workspaces, manage all users, assign members to any workspace
 * - workspace_admin: Reserved for future use (currently same as normal)
 * - normal: Default role, can only access joined workspaces
 */
export type SystemRole = 'super_admin' | 'workspace_admin' | 'normal'

/**
 * Workspace-level role.
 */
export type WorkspaceRole = 'owner' | 'admin' | 'editor' | 'normal' | 'dataset_operator'

/**
 * User status.
 */
export type UserStatus = 'active' | 'pending' | 'banned' | 'closed'

/**
 * Workspace info for admin user detail.
 */
export type AdminUserWorkspace = {
  id: string
  name: string
  role: WorkspaceRole
  created_at: number
}

/**
 * Admin user representation for user management.
 */
export type AdminUser = {
  id: string
  name: string
  email: string
  avatar_url: string | null
  system_role: SystemRole
  status: UserStatus
  created_at: number
  last_login_at: number | null
  last_active_at: number | null
  workspaces: AdminUserWorkspace[]
}

/**
 * Paginated admin user list response.
 */
export type AdminUserListResponse = {
  data: AdminUser[]
  total: number
  page: number
  limit: number
}

/**
 * Admin user detail response.
 */
export type AdminUserDetailResponse = AdminUser

/**
 * Workspace member representation for member management.
 */
export type AdminMember = {
  id: string
  name: string
  email: string
  avatar_url: string | null
  role: WorkspaceRole
  status: UserStatus
  joined_at: number
  last_active_at: number | null
}

/**
 * Workspace member list response.
 */
export type AdminMemberListResponse = {
  data: AdminMember[]
  total: number
  workspace_name?: string
}

/**
 * Available user for adding to workspace.
 */
export type AvailableUser = {
  id: string
  name: string
  email: string
  avatar_url: string | null
}

/**
 * Available users response.
 */
export type AvailableUsersResponse = {
  data: AvailableUser[]
  total: number
}

/**
 * System role option for role selection.
 */
export type SystemRoleOption = {
  value: SystemRole
  label: string
  description: string
}

/**
 * Workspace role option for role selection.
 */
export type WorkspaceRoleOption = {
  value: WorkspaceRole
  label: string
  description: string
}

/**
 * Workspace info for admin workspace list.
 */
export type AdminWorkspace = {
  id: string
  name: string
  plan: string
  status: string
  created_at: number
  member_count: number
}

/**
 * Admin workspace list response.
 */
export type AdminWorkspaceListResponse = {
  data: AdminWorkspace[]
  total: number
}

/**
 * Feature flags response from API.
 */
export type CustomFeatureFlagsResponse = {
  multi_workspace_permission_enabled: boolean
}
