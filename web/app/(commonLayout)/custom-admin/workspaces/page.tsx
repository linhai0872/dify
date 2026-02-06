'use client'

/**
 * [CUSTOM] Workspace management page for multi-workspace permission control.
 *
 * Features:
 * - List all workspaces with member counts
 * - Search workspaces by name (debounced)
 * - Create new workspaces
 * - Delete workspaces (with confirmation)
 * - Navigate to workspace member management
 */

import type { AdminWorkspace } from '@/models/custom/admin'
import {
  RiAddLine,
  RiArrowRightSLine,
  RiDeleteBinLine,
  RiGroupLine,
  RiTeamLine,
} from '@remixicon/react'
import Link from 'next/link'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import Confirm from '@/app/components/base/confirm'
import Input from '@/app/components/base/input'
import Modal from '@/app/components/base/modal'
import Pagination from '@/app/components/base/pagination'
import SearchInput from '@/app/components/base/search-input'
import Toast from '@/app/components/base/toast'
import { AdminEmptyState, AdminPageHeader } from '@/app/components/custom/admin'
import { useDebouncedValue } from '@/hooks/custom/use-custom-debounced-value'
import { useIsSystemAdmin } from '@/hooks/custom/use-custom-system-role'
import { useAdminWorkspaces, useCreateWorkspace, useDeleteWorkspace } from '@/service/custom/admin-member'
import { formatDate } from '@/utils/custom/format-date'

