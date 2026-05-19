import type { TFunction } from 'i18next'

export function getSystemRoleLabel(role: string, t: TFunction): string {
  const labels: Record<string, string> = {
    system_admin: t('admin.systemRoleSystemAdmin', { ns: 'custom', defaultValue: 'System Admin' }),
    tenant_manager: t('admin.systemRoleTenantManager', { ns: 'custom', defaultValue: 'Tenant Manager' }),
    user: t('admin.systemRoleUser', { ns: 'custom', defaultValue: 'User' }),
  }
  return labels[role] ?? role
}

export function getStatusLabel(status: string, t: TFunction): string {
  const labels: Record<string, string> = {
    active: t('admin.statusActive', { ns: 'custom', defaultValue: 'Active' }),
    pending: t('admin.statusPending', { ns: 'custom', defaultValue: 'Pending' }),
    banned: t('admin.statusBanned', { ns: 'custom', defaultValue: 'Banned' }),
    closed: t('admin.statusClosed', { ns: 'custom', defaultValue: 'Closed' }),
  }
  return labels[status] ?? status
}
