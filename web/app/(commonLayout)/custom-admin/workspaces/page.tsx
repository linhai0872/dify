'use client'

/**
 * [CUSTOM] Workspace management page for multi-workspace permission control.
 *
 * Features:
 * - List all workspaces with member counts
 * - Search workspaces by name
 * - Navigate to workspace member management
 */

import {
  RiArrowRightSLine,
  RiGroupLine,
  RiLoader4Line,
  RiSearchLine,
  RiTeamLine,
} from '@remixicon/react'
import Link from 'next/link'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import { useAdminWorkspaces } from '@/service/custom/admin-member'

export default function WorkspacesPage() {
  const { t } = useTranslation()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')

  const { data: workspacesData, isLoading } = useAdminWorkspaces({
    page,
    limit: 20,
    search,
  })

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="mb-6">
        <h2 className="system-xl-semibold text-text-primary">
          {t('admin.workspaceManagement', { ns: 'custom' })}
        </h2>
        <p className="mt-1 text-sm text-text-tertiary">
          {t('admin.workspaceManagementDesc', { ns: 'custom' })}
        </p>
      </div>

      {/* Search */}
      <div className="mb-4">
        <div className="relative max-w-[400px]">
          <RiSearchLine className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-tertiary" />
          <input
            type="text"
            placeholder={t('admin.searchWorkspacePlaceholder', { ns: 'custom' })}
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="system-sm-regular w-full rounded-lg border border-components-input-border-active bg-components-input-bg-normal py-2 pl-9 pr-3 text-text-primary placeholder:text-text-placeholder focus:border-components-input-border-active focus:outline-none"
          />
        </div>
      </div>

      {/* Workspaces Grid */}
      <div className="flex-1 overflow-auto">
        {isLoading
          ? (
              <div className="flex h-48 items-center justify-center">
                <RiLoader4Line className="size-6 animate-spin text-text-tertiary" />
              </div>
            )
          : workspacesData?.data?.length === 0
            ? (
                <div className="flex h-48 flex-col items-center justify-center gap-2">
                  <RiTeamLine className="size-12 text-text-quaternary" />
                  <span className="system-sm-regular text-text-tertiary">
                    {t('admin.noWorkspacesFound', { ns: 'custom' })}
                  </span>
                </div>
              )
            : (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {workspacesData?.data?.map(workspace => (
                    <Link
                      key={workspace.id}
                      href={`/custom-admin/workspaces/${workspace.id}/members`}
                      className="group flex flex-col rounded-xl border border-divider-subtle bg-components-panel-bg p-4 transition-all hover:border-components-panel-border-subtle hover:shadow-md"
                    >
                      {/* Workspace Icon & Name */}
                      <div className="mb-3 flex items-start justify-between">
                        <div className="flex size-10 items-center justify-center rounded-lg bg-util-colors-blue-brand-blue-brand-50">
                          <RiTeamLine className="size-5 text-util-colors-blue-brand-blue-brand-600" />
                        </div>
                        <RiArrowRightSLine className="size-5 text-text-tertiary opacity-0 transition-opacity group-hover:opacity-100" />
                      </div>

                      {/* Workspace Name */}
                      <h3 className="system-md-semibold mb-1 text-text-primary">
                        {workspace.name}
                      </h3>

                      {/* Member Count */}
                      <div className="mt-auto flex items-center gap-1.5 text-text-tertiary">
                        <RiGroupLine className="size-4" />
                        <span className="system-sm-regular">
                          {t('admin.memberCount', { ns: 'custom', count: workspace.member_count || 0 })}
                        </span>
                      </div>

                      {/* Created Date */}
                      <div className="system-xs-regular mt-2 text-text-quaternary">
                        {workspace.created_at
                          ? new Date(workspace.created_at).toLocaleDateString()
                          : '-'}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
      </div>

      {/* Pagination */}
      {workspacesData && workspacesData.total > 20 && (
        <div className="mt-4 flex items-center justify-between border-t border-divider-subtle pt-4">
          <span className="system-sm-regular text-text-tertiary">
            {t('admin.pageShowing', {
              ns: 'custom',
              from: ((page - 1) * 20) + 1,
              to: Math.min(page * 20, workspacesData.total),
              total: workspacesData.total,
            })}
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="small"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              {t('admin.pagePrevious', { ns: 'custom' })}
            </Button>
            <Button
              variant="secondary"
              size="small"
              onClick={() => setPage(p => p + 1)}
              disabled={page * 20 >= workspacesData.total}
            >
              {t('admin.pageNext', { ns: 'custom' })}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
