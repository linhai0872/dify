/**
 * [CUSTOM] Hook for admin permission validation in multi-workspace permission control.
 *
 * Provides methods to check if the current user can perform admin actions
 * on other users, with localized reason messages when actions are disabled.
 */

import type { SystemRole, UserStatus } from '@/models/custom/admin'
import { useCallback, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { useAppContext } from '@/context/app-context'
import { useCurrentSystemRole } from './use-custom-system-role'

export type PermissionCheckResult = {
  allowed: boolean
  reason?: string
}

/**
 * Hook providing admin permission validation methods.
 *
 * Rules:
 * - Cannot demote yourself (any role)
 * - Cannot demote other system_admin via UI (requires CLI)
 * - Cannot disable yourself
 * - Cannot disable other system_admin
 */
export const useAdminPermissions = () => {
  const { t } = useTranslation()
  const { userProfile } = useAppContext()
  const { data: roleData } = useCurrentSystemRole()

  const currentUserId = userProfile.id
  const currentRole = roleData?.system_role

  /**
   * Check if current user can change another user's system role.
   */
  const canChangeRole = useCallback((
    targetUserId: string,
    targetRole: SystemRole,
    newRole: SystemRole,
  ): PermissionCheckResult => {
    // Cannot change own role
    if (targetUserId === currentUserId) {
      return {
        allowed: false,
        reason: t('admin.cannotDemoteSelf', { ns: 'custom' }),
      }
    }

    // Cannot demote system_admin via UI
    if (targetRole === 'system_admin' && newRole !== 'system_admin') {
      return {
        allowed: false,
        reason: t('admin.cannotDemoteSystemAdmin', { ns: 'custom' }),
      }
    }

    return { allowed: true }
  }, [currentUserId, t])

  /**
   * Check if current user can change another user's status.
   */
  const canChangeStatus = useCallback((
    targetUserId: string,
    targetRole: SystemRole,
    newStatus: UserStatus,
  ): PermissionCheckResult => {
    // Cannot disable yourself
    if (targetUserId === currentUserId && newStatus === 'banned') {
      return {
        allowed: false,
        reason: t('admin.cannotDisableSelf', { ns: 'custom' }),
      }
    }

    // Cannot disable system_admin
    if (targetRole === 'system_admin' && newStatus === 'banned') {
      return {
        allowed: false,
        reason: t('admin.cannotDisableSystemAdmin', { ns: 'custom' }),
      }
    }

    return { allowed: true }
  }, [currentUserId, t])

  /**
   * Check if current user can delete another user.
   */
  const canDeleteUser = useCallback((
    targetUserId: string,
    targetRole: SystemRole,
  ): PermissionCheckResult => {
    // Cannot delete yourself
    if (targetUserId === currentUserId) {
      return {
        allowed: false,
        reason: t('admin.cannotDeleteSelf', { ns: 'custom' }),
      }
    }

    // Cannot delete system_admin via UI
    if (targetRole === 'system_admin') {
      return {
        allowed: false,
        reason: t('admin.cannotDeleteSystemAdmin', { ns: 'custom' }),
      }
    }

    return { allowed: true }
  }, [currentUserId, t])

  /**
   * Check if the role dropdown should show a specific role as disabled.
   * Returns the reason if disabled, undefined if allowed.
   */
  const getRoleOptionDisabledReason = useCallback((
    targetUserId: string,
    targetRole: SystemRole,
    optionRole: SystemRole,
  ): string | undefined => {
    // If target is self, all options are disabled
    if (targetUserId === currentUserId) {
      return t('admin.cannotDemoteSelf', { ns: 'custom' })
    }

    // If target is system_admin and option is not system_admin, disable it
    if (targetRole === 'system_admin' && optionRole !== 'system_admin') {
      return t('admin.cannotDemoteSystemAdmin', { ns: 'custom' })
    }

    return undefined
  }, [currentUserId, t])

  /**
   * Check if current user is the target user.
   */
  const isSelf = useCallback((targetUserId: string): boolean => {
    return targetUserId === currentUserId
  }, [currentUserId])

  /**
   * Check if target user is a system admin.
   */
  const isTargetSystemAdmin = useCallback((targetRole: SystemRole): boolean => {
    return targetRole === 'system_admin'
  }, [])

  /**
   * Check if current user can access the admin panel.
   * Both system_admin and tenant_manager have access.
   */
  const canAccessAdminPanel = currentRole === 'system_admin' || currentRole === 'tenant_manager'

  /**
   * Check if current user can manage users (system_admin only).
   */
  const canManageUsers = currentRole === 'system_admin'

  return useMemo(() => ({
    currentUserId,
    currentRole,
    canChangeRole,
    canChangeStatus,
    canDeleteUser,
    getRoleOptionDisabledReason,
    isSelf,
    isTargetSystemAdmin,
    canAccessAdminPanel,
    canManageUsers,
  }), [
    currentUserId,
    currentRole,
    canChangeRole,
    canChangeStatus,
    canDeleteUser,
    getRoleOptionDisabledReason,
    isSelf,
    isTargetSystemAdmin,
    canAccessAdminPanel,
    canManageUsers,
  ])
}
