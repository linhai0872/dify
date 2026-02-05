'use client'

/**
 * [CUSTOM] Admin layout for multi-workspace permission control.
 *
 * Provides:
 * - Permission guard (redirect non-super_admin users)
 * - Left sidebar navigation
 * - Common layout structure for admin pages
 */

import type { ReactNode } from 'react'
import {
  RiGroupLine,
  RiTeamLine,
} from '@remixicon/react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useIsSuperAdmin } from '@/hooks/custom/use-system-role'
import { cn } from '@/utils/classnames'

type AdminLayoutProps = {
  children: ReactNode
}

const navItems = [
  {
    key: 'users',
    href: '/custom-admin/users',
    icon: RiGroupLine,
    labelKey: 'admin.userManagement' as const,
  },
  {
    key: 'workspaces',
    href: '/custom-admin/workspaces',
    icon: RiTeamLine,
    labelKey: 'admin.workspaceManagement' as const,
  },
] as const

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { t } = useTranslation()
  const router = useRouter()
  const pathname = usePathname()
  const { isSuperAdmin, isFeatureEnabled, isLoading } = useIsSuperAdmin()

  // Permission guard: redirect non-super_admin users
  useEffect(() => {
    if (!isLoading && (!isFeatureEnabled || !isSuperAdmin))
      router.replace('/apps')
  }, [isLoading, isFeatureEnabled, isSuperAdmin, router])

  // Show loading state while checking permissions
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-text-tertiary">{t('loading', { ns: 'common' })}</div>
      </div>
    )
  }

  // Don't render if user doesn't have permission
  if (!isFeatureEnabled || !isSuperAdmin)
    return null

  return (
    <div className="flex h-full">
      {/* Left Sidebar */}
      <aside className="flex w-56 shrink-0 flex-col border-r border-divider-subtle bg-background-default-subtle">
        <div className="px-4 py-3">
          <h1 className="system-lg-semibold text-text-primary">
            {t('admin.systemAdmin', { ns: 'custom' })}
          </h1>
        </div>
        <nav className="flex-1 px-2 py-2">
          {navItems.map(item => (
            <Link
              key={item.key}
              href={item.href}
              className={cn(
                'flex items-center gap-2 rounded-lg px-3 py-2 text-text-secondary transition-colors',
                'hover:bg-state-base-hover',
                pathname.startsWith(item.href) && 'bg-state-base-active text-text-primary',
              )}
            >
              <item.icon className="size-4 shrink-0" />
              <span className="system-md-regular">
                {t(item.labelKey, { ns: 'custom' })}
              </span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-background-body p-6">
        {children}
      </main>
    </div>
  )
}
