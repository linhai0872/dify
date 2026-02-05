'use client'

/**
 * [CUSTOM] User management page for multi-workspace permission control.
 *
 * Features:
 * - List all users with pagination
 * - Search users by name or email
 * - Filter by system role and status
 * - Modify user system role
 * - Enable/disable user accounts
 */

import type { RoleOption } from '@/app/components/custom/admin'
import type { SystemRole, UserStatus } from '@/models/custom/admin'
import {
  RiGroupLine,
  RiLoader4Line,
} from '@remixicon/react'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Avatar from '@/app/components/base/avatar'
import Button from '@/app/components/base/button'
import Pagination from '@/app/components/base/pagination'
import SearchInput from '@/app/components/base/search-input'
import { PortalSelect } from '@/app/components/base/select'
import { AdminPageHeader, RoleBadge, RoleOperation } from '@/app/components/custom/admin'
import { useAdminUsers, useSystemRoles, useUpdateUserStatus, useUpdateUserSystemRole } from '@/service/custom/admin-user'

// Status badge colors
const statusColors: Record<string, { bg: string, text: string }> = {
  active: { bg: 'bg-util-colors-green-green-50', text: 'text-util-colors-green-green-600' },
  pending: { bg: 'bg-util-colors-warning-warning-50', text: 'text-util-colors-warning-warning-600' },
  banned: { bg: 'bg-util-colors-red-red-50', text: 'text-util-colors-red-red-600' },
  closed: { bg: 'bg-components-badge-bg-gray', text: 'text-text-tertiary' },
}

