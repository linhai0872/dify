'use client'

/**
 * [CUSTOM] User management page for multi-workspace permission control.
 *
 * Features:
 * - List all users with pagination
 * - Search users by name or email (debounced)
 * - Filter by system role and status
 * - Modify user system role
 * - Enable/disable user accounts
 * - Batch operations with toast feedback
 */

import type { RoleOption } from '@/app/components/custom/admin'
import type { AdminUser, SystemRole, UserStatus } from '@/models/custom/admin'
import {
  RiAddLine,
  RiGroupLine,
} from '@remixicon/react'
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import Checkbox from '@/app/components/base/checkbox'
import Confirm from '@/app/components/base/confirm'
import Pagination from '@/app/components/base/pagination'
import Toast from '@/app/components/base/toast'
import { AdminEmptyState, AdminPageHeader, AdminTableSkeleton, BatchActionBar } from '@/app/components/custom/admin'
import CreateUserModal from '@/app/components/custom/admin/users/create-user-modal'
import UserConfirmDialogs from '@/app/components/custom/admin/users/user-confirm-dialogs'
import UserFilters from '@/app/components/custom/admin/users/user-filters'
import UserTableRow from '@/app/components/custom/admin/users/user-table-row'
import { useAdminPermissions } from '@/hooks/custom/use-custom-admin-permissions'
import { useDebouncedValue } from '@/hooks/custom/use-custom-debounced-value'
import { useAdminUsers, useBatchUserAction, useCreateUser, useDeleteUser, useSystemRoles, useUpdateUserStatus, useUpdateUserSystemRole } from '@/service/custom/admin-user'
import { getSystemRoleLabel, getSystemRoleTip } from '@/utils/custom/admin-labels'

