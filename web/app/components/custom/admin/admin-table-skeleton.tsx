'use client'

import type { FC } from 'react'
import { cn } from '@/utils/classnames'

export type AdminTableSkeletonProps = {
  columns?: number
  rows?: number
  className?: string
}

const ShimmerBar: FC<{ width?: string, className?: string }> = ({ width = 'w-24', className }) => (
  <div className={cn('h-3 animate-pulse rounded bg-state-base-hover', width, className)} />
)

const AdminTableSkeleton: FC<AdminTableSkeletonProps> = ({
  columns = 5,
  rows = 5,
  className,
}) => {
  return (
    <div className={cn('min-w-[800px]', className)}>
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="flex items-center border-b border-divider-subtle py-3">
          {/* Avatar + name column */}
          <div className="flex grow items-center gap-3 px-4">
            <div className="size-8 animate-pulse rounded-full bg-state-base-hover" />
            <div className="space-y-1.5">
              <ShimmerBar width="w-28" />
              <ShimmerBar width="w-40" className="h-2.5" />
            </div>
          </div>
          {/* Remaining columns */}
          {Array.from({ length: columns - 1 }).map((_, colIdx) => (
            <div key={colIdx} className="w-[120px] shrink-0 px-3">
              <ShimmerBar width={colIdx % 2 === 0 ? 'w-16' : 'w-20'} />
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

export default AdminTableSkeleton
