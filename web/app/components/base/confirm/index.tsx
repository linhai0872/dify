/**
 * @deprecated Use `@/app/components/base/ui/alert-dialog` instead.
 * See issue #32767 for migration details.
 */

import * as React from 'react'
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { useTranslation } from 'react-i18next'
// [CUSTOM] Updated imports: base/button → dify-ui/button (removed in 1.14.0)
import { Button } from '@langgenius/dify-ui/button'

/** @deprecated Use `@/app/components/base/ui/alert-dialog` instead. */
export type IConfirm = {
  className?: string
  isShow: boolean
  type?: 'info' | 'warning' | 'danger'
  title: string
  content?: React.ReactNode
  confirmText?: string | null
  onConfirm: () => void
  cancelText?: string
  onCancel: () => void
  isLoading?: boolean
  isDisabled?: boolean
  showConfirm?: boolean
  showCancel?: boolean
  maskClosable?: boolean
  confirmInputLabel?: string
  confirmInputPlaceholder?: string
  confirmInputValue?: string
  onConfirmInputChange?: (value: string) => void
  confirmInputMatchValue?: string
}

function Confirm({
  isShow,
  type = 'warning',
  title,
  content,
  confirmText,
  cancelText,
  onConfirm,
  onCancel,
  showConfirm = true,
  showCancel = true,
  isLoading = false,
  isDisabled = false,
  maskClosable = true,
  confirmInputLabel,
  confirmInputPlaceholder,
  confirmInputValue = '',
  onConfirmInputChange,
  confirmInputMatchValue,
}: IConfirm) {
  const { t } = useTranslation()
  const dialogRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLDivElement>(null)
  const [isVisible, setIsVisible] = useState(isShow)

  const confirmTxt = confirmText || `${t('operation.confirm', { ns: 'common' })}`
  const cancelTxt = cancelText || `${t('operation.cancel', { ns: 'common' })}`
  const isConfirmDisabled = isDisabled || (confirmInputMatchValue ? confirmInputValue !== confirmInputMatchValue : false)

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape')
        onCancel()
      if (event.key === 'Enter' && isShow && !isConfirmDisabled) {
        event.preventDefault()
        onConfirm()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [onCancel, onConfirm, isShow, isConfirmDisabled])

  const handleClickOutside = (event: MouseEvent) => {
    if (maskClosable && dialogRef.current && !dialogRef.current.contains(event.target as Node))
      onCancel()
  }

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [maskClosable])

  useEffect(() => {
    if (isShow) {
      setIsVisible(true)
    }
    else {
      // [CUSTOM] Reduced from 200ms to 100ms for snappier close feel
      const timer = setTimeout(() => setIsVisible(false), 100)
      return () => clearTimeout(timer)
    }
  }, [isShow])

  if (!isVisible)
    return null

  return createPortal(
    <div
      className="fixed inset-0 z-[10000000] flex items-center justify-center bg-background-overlay"
      onClick={(e) => {
        e.preventDefault()
        e.stopPropagation()
      }}
      data-testid="confirm-overlay"
    >
      <div ref={dialogRef} className="relative w-full max-w-[480px] overflow-hidden">
        <div className="shadows-shadow-lg flex max-w-full flex-col items-start rounded-2xl border-[0.5px] border-solid border-components-panel-border bg-components-panel-bg">
          <div className="flex flex-col items-start gap-2 self-stretch pb-4 pl-6 pr-6 pt-6">
            <div ref={titleRef} className="w-full truncate text-text-primary title-2xl-semi-bold" title={title}>
              {title}
            </div>
            <div className="w-full whitespace-pre-wrap break-words text-text-tertiary system-md-regular">{content}</div>
            {confirmInputLabel && (
              <div className="mt-2">
                <label className="mb-1 block text-text-secondary system-sm-regular">
                  {confirmInputLabel}
                </label>
                <input
                  type="text"
                  className="border-components-input-border bg-components-input-bg focus:border-components-input-border-focus focus:ring-components-input-border-focus h-9 w-full rounded-lg border px-3 text-sm text-text-primary placeholder:text-text-quaternary focus:outline-none focus:ring-1"
                  placeholder={confirmInputPlaceholder}
                  value={confirmInputValue}
                  onChange={e => onConfirmInputChange?.(e.target.value)}
                />
              </div>
            )}
          </div>
          <div className="flex items-start justify-end gap-2 self-stretch p-6">
            {showCancel && <Button onClick={onCancel}>{cancelTxt}</Button>}
            {showConfirm && <Button variant="primary" tone={type !== 'info' ? 'destructive' : 'default'} disabled={isConfirmDisabled || isLoading} onClick={onConfirm}>{confirmTxt}</Button>}
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}

export default React.memo(Confirm)
