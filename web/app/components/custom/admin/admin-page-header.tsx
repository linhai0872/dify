'use client'

import type { ReactNode } from 'react'
import { cn } from '@/utils/classnames'

export type AdminPageHeaderProps = {
  icon: ReactNode
  title: string
  subtitle?: string
  action?: ReactNode
  className?: string
}

/**
 * [CUSTOM] Admin page header component with gradient background.
 * Following Dify members-page design patterns.
 */
const AdminPageHeader = ({
  icon,
  title,
  subtitle,
  action,
  className,
}: AdminPageHeaderProps) => {
  return (
    <div className={cn(
      'mb-4 flex items-center gap-3 rounded-xl border-l-[0.5px] border-t-[0.5px] border-divider-subtle',
      'bg-gradient-to-r from-background-gradient-bg-fill-chat-bg-2 to-background-gradient-bg-fill-chat-bg-1',
      'p-3 pr-5',
      className,
    )}
    >
      {/* Icon */}
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-components-icon-bg-blue-solid text-[20px]">
        {typeof icon === 'string'
          ? (
              <span className="bg-gradient-to-r from-components-avatar-shape-fill-stop-0 to-components-avatar-shape-fill-stop-100 bg-clip-text font-semibold uppercase text-shadow-shadow-1 opacity-90">
                {icon}
              </span>
            )
          : (
              <span className="text-white">
                {icon}
              </span>
            )}
      </div>

      {/* Title and subtitle */}
      <div className="min-w-0 grow">
        <div className="system-md-semibold flex items-center gap-1 text-text-secondary">
          <span className="truncate">{title}</span>
        </div>
        {subtitle && (
          <div className="system-xs-medium mt-1 text-text-tertiary">
            {subtitle}
          </div>
        )}
      </div>

      {/* Action slot */}
      {action && (
        <div className="shrink-0">
          {action}
        </div>
      )}
    </div>
  )
}

export default AdminPageHeader
