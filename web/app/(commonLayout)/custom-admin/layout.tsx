'use client'

/**
 * [CUSTOM] Admin layout for multi-workspace permission control.
 *
 * Provides:
 * - Permission guard (redirect non-admin users)
 * - Enhanced left sidebar navigation with icons and descriptions
 * - Dashboard, Users, and Workspaces nav items
 * - Conditional nav rendering for tenant_manager
 * - Current user info at sidebar bottom
 */

import type { ReactNode } from 'react'
import {
  RiDashboardLine,
  RiGroupLine,
  RiShieldLine,
  RiTeamLine,
} from '@remixicon/react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import Avatar from '@/app/components/base/avatar'
import { RoleBadge } from '@/app/components/custom/admin'
import { useAppContext } from '@/context/app-context'
import { useCurrentSystemRole, useIsSystemAdmin, useIsTenantManager } from '@/hooks/custom/use-custom-system-role'
import { cn } from '@/utils/classnames'
import { getSystemRoleLabel } from '@/utils/custom/admin-labels'

type AdminLayoutProps = {
  children: ReactNode
}

const allNavItems = [
  {
    key: 'dashboard',
    href: '/custom-admin/dashboard',
    icon: RiDashboardLine,
    labelKey: 'admin.overview' as const,
    descKey: 'admin.dashboard' as const,
    requiredRole: 'system_admin' as const,
  },
  {
    key: 'users',
    href: '/custom-admin/users',
    icon: RiGroupLine,
    labelKey: 'admin.userManagement' as const,
    descKey: 'admin.manageAccountsAndRoles' as const,
    requiredRole: 'system_admin' as const,
  },
  {
    key: 'workspaces',
    href: '/custom-admin/workspaces',
    icon: RiTeamLine,
    labelKey: 'admin.workspaceManagement' as const,
    descKey: 'admin.manageTeamsAndMembers' as const,
    requiredRole: 'any' as const,
  },
] as const

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()
  const { userProfile } = useAppContext()
  const { isSystemAdmin, isFeatureEnabled, isLoading: isLoadingAdmin } = useIsSystemAdmin()
  const { isTenantManager, isLoading: isLoadingTM } = useIsTenantManager()
  const { data: roleData } = useCurrentSystemRole()

  const isLoading = isLoadingAdmin || isLoadingTM
  const canAccess = isSystemAdmin || isTenantManager

  // Permission guard: redirect users without admin access
  useEffect(() => {
    if (!isLoading && (!isFeatureEnabled || !canAccess))
      router.replace('/apps')
  }, [isLoading, isFeatureEnabled, canAccess, router])

  // Filter nav items based on role
  const navItems = useMemo(() => {
    return allNavItems.filter((item) => {
      if (item.requiredRole === 'any')
        return true
      if (item.requiredRole === 'system_admin')
        return isSystemAdmin
      return false
    })
  }, [isSystemAdmin])

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-text-tertiary">{t('loading', { ns: 'common' })}</div>
      </div>
    )
  }

  if (!isFeatureEnabled || !canAccess)
    return null

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <aside className="flex w-56 shrink-0 flex-col border-r border-divider-subtle bg-background-default-subtle">
        {/* Header */}
        <div className="flex items-center gap-2 px-4 py-4">
          <div className="flex size-8 items-center justify-center rounded-lg bg-util-colors-blue-brand-blue-brand-50">
            <RiShieldLine className="size-4 text-util-colors-blue-brand-blue-brand-600" />
          </div>
          <div>
            <h1 className="system-md-semibold text-text-primary">
              {t('admin.systemAdmin', { ns: 'custom' })}
            </h1>
          </div>
        </div>

        <div className="mx-3 border-b border-divider-subtle" />

        {/* Navigation */}
        <nav className="flex-1 px-2 py-3">
          <div className="space-y-0.5">
            {navItems.map(item => (
              <Link
                key={item.key}
                href={item.href}
                className={cn(
                  'group flex items-start gap-2.5 rounded-lg px-3 py-2 transition-colors',
                  'hover:bg-state-base-hover',
                  pathname.startsWith(item.href)
                    ? 'border-l-2 border-util-colors-blue-brand-blue-brand-600 bg-state-accent-active'
                    : 'border-l-2 border-transparent',
                )}
              >
                <item.icon className={cn(
                  'mt-0.5 size-4 shrink-0',
                  pathname.startsWith(item.href) ? 'text-util-colors-blue-brand-blue-brand-600' : 'text-text-tertiary',
                )}
                />
                <div className="min-w-0">
                  <span className={cn(
                    'system-sm-medium block',
                    pathname.startsWith(item.href) ? 'text-text-primary' : 'text-text-secondary',
                  )}
                  >
                    {t(item.labelKey, { ns: 'custom' })}
                  </span>
                  <span className="system-xs-regular block text-text-quaternary">
                    {t(item.descKey, { ns: 'custom' })}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </nav>

        {/* Current User Info */}
        <div className="border-t border-divider-subtle px-3 py-3">
          <div className="flex items-center gap-2">
            <Avatar avatar={userProfile.avatar_url} name={userProfile.name} size={28} />
            <div className="min-w-0 flex-1">
              <div className="system-xs-medium truncate text-text-secondary">{userProfile.name}</div>
              <RoleBadge role={roleData?.system_role || 'user'} label={getSystemRoleLabel(roleData?.system_role || 'user', t)} type="system" />
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-background-body p-6">
        {children}
      </main>
    </div>
  )
}