export default function UsersPage() {
  const { t } = useTranslation()
  const [page, setPage] = useState(0)
  const [limit, setLimit] = useState(10)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const debouncedSearch = useDebouncedValue(search, 300)

  // Confirmation dialog state
  const [showStatusConfirm, setShowStatusConfirm] = useState(false)
  const [userToToggle, setUserToToggle] = useState<{ id: string, name: string, status: UserStatus } | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [userToDelete, setUserToDelete] = useState<{ id: string, name: string } | null>(null)
  const [showRoleConfirm, setShowRoleConfirm] = useState(false)
  const [pendingRoleChange, setPendingRoleChange] = useState<{ userId: string, name: string, from: SystemRole, to: SystemRole } | null>(null)

  // Batch selection state
  const [selectedUserIds, setSelectedUserIds] = useState<Set<string>>(new Set())
  const [showBatchConfirm, setShowBatchConfirm] = useState(false)
  const [batchAction, setBatchAction] = useState<'enable' | 'disable' | 'delete' | null>(null)

  const { data: usersData, isLoading } = useAdminUsers({
    page: page + 1,
    limit,
    search: debouncedSearch,
    system_role: roleFilter,
    status: statusFilter,
  })
  const { data: rolesData } = useSystemRoles()
  const { mutate: updateRole, isPending: isUpdatingRole } = useUpdateUserSystemRole()
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateUserStatus()
  const { mutate: createUser, isPending: isCreating } = useCreateUser()
  const { mutate: deleteUser, isPending: isDeleting } = useDeleteUser()
  const { mutate: batchUserAction, isPending: isBatchProcessing } = useBatchUserAction()
  const { canChangeRole, canChangeStatus, canDeleteUser, isSelf, isTargetSystemAdmin } = useAdminPermissions()

  const handleRoleChange = useCallback((userId: string, currentRole: SystemRole, newRole: SystemRole) => {
    const check = canChangeRole(userId, currentRole, newRole)
    if (!check.allowed)
      return

    // Require confirmation for dangerous role changes:
    // 1. Promoting to system_admin (grants highest privilege)
    // 2. Demoting from tenant_manager to user (removes workspace management)
    const needsConfirm = newRole === 'system_admin'
      || (currentRole === 'tenant_manager' && newRole === 'user')

    if (needsConfirm) {
      const user = usersData?.data?.find(u => u.id === userId)
      setPendingRoleChange({ userId, name: user?.name || '', from: currentRole, to: newRole })
      setShowRoleConfirm(true)
      return
    }

    updateRole({ userId, role: newRole }, {
      onSuccess: () => Toast.notify({ type: 'success', message: t('admin.roleUpdateSuccess', { ns: 'custom' }) }),
      onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
    })
  }, [canChangeRole, updateRole, usersData?.data, t])

  const handleConfirmRoleChange = useCallback(() => {
    if (pendingRoleChange) {
      updateRole({ userId: pendingRoleChange.userId, role: pendingRoleChange.to }, {
        onSuccess: () => Toast.notify({ type: 'success', message: t('admin.roleUpdateSuccess', { ns: 'custom' }) }),
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      })
      setShowRoleConfirm(false)
    }
  }, [pendingRoleChange, updateRole, t])

  const handleStatusClick = useCallback((user: AdminUser) => {
    const newStatus: UserStatus = user.status === 'active' ? 'banned' : 'active'
    const check = canChangeStatus(user.id, user.system_role, newStatus)
    if (!check.allowed)
      return

    if (user.status === 'active') {
      setUserToToggle({ id: user.id, name: user.name, status: user.status })
      setShowStatusConfirm(true)
    }
    else {
      updateStatus({ userId: user.id, status: 'active' }, {
        onSuccess: () => Toast.notify({ type: 'success', message: t('admin.statusUpdateSuccess', { ns: 'custom' }) }),
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      })
    }
  }, [canChangeStatus, updateStatus, t])

  const handleConfirmStatusToggle = useCallback(() => {
    if (userToToggle) {
      const newStatus = userToToggle.status === 'active' ? 'banned' : 'active'
      updateStatus({ userId: userToToggle.id, status: newStatus }, {
        onSuccess: () => Toast.notify({ type: 'success', message: t('admin.statusUpdateSuccess', { ns: 'custom' }) }),
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      })
      setShowStatusConfirm(false)
    }
  }, [userToToggle, updateStatus, t])

  const handleCreateUser = useCallback((data: { name: string, email: string, password: string, systemRole: SystemRole }) => {
    createUser(data, {
      onSuccess: () => {
        setShowCreateModal(false)
        Toast.notify({ type: 'success', message: t('admin.userCreateSuccess', { ns: 'custom' }) })
      },
      onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
    })
  }, [createUser, t])

  const handleDeleteClick = useCallback((user: AdminUser) => {
    const check = canDeleteUser(user.id, user.system_role)
    if (!check.allowed)
      return
    setUserToDelete({ id: user.id, name: user.name })
    setShowDeleteConfirm(true)
  }, [canDeleteUser])

  const handleConfirmDelete = useCallback(() => {
    if (userToDelete) {
      deleteUser(userToDelete.id, {
        onSuccess: () => {
          setShowDeleteConfirm(false)
          Toast.notify({ type: 'success', message: t('admin.userDeleteSuccess', { ns: 'custom' }) })
        },
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      })
    }
  }, [userToDelete, deleteUser, t])

  // Batch selection handlers
  const selectableUsers = useMemo(() => {
    return usersData?.data?.filter(user => !isSelf(user.id) && !isTargetSystemAdmin(user.system_role)) || []
  }, [usersData?.data, isSelf, isTargetSystemAdmin])

  const isAllSelected = useMemo(() => {
    return selectableUsers.length > 0 && selectableUsers.every(user => selectedUserIds.has(user.id))
  }, [selectableUsers, selectedUserIds])

  const isIndeterminate = useMemo(() => {
    return selectedUserIds.size > 0 && !isAllSelected
  }, [selectedUserIds.size, isAllSelected])

  const handleSelectAll = useCallback(() => {
    if (isAllSelected)
      setSelectedUserIds(new Set())
    else
      setSelectedUserIds(new Set(selectableUsers.map(user => user.id)))
  }, [isAllSelected, selectableUsers])

  const handleSelectUser = useCallback((userId: string) => {
    setSelectedUserIds((prev) => {
      const next = new Set(prev)
      if (next.has(userId))
        next.delete(userId)
      else
        next.add(userId)
      return next
    })
  }, [])

  const handleBatchAction = useCallback((action: 'enable' | 'disable' | 'delete') => {
    setBatchAction(action)
    setShowBatchConfirm(true)
  }, [])

  const handleConfirmBatchAction = useCallback(() => {
    if (!batchAction || selectedUserIds.size === 0)
      return

    batchUserAction(
      { userIds: Array.from(selectedUserIds), action: batchAction },
      {
        onSuccess: () => {
          setShowBatchConfirm(false)
          setSelectedUserIds(new Set())
          Toast.notify({ type: 'success', message: t('admin.batchActionSuccess', { ns: 'custom', count: selectedUserIds.size }) })
        },
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      },
    )
  }, [batchAction, selectedUserIds, batchUserAction, t])

  // Build role options for dropdown with descriptions
  const systemRolesWithTips: RoleOption[] = useMemo(() => {
    return (rolesData?.roles || []).map(role => ({
      value: role.value,
      label: getSystemRoleLabel(role.value, t),
      description: getSystemRoleTip(role.value, t),
    }))
  }, [rolesData?.roles, t])

  // Build filter options
  const roleFilterOptions = useMemo(() => {
    const options = [{ value: '', name: t('admin.allRoles', { ns: 'custom' }) }]
    rolesData?.roles?.forEach((role) => {
      options.push({ value: role.value, name: getSystemRoleLabel(role.value, t) })
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
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <AdminPageHeader
          icon={<RiGroupLine className="h-6 w-6" />}
          title={t('admin.userManagement', { ns: 'custom' })}
          subtitle={t('admin.totalUsers', { ns: 'custom', count: usersData?.total || 0 })}
        />
        <Button variant="primary" onClick={() => setShowCreateModal(true)}>
          <RiAddLine className="mr-1 size-4" />
          {t('admin.createUser', { ns: 'custom' })}
        </Button>
      </div>

      {/* Filters */}
      <UserFilters
        search={search}
        onSearchChange={setSearch}
        roleFilter={roleFilter}
        onRoleFilterChange={setRoleFilter}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        roleFilterOptions={roleFilterOptions}
        statusFilterOptions={statusFilterOptions}
      />

      {/* Users Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-divider-subtle bg-components-panel-bg">
        {/* Table Header */}
        <div className="flex min-w-[800px] items-center border-b border-divider-regular bg-background-section-burn py-[7px]">
          <div className="flex w-10 shrink-0 items-center justify-center">
            <Checkbox
              checked={isAllSelected}
              indeterminate={isIndeterminate}
              onCheck={handleSelectAll}
              disabled={selectableUsers.length === 0}
            />
          </div>
          <div className="system-xs-medium-uppercase grow px-4 text-text-tertiary">
            {t('admin.user', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[140px] shrink-0 px-3 text-text-tertiary">
            {t('admin.systemRoleLabel', { ns: 'custom' })}
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
            ? <AdminTableSkeleton rows={5} columns={5} />
            : usersData?.data?.length === 0
              ? (
                  <AdminEmptyState
                    icon={<RiGroupLine className="size-6" />}
                    title={t('admin.noUsersFound', { ns: 'custom' })}
                    description={search ? t('admin.tryDifferentSearch', { ns: 'custom' }) : undefined}
                  />
                )
              : (
                  usersData?.data?.map(user => (
                    <UserTableRow
                      key={user.id}
                      user={user}
                      systemRolesWithTips={systemRolesWithTips}
                      isSelected={selectedUserIds.has(user.id)}
                      isSelectable={!isSelf(user.id) && !isTargetSystemAdmin(user.system_role)}
                      isUpdatingRole={isUpdatingRole}
                      isSelf={isSelf(user.id)}
                      isSystemAdmin={isTargetSystemAdmin(user.system_role)}
                      onSelect={handleSelectUser}
                      onRoleChange={handleRoleChange}
                      onStatusClick={handleStatusClick}
                      onDeleteClick={handleDeleteClick}
                      isUpdatingStatus={isUpdatingStatus}
                      isDeleting={isDeleting}
                    />
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

      {/* Create User Modal */}
      <CreateUserModal
        isShow={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateUser}
        isLoading={isCreating}
      />

      {/* Role Change Confirmation */}
      <Confirm
        isShow={showRoleConfirm}
        type={pendingRoleChange?.to === 'system_admin' ? 'warning' : 'danger'}
        title={pendingRoleChange?.to === 'system_admin'
          ? t('admin.confirmPromoteToAdminTitle', { ns: 'custom' })
          : t('admin.confirmDemoteRoleTitle', { ns: 'custom' })}
        content={pendingRoleChange?.to === 'system_admin'
          ? t('admin.confirmPromoteToAdmin', { ns: 'custom', name: pendingRoleChange?.name })
          : t('admin.confirmDemoteRole', { ns: 'custom', name: pendingRoleChange?.name })}
        onConfirm={handleConfirmRoleChange}
        onCancel={() => {
          setShowRoleConfirm(false)
        }}
        isLoading={isUpdatingRole}
      />

      {/* Confirmation Dialogs */}
      <UserConfirmDialogs
        showStatusConfirm={showStatusConfirm}
        userToToggle={userToToggle}
        onConfirmStatusToggle={handleConfirmStatusToggle}
        onCancelStatusToggle={() => {
          setShowStatusConfirm(false)
        }}
        isUpdatingStatus={isUpdatingStatus}
        showDeleteConfirm={showDeleteConfirm}
        userToDelete={userToDelete}
        onConfirmDelete={handleConfirmDelete}
        onCancelDelete={() => {
          setShowDeleteConfirm(false)
        }}
        isDeleting={isDeleting}
        showBatchConfirm={showBatchConfirm}
        batchAction={batchAction}
        selectedCount={selectedUserIds.size}
        onConfirmBatchAction={handleConfirmBatchAction}
        onCancelBatchAction={() => {
          setShowBatchConfirm(false)
        }}
        isBatchProcessing={isBatchProcessing}
      />

      {/* Batch Action Bar */}
      <BatchActionBar
        selectedCount={selectedUserIds.size}
        onEnable={() => handleBatchAction('enable')}
        onDisable={() => handleBatchAction('disable')}
        onDelete={() => handleBatchAction('delete')}
        onClear={() => setSelectedUserIds(new Set())}
        isLoading={isBatchProcessing}
      />
    </div>
  )
}
