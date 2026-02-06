/**
 * [CUSTOM] Status badge component for multi-workspace admin.
 *
 * Displays user account status (active/pending/banned) with colored dot indicator.
 */
'use client'

import type { FC } from 'react'
import { cn } from '@/utils/classnames'

export type StatusBadgeProps = {
  status: 'active' | 'pending' | 'banned' | 'closed'
  label: string
  className?: string
}

// Status colors with dot indicator
const statusConfig: Record<string, { bg: string, text: string, dot: string }> = {
  active: {
    bg: 'bg-util-colors-green-green-50',
    text: 'text-util-colors-green-green-600',
    dot: 'bg-util-colors-green-green-500',
  },
  pending: {
    bg: 'bg-util-colors-warning-warning-50',
    text: 'text-util-colors-warning-warning-600',
    dot: 'bg-util-colors-warning-warning-500',
  },
  banned: {
    bg: 'bg-util-colors-red-red-50',
    text: 'text-util-colors-red-red-600',
    dot: 'bg-util-colors-red-red-500',
  },
  closed: {
    bg: 'bg-components-badge-bg-gray',
    text: 'text-text-tertiary',
    dot: 'bg-text-quaternary',
  },
}

/**
 * [CUSTOM] Status badge component with colored dot indicator.
 * Displays user account status with visual distinction.
 */
const StatusBadge: FC<StatusBadgeProps> = ({
  status,
  label,
  className,
}) => {
  const config = statusConfig[status] || statusConfig.closed

  return (
    <span
      className={cn(
        'system-xs-medium inline-flex shrink-0 items-center gap-1.5 rounded-md px-2 py-0.5',
        config.bg,
        config.text,
        className,
      )}
    >
      <span className={cn('size-1.5 rounded-full', config.dot)} />
      {label}
    </span>
  )
}

export default StatusBadge
