'use client'

import type { FC, ReactNode } from 'react'
import { cn } from '@/utils/classnames'

export type StatCardProps = {
  icon: ReactNode
  label: string
  value: number | string
  iconClassName?: string
  className?: string
}

const StatCard: FC<StatCardProps> = ({
  icon,
  label,
  value,
  iconClassName,
  className,
}) => {
  return (
    <div className={cn(
      'flex items-center gap-4 rounded-xl border border-divider-subtle bg-components-panel-bg px-5 py-4',
      className,
    )}
    >
      <div className={cn(
        'flex size-10 shrink-0 items-center justify-center rounded-lg',
        iconClassName || 'bg-util-colors-blue-brand-blue-brand-50',
      )}
      >
        {icon}
      </div>
      <div className="min-w-0">
        <div className="system-2xl-semibold text-text-primary">{value}</div>
        <div className="system-xs-regular text-text-tertiary">{label}</div>
      </div>
    </div>
  )
}

export default StatCard
