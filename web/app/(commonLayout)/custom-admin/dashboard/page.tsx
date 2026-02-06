'use client'

/**
 * [CUSTOM] Admin dashboard page with summary statistics.
 *
 * Features:
 * - Welcome greeting with role badge
 * - Stat cards showing user and workspace counts
 * - Quick action links to Users and Workspaces pages
 */

import {
  RiGroupLine,
  RiProhibitedLine,
  RiTeamLine,
  RiUserLine,
} from '@remixicon/react'
import Link from 'next/link'
import { useTranslation } from 'react-i18next'
import { RoleBadge } from '@/app/components/custom/admin'
import StatCard from '@/app/components/custom/admin/dashboard/stat-card'
import { useAppContext } from '@/context/app-context'
import { useCurrentSystemRole } from '@/hooks/custom/use-custom-system-role'
import { useAdminDashboard } from '@/service/custom/admin-dashboard'
import { getSystemRoleLabel } from '@/utils/custom/admin-labels'

export default function DashboardPage() {
  const { t } = useTranslation()
  const { userProfile } = useAppContext()
  const { data: roleData } = useCurrentSystemRole()
  const { data: stats, isLoading } = useAdminDashboard()

  return (
    <div className="flex h-full flex-col">
      {/* Welcome Section */}
      <div className="mb-6">
        <h1 className="system-xl-semibold text-text-primary">
          {t('admin.welcomeBack', { ns: 'custom' })}
          ,
          {userProfile.name}
        </h1>
        <div className="mt-1 flex items-center gap-2">
          <RoleBadge role={roleData?.system_role || 'user'} label={getSystemRoleLabel(roleData?.system_role || 'user', t)} type="system" />
        </div>
      </div>

      {/* Stat Cards */}
      <div className="mb-8 grid grid-cols-2 gap-4 xl:grid-cols-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-[88px] animate-pulse rounded-xl border border-divider-subtle bg-background-default-subtle" />
            ))
          : (
              <>
                <StatCard
                  icon={<RiGroupLine className="size-5 text-util-colors-blue-brand-blue-brand-600" />}
                  iconClassName="bg-util-colors-blue-brand-blue-brand-50"
                  label={t('admin.totalUsersCount', { ns: 'custom' })}
                  value={stats?.total_users ?? 0}
                />
                <StatCard
                  icon={<RiUserLine className="size-5 text-util-colors-green-green-600" />}
                  iconClassName="bg-util-colors-green-green-50"
                  label={t('admin.activeUsersCount', { ns: 'custom' })}
                  value={stats?.active_users ?? 0}
                />
                <StatCard
                  icon={<RiProhibitedLine className="size-5 text-util-colors-orange-orange-600" />}
                  iconClassName="bg-util-colors-orange-orange-50"
                  label={t('admin.bannedUsersCount', { ns: 'custom' })}
                  value={stats?.banned_users ?? 0}
                />
                <StatCard
                  icon={<RiTeamLine className="size-5 text-util-colors-violet-violet-600" />}
                  iconClassName="bg-util-colors-violet-violet-50"
                  label={t('admin.totalWorkspacesCount', { ns: 'custom' })}
                  value={stats?.total_workspaces ?? 0}
                />
              </>
            )}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="system-md-semibold mb-3 text-text-primary">
          {t('admin.quickActions', { ns: 'custom' })}
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Link
            href="/custom-admin/users"
            className="flex items-center gap-3 rounded-xl border border-divider-subtle bg-components-panel-bg px-5 py-4 transition-colors hover:bg-state-base-hover"
          >
            <div className="flex size-9 items-center justify-center rounded-lg bg-util-colors-blue-brand-blue-brand-50">
              <RiGroupLine className="size-4 text-util-colors-blue-brand-blue-brand-600" />
            </div>
            <div>
              <div className="system-sm-medium text-text-secondary">
                {t('admin.userManagement', { ns: 'custom' })}
              </div>
              <div className="system-xs-regular text-text-tertiary">
                {t('admin.manageAccountsAndRoles', { ns: 'custom' })}
              </div>
            </div>
          </Link>

          <Link
            href="/custom-admin/workspaces"
            className="flex items-center gap-3 rounded-xl border border-divider-subtle bg-components-panel-bg px-5 py-4 transition-colors hover:bg-state-base-hover"
          >
            <div className="flex size-9 items-center justify-center rounded-lg bg-util-colors-violet-violet-50">
              <RiTeamLine className="size-4 text-util-colors-violet-violet-600" />
            </div>
            <div>
              <div className="system-sm-medium text-text-secondary">
                {t('admin.workspaceManagement', { ns: 'custom' })}
              </div>
              <div className="system-xs-regular text-text-tertiary">
                {t('admin.manageTeamsAndMembers', { ns: 'custom' })}
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  )
}
