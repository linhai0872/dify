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
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Avatar } from '@/app/components/base/avatar'
import Button from '@/app/components/base/button'
import SearchInput from '@/app/components/base/search-input'
import {
  AlertDialog,
  AlertDialogActions,
  AlertDialogCancelButton,
  AlertDialogConfirmButton,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/app/components/base/ui/alert-dialog'
import { Dialog, DialogCloseButton, DialogContent, DialogTitle } from '@/app/components/base/ui/dialog'
import { toast } from '@/app/components/base/ui/toast'
import { AdminBreadcrumb, AdminEmptyState, AdminPageHeader, AdminTableSkeleton, RoleOperation } from '@/app/components/custom/admin'
import { useParams } from '@/next/navigation'
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
          toast.success(t('admin.memberAddSuccess', { ns: 'custom' }))
        },
        onError: () => toast.error(t('admin.operationFailed', { ns: 'custom' })),
      },
    )
  }, [workspaceId, selectedUserId, selectedRole, addMember, t])

  const handleRoleChange = useCallback((userId: string, role: WorkspaceRole) => {
    updateRole({ workspaceId, userId, role }, {
      onSuccess: () => toast.success(t('admin.memberRoleUpdateSuccess', { ns: 'custom' })),
      onError: () => toast.error(t('admin.operationFailed', { ns: 'custom' })),
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
          toast.success(t('admin.memberRemoveSuccess', { ns: 'custom' }))
        },
        onError: () => toast.error(t('admin.operationFailed', { ns: 'custom' })),
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
        <div className="mb-3 text-text-quaternary system-xs-regular">
          ID:
          {' '}
          {workspaceId}
        </div>
      )}

      {/* Members Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-divider-subtle bg-components-panel-bg">
        <div className="flex min-w-[600px] items-center border-b border-divider-regular bg-background-section-burn py-[7px]">
          <div className="grow px-4 text-text-tertiary system-xs-medium-uppercase">
            {t('admin.member', { ns: 'custom' })}
          </div>
          <div className="w-[140px] shrink-0 px-3 text-text-tertiary system-xs-medium-uppercase">
            {t('admin.role', { ns: 'custom' })}
          </div>
          <div className="w-[120px] shrink-0 text-text-tertiary system-xs-medium-uppercase">
            {t('admin.joined', { ns: 'custom' })}
          </div>
          <div className="w-[100px] shrink-0 px-3 text-text-tertiary system-xs-medium-uppercase">
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
                        <Avatar avatar={member.avatar_url} name={member.name} size="md" className="mr-3" />
                        <div className="min-w-0">
                          <div className="truncate text-text-secondary system-sm-medium">{member.name}</div>
                          <div className="truncate text-text-tertiary system-xs-regular">{member.email}</div>
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
                        <span className="text-text-tertiary system-sm-regular">{formatDate(member.joined_at)}</span>
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
      <Dialog open={showAddModal} onOpenChange={open => !open && setShowAddModal(false)}>
        <DialogContent className="max-w-[520px]">
          <DialogCloseButton />
          <DialogTitle className="text-text-primary title-2xl-semi-bold">
            {t('admin.addMember', { ns: 'custom' })}
          </DialogTitle>
          <div className="mt-4">
            <div className="mb-4">
              <label className="mb-2 block text-text-secondary system-sm-medium">
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
                      <div className="px-3 py-4 text-center text-text-tertiary system-sm-regular">
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
                          <Avatar avatar={user.avatar_url} name={user.name} size="sm" />
                          <div className="min-w-0 flex-1">
                            <div className="truncate text-text-primary system-sm-medium">{user.name}</div>
                            <div className="truncate text-text-tertiary system-xs-regular">{user.email}</div>
                          </div>
                        </div>
                      ))
                    )}
              </div>
            </div>

            <div className="mb-6">
              <label className="mb-2 block text-text-secondary system-sm-medium">
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
                    <div className="text-text-secondary system-sm-medium">{role.label}</div>
                    {role.description && (
                      <div className="text-text-tertiary system-xs-regular">{role.description}</div>
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
        </DialogContent>
      </Dialog>

      {/* Remove Confirmation */}
      <AlertDialog
        open={showRemoveConfirm}
        onOpenChange={(open) => {
          if (!open) {
            setShowRemoveConfirm(false)
            setMemberToRemove(null)
          }
        }}
      >
        <AlertDialogContent>
          <div className="flex flex-col items-start gap-2 self-stretch pb-4 pl-6 pr-6 pt-6">
            <AlertDialogTitle className="w-full text-text-primary title-2xl-semi-bold">
              {t('admin.confirmRemoveMemberTitle', { ns: 'custom' })}
            </AlertDialogTitle>
            <AlertDialogDescription className="w-full whitespace-pre-wrap break-words text-text-tertiary system-md-regular">
              {t('admin.confirmRemoveMember', { ns: 'custom', name: memberToRemove?.name || '' })}
            </AlertDialogDescription>
          </div>
          <AlertDialogActions>
            <AlertDialogCancelButton disabled={isRemoving}>
              {t('operation.cancel', { ns: 'common' })}
            </AlertDialogCancelButton>
            <AlertDialogConfirmButton loading={isRemoving} disabled={isRemoving} onClick={handleConfirmRemove}>
              {t('operation.confirm', { ns: 'common' })}
            </AlertDialogConfirmButton>
          </AlertDialogActions>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
