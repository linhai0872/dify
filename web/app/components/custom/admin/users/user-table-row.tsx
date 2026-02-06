'use client'

import type { FC } from 'react'
import type { RoleOption } from '@/app/components/custom/admin'
import type { AdminUser, SystemRole } from '@/models/custom/admin'
import { RiDeleteBinLine } from '@remixicon/react'
import { useTranslation } from 'react-i18next'
import Avatar from '@/app/components/base/avatar'
import Checkbox from '@/app/components/base/checkbox'
import Tooltip from '@/app/components/base/tooltip'
import { RoleOperation, StatusBadge } from '@/app/components/custom/admin'
import { getStatusLabel } from '@/utils/custom/admin-labels'
import { formatDate } from '@/utils/custom/format-date'

export type UserTableRowProps = {
  user: AdminUser
  systemRolesWithTips: RoleOption[]
  isSelected: boolean
  isSelectable: boolean
  isUpdatingRole: boolean
  isSelf: boolean
  isSystemAdmin: boolean
  onSelect: (userId: string) => void
  onRoleChange: (userId: string, currentRole: SystemRole, newRole: SystemRole) => void
  onStatusClick: (user: AdminUser) => void
  onDeleteClick: (user: AdminUser) => void
  isUpdatingStatus: boolean
  isDeleting: boolean
}

const UserTableRow: FC<UserTableRowProps> = ({
  user,
  systemRolesWithTips,
  isSelected,
  isSelectable,
  isUpdatingRole,
  isSelf,
  isSystemAdmin,
  onSelect,
  onRoleChange,
  onStatusClick,
  onDeleteClick,
  isUpdatingStatus,
  isDeleting,
}) => {
  const { t } = useTranslation()
  const disabled = isSelf || isSystemAdmin

  return (
    <div className="flex border-b border-divider-subtle transition-colors hover:bg-state-base-hover">
      <div className="flex w-10 shrink-0 items-center justify-center">
        <Checkbox
          checked={isSelected}
          onCheck={() => onSelect(user.id)}
          disabled={!isSelectable}
        />
      </div>
      <div className="flex grow items-center px-4 py-2">
        <Avatar avatar={user.avatar_url} name={user.name} size={32} className="mr-3" />
        <div className="min-w-0">
          <div className="system-sm-medium truncate text-text-secondary">{user.name}</div>
          <div className="system-xs-regular truncate text-text-tertiary">{user.email}</div>
        </div>
      </div>
      <div className="flex w-[140px] shrink-0 items-center">
        <RoleOperation
          currentRole={user.system_role}
          roles={systemRolesWithTips}
          onRoleChange={role => onRoleChange(user.id, user.system_role, role as SystemRole)}
          disabled={isUpdatingRole || disabled}
        />
      </div>
      <div className="flex w-[100px] shrink-0 items-center px-3">
        <StatusBadge
          status={user.status as 'active' | 'pending' | 'banned' | 'closed'}
          label={getStatusLabel(user.status, t)}
        />
      </div>
      <div className="flex w-[120px] shrink-0 items-center px-3">
        <span className="system-sm-regular text-text-secondary">
          {t('admin.workspaceCount', { ns: 'custom', count: user.workspaces?.length || 0 })}
        </span>
      </div>
      <div className="flex w-[104px] shrink-0 items-center">
        <span className="system-sm-regular text-text-tertiary">{formatDate(user.last_active_at)}</span>
      </div>
      <div className="flex w-[100px] shrink-0 items-center gap-2 px-3">
        <Tooltip popupContent={user.status === 'active' ? t('admin.disable', { ns: 'custom' }) : t('admin.enable', { ns: 'custom' })}>
          <button
            onClick={() => onStatusClick(user)}
            disabled={isUpdatingStatus || disabled}
            className={`system-xs-medium rounded-md px-2 py-1 transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
              user.status === 'active'
                ? 'text-text-warning hover:bg-state-warning-hover'
                : 'text-util-colors-blue-brand-blue-brand-600 hover:bg-state-accent-hover'
            }`}
          >
            {user.status === 'active'
              ? t('admin.disable', { ns: 'custom' })
              : t('admin.enable', { ns: 'custom' })}
          </button>
        </Tooltip>
        <Tooltip popupContent={t('admin.deleteUser', { ns: 'custom' })}>
          <button
            onClick={() => onDeleteClick(user)}
            disabled={isDeleting || disabled}
            className="rounded-md p-1 text-text-tertiary transition-all hover:bg-state-destructive-hover hover:text-text-destructive disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RiDeleteBinLine className="size-4" />
          </button>
        </Tooltip>
      </div>
    </div>
  )
}

export default UserTableRow
