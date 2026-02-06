/**
 * [CUSTOM] Shared label utilities for admin role and status display.
 *
 * Eliminates duplicate label functions across users and members pages.
 */

import type { TFunction } from 'i18next'

export const getSystemRoleLabel = (role: string, t: TFunction): string => {
  switch (role) {
    case 'system_admin':
    case 'super_admin':
      return t('admin.systemRoleSystemAdmin', { ns: 'custom' })
    case 'tenant_manager':
    case 'workspace_admin':
      return t('admin.systemRoleTenantManager', { ns: 'custom' })
    case 'user':
    case 'normal':
    default:
      return t('admin.systemRoleUser', { ns: 'custom' })
  }
}

export const getSystemRoleTip = (role: string, t: TFunction): string => {
  switch (role) {
    case 'system_admin':
    case 'super_admin':
      return t('admin.systemRoleSystemAdminTip', { ns: 'custom' })
    case 'tenant_manager':
    case 'workspace_admin':
      return t('admin.systemRoleTenantManagerTip', { ns: 'custom' })
    case 'user':
    case 'normal':
    default:
      return t('admin.systemRoleUserTip', { ns: 'custom' })
  }
}

export const getWorkspaceRoleLabel = (role: string, t: TFunction): string => {
  switch (role) {
    case 'owner':
      return t('admin.workspaceRole.owner', { ns: 'custom' })
    case 'admin':
      return t('admin.workspaceRole.admin', { ns: 'custom' })
    case 'editor':
      return t('admin.workspaceRole.editor', { ns: 'custom' })
    case 'normal':
      return t('admin.workspaceRole.normal', { ns: 'custom' })
    case 'dataset_operator':
      return t('admin.workspaceRole.datasetOperator', { ns: 'custom' })
    default:
      return role
  }
}

export const getWorkspaceRoleTip = (role: string, t: TFunction): string => {
  switch (role) {
    case 'owner':
      return t('admin.workspaceRole.ownerTip', { ns: 'custom' })
    case 'admin':
      return t('admin.workspaceRole.adminTip', { ns: 'custom' })
    case 'editor':
      return t('admin.workspaceRole.editorTip', { ns: 'custom' })
    case 'normal':
      return t('admin.workspaceRole.normalTip', { ns: 'custom' })
    case 'dataset_operator':
      return t('admin.workspaceRole.datasetOperatorTip', { ns: 'custom' })
    default:
      return ''
  }
}

export const getStatusLabel = (status: string, t: TFunction): string => {
  switch (status) {
    case 'active':
      return t('admin.statusActive', { ns: 'custom' })
    case 'pending':
      return t('admin.statusPending', { ns: 'custom' })
    case 'banned':
      return t('admin.statusBanned', { ns: 'custom' })
    default:
      return status
  }
}
