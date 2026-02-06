/**
 * [CUSTOM] Breadcrumb navigation component for multi-workspace admin.
 *
 * Displays hierarchical navigation path for admin pages.
 */
'use client'

import type { FC } from 'react'
import { RiArrowRightSLine } from '@remixicon/react'
import Link from 'next/link'
import { cn } from '@/utils/classnames'

export type BreadcrumbItem = {
  label: string
  href?: string
}

export type AdminBreadcrumbProps = {
  items: BreadcrumbItem[]
  className?: string
}

/**
 * [CUSTOM] Breadcrumb navigation component for admin pages.
 * Displays hierarchical navigation path.
 */
const AdminBreadcrumb: FC<AdminBreadcrumbProps> = ({
  items,
  className,
}) => {
  return (
    <nav
      aria-label="Breadcrumb"
      className={cn(
        'flex items-center gap-1 text-sm',
        className,
      )}
    >
      {items.map((item, index) => {
        const isLast = index === items.length - 1

        return (
          <div key={index} className="flex items-center gap-1">
            {index > 0 && (
              <RiArrowRightSLine className="size-4 text-text-quaternary" />
            )}
            {item.href && !isLast
              ? (
                  <Link
                    href={item.href}
                    className="text-text-tertiary transition-colors hover:text-text-secondary"
                  >
                    {item.label}
                  </Link>
                )
              : (
                  <span className={cn(
                    isLast ? 'font-medium text-text-secondary' : 'text-text-tertiary',
                  )}
                  >
                    {item.label}
                  </span>
                )}
          </div>
        )
      })}
    </nav>
  )
}

export default AdminBreadcrumb