export default function UsersPage() {
  const { t } = useTranslation()
  const [page, setPage] = useState(0) // Pagination component uses 0-indexed
  const [limit, setLimit] = useState(10)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data: usersData, isLoading } = useAdminUsers({
    page: page + 1, // API uses 1-indexed
    limit,
    search,
    system_role: roleFilter,
    status: statusFilter,
  })
  const { data: rolesData } = useSystemRoles()
  const { mutate: updateRole, isPending: isUpdatingRole } = useUpdateUserSystemRole()
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateUserStatus()

  const handleRoleChange = (userId: string, role: SystemRole) => {
    updateRole({ userId, role })
  }

  const handleStatusToggle = (userId: string, currentStatus: UserStatus) => {
    const newStatus = currentStatus === 'active' ? 'banned' : 'active'
    updateStatus({ userId, status: newStatus })
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'super_admin':
        return t('systemRole.superAdmin', { ns: 'custom' })
      case 'workspace_admin':
        return t('systemRole.workspaceAdmin', { ns: 'custom' })
      default:
        return t('systemRole.normal', { ns: 'custom' })
    }
  }

  const getRoleTip = (role: string) => {
    switch (role) {
      case 'super_admin':
        return t('systemRole.superAdminTip', { ns: 'custom' })
      case 'workspace_admin':
        return t('systemRole.workspaceAdminTip', { ns: 'custom' })
      default:
        return t('systemRole.normalTip', { ns: 'custom' })
    }
  }

  const getStatusLabel = (status: string) => {
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

  // Build role options for dropdown with descriptions
  const systemRolesWithTips: RoleOption[] = useMemo(() => {
    return (rolesData?.roles || []).map(role => ({
      value: role.value,
      label: getRoleLabel(role.value),
      description: getRoleTip(role.value),
    }))
  }, [rolesData?.roles, t])

  // Build filter options for PortalSelect
  const roleFilterOptions = useMemo(() => {
    const options = [{ value: '', name: t('admin.allRoles', { ns: 'custom' }) }]
    rolesData?.roles?.forEach((role) => {
      options.push({ value: role.value, name: getRoleLabel(role.value) })
    })
    return options
  }, [rolesData?.roles, t])

  const statusFilterOptions = useMemo(() => [
    { value: '', name: t('admin.allStatus', { ns: 'custom' }) },
    { value: 'active', name: t('admin.statusActive', { ns: 'custom' }) },
    { value: 'pending', name: t('admin.statusPending', { ns: 'custom' }) },
    { value: 'banned', name: t('admin.statusBanned', { ns: 'custom' }) },
  ], [t])

  return (
    <div className="flex h-full flex-col">
      {/* Header Card */}
      <AdminPageHeader
        icon={<RiGroupLine className="h-6 w-6" />}
        title={t('admin.userManagement', { ns: 'custom' })}
        subtitle={t('admin.totalUsers', { ns: 'custom', count: usersData?.total || 0 })}
      />

      {/* Filters */}
      <div className="mb-4 flex flex-wrap items-center gap-3">
        {/* Search */}
        <SearchInput
          className="min-w-[200px] max-w-[400px] flex-1"
          placeholder={t('admin.searchPlaceholder', { ns: 'custom' })}
          value={search}
          onChange={setSearch}
        />

        {/* Role Filter */}
        <PortalSelect
          value={roleFilter}
          items={roleFilterOptions}
          onSelect={item => setRoleFilter(item.value as string)}
          popupClassName="w-[180px]"
        />

        {/* Status Filter */}
        <PortalSelect
          value={statusFilter}
          items={statusFilterOptions}
          onSelect={item => setStatusFilter(item.value as string)}
          popupClassName="w-[140px]"
        />
      </div>

      {/* Users Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-divider-subtle bg-components-panel-bg">
        {/* Table Header */}
        <div className="flex min-w-[800px] items-center border-b border-divider-regular bg-background-section-burn py-[7px]">
          <div className="system-xs-medium-uppercase grow px-4 text-text-tertiary">
            {t('admin.user', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[140px] shrink-0 px-3 text-text-tertiary">
            {t('admin.systemRole', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[100px] shrink-0 px-3 text-text-tertiary">
            {t('admin.status', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[120px] shrink-0 px-3 text-text-tertiary">
            {t('admin.workspaces', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[104px] shrink-0 text-text-tertiary">
            {t('admin.lastActive', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[100px] shrink-0 px-3 text-text-tertiary">
            {t('admin.actions', { ns: 'custom' })}
          </div>
        </div>

        {/* Table Body */}
        <div className="min-w-[800px]">
          {isLoading
            ? (
                <div className="flex items-center justify-center py-12">
                  <RiLoader4Line className="h-6 w-6 animate-spin text-text-tertiary" />
                </div>
              )
            : usersData?.data?.length === 0
              ? (
                  <div className="system-sm-regular py-12 text-center text-text-tertiary">
                    {t('admin.noUsersFound', { ns: 'custom' })}
                  </div>
                )
              : (
                  usersData?.data?.map(user => (
                    <div key={user.id} className="flex border-b border-divider-subtle transition-colors hover:bg-state-base-hover">
                      {/* User Info */}
                      <div className="flex grow items-center px-4 py-2">
                        <Avatar avatar={user.avatar_url} name={user.name} size={32} className="mr-3" />
                        <div className="min-w-0">
                          <div className="system-sm-medium truncate text-text-secondary">
                            {user.name}
                          </div>
                          <div className="system-xs-regular truncate text-text-tertiary">
                            {user.email}
                          </div>
                        </div>
                      </div>

                      {/* System Role */}
                      <div className="flex w-[140px] shrink-0 items-center">
                        <RoleOperation
                          currentRole={user.system_role}
                          roles={systemRolesWithTips}
                          onRoleChange={role => handleRoleChange(user.id, role as SystemRole)}
                          disabled={isUpdatingRole}
                        />
                      </div>

                      {/* Status */}
                      <div className="flex w-[100px] shrink-0 items-center px-3">
                        <RoleBadge
                          role={user.status}
                          label={getStatusLabel(user.status)}
                          type="system"
                          className={`${statusColors[user.status]?.bg || ''} ${statusColors[user.status]?.text || ''}`}
                        />
                      </div>

                      {/* Workspaces */}
                      <div className="flex w-[120px] shrink-0 items-center px-3">
                        <span className="system-sm-regular text-text-secondary">
                          {t('admin.workspaceCount', { ns: 'custom', count: user.workspaces?.length || 0 })}
                        </span>
                      </div>

                      {/* Last Active */}
                      <div className="flex w-[104px] shrink-0 items-center">
                        <span className="system-sm-regular text-text-tertiary">
                          {user.last_active_at
                            ? new Date(user.last_active_at * 1000).toLocaleDateString()
                            : '-'}
                        </span>
                      </div>

                      {/* Actions */}
                      <div className="flex w-[100px] shrink-0 items-center px-3">
                        <Button
                          variant={user.status === 'active' ? 'warning' : 'primary'}
                          size="small"
                          onClick={() => handleStatusToggle(user.id, user.status)}
                          disabled={isUpdatingStatus}
                        >
                          {user.status === 'active'
                            ? t('admin.disable', { ns: 'custom' })
                            : t('admin.enable', { ns: 'custom' })}
                        </Button>
                      </div>
                    </div>
                  ))
                )}
        </div>
      </div>

      {/* Pagination */}
      {usersData && usersData.total > limit && (
        <Pagination
          className="mt-4"
          current={page}
          onChange={setPage}
          total={usersData.total}
          limit={limit}
          onLimitChange={setLimit}
        />
      )}
    </div>
  )
}
