'use client'

/**
 * [CUSTOM] Workspace member management page for multi-workspace permission control.
 *
 * Features:
 * - List workspace members with skeleton loading
 * - Add members to workspace
 * - Modify member roles
 * - Remove members from workspace
 * - Toast feedback on all mutations
 */

import type { BreadcrumbItem, RoleOption } from '@/app/components/custom/admin'
import type { WorkspaceRole } from '@/models/custom/admin'
import {
  RiUserAddLine,
  RiUserLine,
} from '@remixicon/react'
import { useParams } from 'next/navigation'
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Avatar from '@/app/components/base/avatar'
import Button from '@/app/components/base/button'
import Confirm from '@/app/components/base/confirm'
import Modal from '@/app/components/base/modal'
import SearchInput from '@/app/components/base/search-input'
import Toast from '@/app/components/base/toast'
import { AdminBreadcrumb, AdminEmptyState, AdminPageHeader, AdminTableSkeleton, RoleOperation } from '@/app/components/custom/admin'
import {
  useAddWorkspaceMember,
  useAvailableUsers,
  useRemoveWorkspaceMember,
  useUpdateMemberRole,
  useWorkspaceMembers,
  useWorkspaceRoles,
} from '@/service/custom/admin-member'
import { cn } from '@/utils/classnames'
import { getWorkspaceRoleLabel, getWorkspaceRoleTip } from '@/utils/custom/admin-labels'
import { formatDate } from '@/utils/custom/format-date'

