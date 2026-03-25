'use client'

import type { FC, ReactNode } from 'react'
import { cn } from '@/utils/classnames'

export type AdminEmptyStateProps = {
  icon: ReactNode
  title: string
  description?: string
  action?: ReactNode
  className?: string
}

const AdminEmptyState: FC<AdminEmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className,
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16', className)}>
      <div className="mb-3 flex size-12 items-center justify-center rounded-xl bg-background-section text-text-quaternary">
        {icon}
      </div>
      <h3 className="text-text-secondary system-md-medium">{title}</h3>
      {description && (
        <p className="mt-1 max-w-sm text-center text-text-tertiary system-sm-regular">{description}</p>
      )}
      {action && (
        <div className="mt-4">{action}</div>
      )}
    </div>
  )
}

export default AdminEmptyState