export default function WorkspacesPage() {
  const { t } = useTranslation()
  const { isSystemAdmin } = useIsSystemAdmin()
  const [page, setPage] = useState(0)
  const [limit, setLimit] = useState(12)
  const [search, setSearch] = useState('')

  const debouncedSearch = useDebouncedValue(search, 300)

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newWorkspaceName, setNewWorkspaceName] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [workspaceToDelete, setWorkspaceToDelete] = useState<AdminWorkspace | null>(null)

  const { data: workspacesData, isLoading } = useAdminWorkspaces({
    page: page + 1,
    limit,
    search: debouncedSearch,
  })

  const { mutate: createWorkspace, isPending: isCreating } = useCreateWorkspace()
  const { mutate: deleteWorkspace, isPending: isDeleting } = useDeleteWorkspace()

  const handleCreateWorkspace = useCallback(() => {
    if (!newWorkspaceName.trim())
      return

    createWorkspace(
      { name: newWorkspaceName.trim() },
      {
        onSuccess: () => {
          setShowCreateModal(false)
          setNewWorkspaceName('')
          Toast.notify({ type: 'success', message: t('admin.workspaceCreateSuccess', { ns: 'custom' }) })
        },
        onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
      },
    )
  }, [newWorkspaceName, createWorkspace, t])

  const handleDeleteClick = useCallback((e: React.MouseEvent, workspace: AdminWorkspace) => {
    e.preventDefault()
    e.stopPropagation()
    setWorkspaceToDelete(workspace)
    setShowDeleteConfirm(true)
  }, [])

  const handleConfirmDelete = useCallback(() => {
    if (workspaceToDelete) {
      deleteWorkspace(
        { workspaceId: workspaceToDelete.id },
        {
          onSuccess: () => {
            setShowDeleteConfirm(false)
            Toast.notify({ type: 'success', message: t('admin.workspaceDeleteSuccess', { ns: 'custom' }) })
          },
          onError: () => Toast.notify({ type: 'error', message: t('admin.operationFailed', { ns: 'custom' }) }),
        },
      )
    }
  }, [workspaceToDelete, deleteWorkspace, t])

  // Card skeleton for loading state
  const renderCardSkeleton = () => (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="flex flex-col rounded-xl border border-divider-subtle bg-components-panel-bg p-4">
          <div className="mb-3 flex items-start justify-between">
            <div className="size-12 animate-pulse rounded-xl bg-state-base-hover" />
          </div>
          <div className="mb-2 h-5 w-32 animate-pulse rounded bg-state-base-hover" />
          <div className="mt-auto h-4 w-20 animate-pulse rounded bg-state-base-hover" />
          <div className="mt-2 h-3 w-24 animate-pulse rounded bg-state-base-hover" />
        </div>
      ))}
    </div>
  )

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <AdminPageHeader
          icon={<RiTeamLine className="h-6 w-6" />}
          title={isSystemAdmin ? t('admin.workspaceManagement', { ns: 'custom' }) : t('admin.myWorkspaces', { ns: 'custom' })}
          subtitle={t('admin.workspaceManagementDesc', { ns: 'custom' })}
        />
        <Button variant="primary" onClick={() => setShowCreateModal(true)}>
          <RiAddLine className="mr-1 size-4" />
          {t('admin.createWorkspace', { ns: 'custom' })}
        </Button>
      </div>

      {/* Search */}
      <div className="mb-4">
        <SearchInput
          className="max-w-[400px]"
          placeholder={t('admin.searchWorkspacePlaceholder', { ns: 'custom' })}
          value={search}
          onChange={setSearch}
        />
      </div>

      {/* Workspaces Grid */}
      <div className="flex-1 overflow-auto">
        {isLoading
          ? renderCardSkeleton()
          : workspacesData?.data?.length === 0
            ? (
                <AdminEmptyState
                  icon={<RiTeamLine className="size-6" />}
                  title={t('admin.noWorkspacesFound', { ns: 'custom' })}
                  description={!search ? t('admin.createFirstWorkspace', { ns: 'custom' }) : undefined}
                  action={!search
                    ? (
                        <Button variant="primary" onClick={() => setShowCreateModal(true)}>
                          <RiAddLine className="mr-1 size-4" />
                          {t('admin.createWorkspace', { ns: 'custom' })}
                        </Button>
                      )
                    : undefined}
                />
              )
            : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {workspacesData?.data?.map(workspace => (
                    <Link
                      key={workspace.id}
                      href={`/custom-admin/workspaces/${workspace.id}/members`}
                      className="group relative flex flex-col rounded-xl border border-divider-subtle bg-components-panel-bg p-4 transition-all hover:border-components-panel-border-subtle hover:shadow-md"
                    >
                      {/* Workspace Icon & Name */}
                      <div className="mb-3 flex items-start justify-between">
                        <div className="flex size-12 items-center justify-center rounded-xl bg-gradient-to-br from-util-colors-blue-brand-blue-brand-50 to-util-colors-blue-brand-blue-brand-100">
                          <span className="system-lg-semibold text-util-colors-blue-brand-blue-brand-600">
                            {workspace.name[0]?.toUpperCase() || 'W'}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              if (!workspace.is_default && workspace.member_count <= 1)
                                handleDeleteClick(e, workspace)
                              else if (workspace.is_default)
                                Toast.notify({ type: 'warning', message: t('admin.cannotDeleteDefaultWorkspace', { ns: 'custom' }) })
                            }}
                            className={`rounded-md p-1 opacity-0 transition-all group-hover:opacity-100 ${
                              !workspace.is_default && workspace.member_count <= 1
                                ? 'text-text-tertiary hover:bg-state-destructive-hover hover:text-text-destructive'
                                : 'cursor-not-allowed text-text-disabled'
                            }`}
                            title={workspace.is_default
                              ? t('admin.cannotDeleteDefaultWorkspace', { ns: 'custom' })
                              : workspace.member_count <= 1
                                ? t('admin.deleteWorkspace', { ns: 'custom' })
                                : t('admin.workspaceHasTooManyMembers', { ns: 'custom' })}
                          >
                            <RiDeleteBinLine className="size-4" />
                          </button>
                          <RiArrowRightSLine className="size-5 text-text-tertiary opacity-0 transition-opacity group-hover:opacity-100" />
                        </div>
                      </div>

                      <h3 className="system-md-semibold mb-1 text-text-primary">{workspace.name}</h3>

                      <div className="mt-auto flex items-center gap-1.5 text-text-tertiary">
                        <RiGroupLine className="size-4" />
                        <span className="system-sm-regular">
                          {t('admin.memberCount', { ns: 'custom', count: workspace.member_count || 0 })}
                        </span>
                      </div>

                      <div className="system-xs-regular mt-2 text-text-quaternary">
                        {formatDate(workspace.created_at)}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
      </div>

      {/* Pagination */}
      {workspacesData && workspacesData.total > limit && (
        <Pagination
          className="mt-4"
          current={page}
          onChange={setPage}
          total={workspacesData.total}
          limit={limit}
          onLimitChange={setLimit}
        />
      )}

      {/* Create Workspace Modal */}
      <Modal
        isShow={showCreateModal}
        onClose={() => {
          setShowCreateModal(false)
          setNewWorkspaceName('')
        }}
        title={t('admin.createWorkspace', { ns: 'custom' })}
        closable
      >
        <div className="mt-4">
          <label className="system-sm-medium mb-2 block text-text-secondary">
            {t('admin.workspaceName', { ns: 'custom' })}
          </label>
          <Input
            value={newWorkspaceName}
            onChange={e => setNewWorkspaceName(e.target.value)}
            placeholder={t('admin.workspaceName', { ns: 'custom' })}
            className="mb-6"
          />
          <div className="flex justify-end gap-2">
            <Button
              variant="secondary"
              onClick={() => {
                setShowCreateModal(false)
                setNewWorkspaceName('')
              }}
            >
              {t('admin.cancel', { ns: 'custom' })}
            </Button>
            <Button
              variant="primary"
              onClick={handleCreateWorkspace}
              disabled={!newWorkspaceName.trim() || isCreating}
              loading={isCreating}
            >
              {t('admin.createWorkspace', { ns: 'custom' })}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Delete Confirmation */}
      <Confirm
        isShow={showDeleteConfirm}
        type="danger"
        title={t('admin.confirmDeleteWorkspaceTitle', { ns: 'custom' })}
        content={workspaceToDelete?.member_count === 1
          ? t('admin.confirmDeleteWorkspaceWithOwner', { ns: 'custom', name: workspaceToDelete?.name })
          : t('admin.confirmDeleteWorkspace', { ns: 'custom' })}
        onConfirm={handleConfirmDelete}
        onCancel={() => {
          setShowDeleteConfirm(false)
        }}
        isLoading={isDeleting}
      />
    </div>
  )
}
