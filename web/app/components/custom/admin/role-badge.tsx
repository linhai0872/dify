'use client'

import type { FC } from 'react'
import { cn } from '@/utils/classnames'

export type RoleBadgeProps = {
  role: string
  label: string
  type?: 'system' | 'workspace'
  className?: string
}

// System role colors
const systemRoleColors: Record<string, { bg: string, text: string }> = {
  // New role names
  system_admin: { bg: 'bg-util-colors-red-red-50', text: 'text-util-colors-red-red-600' },
  tenant_manager: { bg: 'bg-util-colors-blue-light-blue-50', text: 'text-util-colors-blue-light-blue-600' },
  user: { bg: 'bg-components-badge-bg-gray', text: 'text-text-tertiary' },
  // Legacy role names for backward compatibility
  super_admin: { bg: 'bg-util-colors-red-red-50', text: 'text-util-colors-red-red-600' },
  workspace_admin: { bg: 'bg-util-colors-blue-light-blue-50', text: 'text-util-colors-blue-light-blue-600' },
  normal: { bg: 'bg-components-badge-bg-gray', text: 'text-text-tertiary' },
}

// Workspace role colors
const workspaceRoleColors: Record<string, { bg: string, text: string }> = {
  owner: { bg: 'bg-util-colors-violet-violet-50', text: 'text-util-colors-violet-violet-600' },
  admin: { bg: 'bg-util-colors-blue-light-blue-50', text: 'text-util-colors-blue-light-blue-600' },
  editor: { bg: 'bg-util-colors-green-green-50', text: 'text-util-colors-green-green-600' },
  normal: { bg: 'bg-components-badge-bg-gray', text: 'text-text-tertiary' },
  dataset_operator: { bg: 'bg-util-colors-warning-warning-50', text: 'text-util-colors-warning-warning-600' },
}

/**
 * [CUSTOM] Role badge component with semantic colors.
 * Supports both system roles and workspace roles.
 */
const RoleBadge: FC<RoleBadgeProps> = ({
  role,
  label,
  type = 'workspace',
  className,
}) => {
  const colorMap = type === 'system' ? systemRoleColors : workspaceRoleColors
  const colors = colorMap[role] || colorMap.normal

  return (
    <span
      className={cn(
        'system-xs-medium inline-flex shrink-0 items-center rounded-md px-2 py-0.5',
        colors.bg,
        colors.text,
        className,
      )}
    >
      {label}
    </span>
  )
}

export default RoleBadge
