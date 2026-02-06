/**
 * [CUSTOM] Type definitions for multi-workspace permission control admin features.
 */

/**
 * System-level role for multi-workspace permission control.
 * - system_admin: Can view all workspaces, manage all users, assign members to any workspace
 * - tenant_manager: Can create and manage own workspaces
 * - user: Default role, can only access joined workspaces
 */
export type SystemRole = 'system_admin' | 'tenant_manager' | 'user'

/**
 * Legacy system role names for backward compatibility.
 * @deprecated Use SystemRole instead
 */
export type LegacySystemRole = 'super_admin' | 'workspace_admin' | 'normal'

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
 * Workspace info in member list response.
 */
export type AdminWorkspaceInfo = {
  id: string
  name: string
  status: string
  created_at: number | string | null
}

/**
 * Workspace member list response.
 */
export type AdminMemberListResponse = {
  data: AdminMember[]
  total: number
  workspace: AdminWorkspaceInfo
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
  is_default?: boolean // Default (first created) workspace cannot be deleted
  created_by?: string // Creator user ID for tenant_manager permission check
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

/**
 * Create user request body.
 */
export type CreateUserRequest = {
  name: string
  email: string
  password: string
  system_role?: SystemRole
}

/**
 * Create workspace request body.
 */
export type CreateWorkspaceRequest = {
  name: string
  owner_id?: string
}

/**
 * Batch user action request body.
 */
export type BatchUserActionRequest = {
  user_ids: string[]
  action: 'enable' | 'disable' | 'delete'
}

/**
 * Batch action response.
 */
export type BatchActionResponse = {
  success: boolean
  processed: number
  failed: number
  errors?: Array<{ id: string, error: string }>
}