export default function WorkspaceMembersPage() {
  const { t } = useTranslation()
  const params = useParams()
  const workspaceId = params.workspaceId as string

  const [showAddModal, setShowAddModal] = useState(false)
  const [userSearch, setUserSearch] = useState('')
  const [selectedUserId, setSelectedUserId] = useState('')
  const [selectedRole, setSelectedRole] = useState<WorkspaceRole>('normal')

  const [showRemoveConfirm, setShowRemoveConfirm] = useState(false)
  const [memberToRemove, setMemberToRemove] = useState<{ id: string, name: string } | null>(null)

  const { data: membersData, isLoading } = useWorkspaceMembers(workspaceId)
  const { data: rolesData } = useWorkspaceRoles()
  const { data: availableUsersData } = useAvailableUsers(workspaceId, userSearch, showAddModal)

  const { mutate: addMember, isPending: isAdding } = useAddWorkspaceMember()
  const { mutate: updateRole, isPending: isUpdatingRole } = useUpdateMemberRole()
  const { mutate: removeMember, isPending: isRemoving } = useRemoveWorkspaceMember()

  const workspaceName = membersData?.workspace?.name || workspaceId

  const handleAddMember = useCallback(() => {
    if (!selectedUserId || !selectedRole)
      return

    addMember(
      { workspaceId, userId: selectedUserId, role: selectedRole },
      {
        onSuccess: () => {
          setShowAddModal(false)
          setSelectedUserId('')
          setSelectedRole('normal')
          setUserSearch('')
          Toast.notify({ type: 'success', message: t('admin.memberAddSuccess', { ns: 'custom' }) })
        },
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      },
    )
  }, [workspaceId, selectedUserId, selectedRole, addMember, t])

  const handleRoleChange = useCallback((userId: string, role: WorkspaceRole) => {
    updateRole({ workspaceId, userId, role }, {
      onSuccess: () => Toast.notify({ type: 'success', message: t('admin.memberRoleUpdateSuccess', { ns: 'custom' }) }),
      onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
    })
  }, [workspaceId, updateRole, t])

  const handleRemoveClick = useCallback((userId: string, name: string) => {
    setMemberToRemove({ id: userId, name })
    setShowRemoveConfirm(true)
  }, [])

  const handleConfirmRemove = useCallback(() => {
    if (memberToRemove) {
      removeMember({ workspaceId, userId: memberToRemove.id }, {
        onSuccess: () => {
          setShowRemoveConfirm(false)
          setMemberToRemove(null)
          Toast.notify({ type: 'success', message: t('admin.memberRemoveSuccess', { ns: 'custom' }) })
        },
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      })
    }
  }, [workspaceId, memberToRemove, removeMember, t])

  const workspaceRolesWithTips: RoleOption[] = useMemo(() => {
    return (rolesData?.roles || []).map(role => ({
      value: role.value,
      label: getWorkspaceRoleLabel(role.value, t),
      description: getWorkspaceRoleTip(role.value, t),
    }))
  }, [rolesData?.roles, t])

  const ownerCount = membersData?.data?.filter(m => m.role === 'owner').length || 0

  const breadcrumbItems: BreadcrumbItem[] = useMemo(() => [
    { label: t('admin.systemAdmin', { ns: 'custom' }), href: '/custom-admin/users' },
    { label: t('admin.workspaceManagement', { ns: 'custom' }), href: '/custom-admin/workspaces' },
    { label: workspaceName },
  ], [t, workspaceName])

  return (
    <div className="flex h-full flex-col">
      <AdminBreadcrumb items={breadcrumbItems} className="mb-3" />

      <AdminPageHeader
        icon={workspaceName[0]?.toUpperCase() || 'W'}
        title={workspaceName}
        subtitle={t('admin.totalMembers', { ns: 'custom', count: membersData?.total || 0 })}
        action={(
          <Button variant="primary" onClick={() => setShowAddModal(true)}>
            <RiUserAddLine className="mr-1 h-4 w-4" />
            {t('admin.addMember', { ns: 'custom' })}
          </Button>
        )}
      />
      {/* Workspace ID for reference */}
      {membersData?.workspace && (
        <div className="system-xs-regular mb-3 text-text-quaternary">
          ID:
          {' '}
          {workspaceId}
        </div>
      )}

      {/* Members Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-divider-subtle bg-components-panel-bg">
        <div className="flex min-w-[600px] items-center border-b border-divider-regular bg-background-section-burn py-[7px]">
          <div className="system-xs-medium-uppercase grow px-4 text-text-tertiary">
            {t('admin.member', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[140px] shrink-0 px-3 text-text-tertiary">
            {t('admin.role', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[120px] shrink-0 text-text-tertiary">
            {t('admin.joined', { ns: 'custom' })}
          </div>
          <div className="system-xs-medium-uppercase w-[100px] shrink-0 px-3 text-text-tertiary">
            {t('admin.actions', { ns: 'custom' })}
          </div>
        </div>

        <div className="min-w-[600px]">
          {isLoading
            ? <AdminTableSkeleton rows={5} columns={3} />
            : membersData?.data?.length === 0
              ? (
                  <AdminEmptyState
                    icon={<RiUserLine className="size-6" />}
                    title={t('admin.noMembersFound', { ns: 'custom' })}
                    description={t('admin.addMemberHint', { ns: 'custom' })}
                    action={(
                      <Button variant="primary" onClick={() => setShowAddModal(true)}>
                        <RiUserAddLine className="mr-1 size-4" />
                        {t('admin.addMember', { ns: 'custom' })}
                      </Button>
                    )}
                  />
                )
              : (
                  membersData?.data?.map(member => (
                    <div key={member.id} className="flex border-b border-divider-subtle transition-colors hover:bg-state-base-hover">
                      <div className="flex grow items-center px-4 py-2">
                        <Avatar avatar={member.avatar_url} name={member.name} size={32} className="mr-3" />
                        <div className="min-w-0">
                          <div className="system-sm-medium truncate text-text-secondary">{member.name}</div>
                          <div className="system-xs-regular truncate text-text-tertiary">{member.email}</div>
                        </div>
                      </div>
                      <div className="flex w-[140px] shrink-0 items-center">
                        <RoleOperation
                          currentRole={member.role}
                          roles={workspaceRolesWithTips}
                          onRoleChange={role => handleRoleChange(member.id, role as WorkspaceRole)}
                          disabled={isUpdatingRole || (member.role === 'owner' && ownerCount <= 1)}
                        />
                      </div>
                      <div className="flex w-[120px] shrink-0 items-center">
                        <span className="system-sm-regular text-text-tertiary">{formatDate(member.joined_at)}</span>
                      </div>
                      <div className="flex w-[100px] shrink-0 items-center px-3">
                        <Button
                          variant="warning"
                          size="small"
                          onClick={() => handleRemoveClick(member.id, member.name)}
                          disabled={isRemoving || (member.role === 'owner' && ownerCount <= 1)}
                        >
                          {t('admin.remove', { ns: 'custom' })}
                        </Button>
                      </div>
                    </div>
                  ))
                )}
        </div>
      </div>

      {/* Add Member Modal */}
      <Modal
        isShow={showAddModal}
        onClose={() => setShowAddModal(false)}
        title={t('admin.addMember', { ns: 'custom' })}
        closable
      >
        <div className="mt-4">
          <div className="mb-4">
            <label className="system-sm-medium mb-2 block text-text-secondary">
              {t('admin.selectUser', { ns: 'custom' })}
            </label>
            <SearchInput
              placeholder={t('admin.searchPlaceholder', { ns: 'custom' })}
              value={userSearch}
              onChange={setUserSearch}
            />
            <div className="mt-2 max-h-40 overflow-auto rounded-lg border border-divider-subtle">
              {availableUsersData?.data?.length === 0
                ? (
                    <div className="system-sm-regular px-3 py-4 text-center text-text-tertiary">
                      {t('admin.noAvailableUsers', { ns: 'custom' })}
                    </div>
                  )
                : (
                    availableUsersData?.data?.map(user => (
                      <div
                        key={user.id}
                        onClick={() => setSelectedUserId(user.id)}
                        className={cn(
                          'flex cursor-pointer items-center gap-2 px-3 py-2 hover:bg-state-base-hover',
                          selectedUserId === user.id && 'bg-state-accent-hover ring-1 ring-inset ring-components-input-border-active',
                        )}
                      >
                        <Avatar avatar={user.avatar_url} name={user.name} size={24} />
                        <div className="min-w-0 flex-1">
                          <div className="system-sm-medium truncate text-text-primary">{user.name}</div>
                          <div className="system-xs-regular truncate text-text-tertiary">{user.email}</div>
                        </div>
                      </div>
                    ))
                  )}
            </div>
          </div>

          <div className="mb-6">
            <label className="system-sm-medium mb-2 block text-text-secondary">
              {t('admin.selectRole', { ns: 'custom' })}
            </label>
            <div className="space-y-1 rounded-lg border border-divider-subtle p-1">
              {workspaceRolesWithTips.map(role => (
                <div
                  key={role.value}
                  onClick={() => setSelectedRole(role.value as WorkspaceRole)}
                  className={cn(
                    'cursor-pointer rounded-lg px-3 py-2 transition-colors hover:bg-state-base-hover',
                    selectedRole === role.value && 'bg-state-accent-hover ring-1 ring-inset ring-components-input-border-active',
                  )}
                >
                  <div className="system-sm-medium text-text-secondary">{role.label}</div>
                  {role.description && (
                    <div className="system-xs-regular text-text-tertiary">{role.description}</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setShowAddModal(false)}>
              {t('admin.cancel', { ns: 'custom' })}
            </Button>
            <Button
              variant="primary"
              onClick={handleAddMember}
              disabled={!selectedUserId || isAdding}
              loading={isAdding}
            >
              {t('admin.addMember', { ns: 'custom' })}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Remove Confirmation */}
      <Confirm
        isShow={showRemoveConfirm}
        type="danger"
        title={t('admin.confirmRemoveMemberTitle', { ns: 'custom' })}
        content={t('admin.confirmRemoveMember', { ns: 'custom', name: memberToRemove?.name || '' })}
        onConfirm={handleConfirmRemove}
        onCancel={() => {
          setShowRemoveConfirm(false)
          setMemberToRemove(null)
        }}
        isLoading={isRemoving}
      />
    </div>
  )
}
