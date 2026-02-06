'use client'

import type { FC } from 'react'
import { RiCheckboxCircleLine, RiCloseLine, RiDeleteBinLine, RiProhibitedLine } from '@remixicon/react'
import { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import { cn } from '@/utils/classnames'

export type BatchActionBarProps = {
  selectedCount: number
  onEnable?: () => void
  onDisable?: () => void
  onDelete?: () => void
  onClear: () => void
  isLoading?: boolean
  className?: string
}

const BatchActionBar: FC<BatchActionBarProps> = ({
  selectedCount,
  onEnable,
  onDisable,
  onDelete,
  onClear,
  isLoading = false,
  className,
}) => {
  const { t } = useTranslation()

  // Escape key handler to clear selection
  useEffect(() => {
    if (selectedCount === 0)
      return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape')
        onClear()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [selectedCount, onClear])

  return (
    <div
      className={cn(
        'fixed bottom-6 left-1/2 z-50 flex -translate-x-1/2 items-center gap-3',
        'bg-components-panel-bg/95 rounded-xl border border-divider-regular px-4 py-3 shadow-lg backdrop-blur-sm',
        'transition-all duration-300 ease-out',
        selectedCount > 0
          ? 'translate-y-0 opacity-100'
          : 'pointer-events-none translate-y-4 opacity-0',
        className,
      )}
    >
      <span className="system-sm-medium text-text-secondary">
        {t('admin.selectedCount', { ns: 'custom', count: selectedCount })}
      </span>

      <div className="h-4 w-px bg-divider-regular" />

      <div className="flex items-center gap-2">
        {onEnable && (
          <Button variant="secondary" size="small" onClick={onEnable} disabled={isLoading}>
            <RiCheckboxCircleLine className="mr-1 size-4" />
            {t('admin.batchEnable', { ns: 'custom' })}
          </Button>
        )}

        {onDisable && (
          <Button variant="warning" size="small" onClick={onDisable} disabled={isLoading}>
            <RiProhibitedLine className="mr-1 size-4" />
            {t('admin.batchDisable', { ns: 'custom' })}
          </Button>
        )}

        {onDelete && (
          <Button
            variant="ghost"
            size="small"
            onClick={onDelete}
            disabled={isLoading}
            className="text-text-destructive hover:bg-state-destructive-hover"
          >
            <RiDeleteBinLine className="mr-1 size-4" />
            {t('admin.batchDelete', { ns: 'custom' })}
          </Button>
        )}
      </div>

      <div className="h-4 w-px bg-divider-regular" />

      <button
        onClick={onClear}
        disabled={isLoading}
        className="flex items-center gap-1 text-text-tertiary transition-colors hover:text-text-secondary disabled:opacity-50"
      >
        <RiCloseLine className="size-4" />
        <span className="system-xs-medium">{t('admin.clearSelection', { ns: 'custom' })}</span>
      </button>
    </div>
  )
}

export default BatchActionBar
