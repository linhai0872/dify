'use client'

// [CUSTOM] 二开: 日期时间范围选择器组件
import type { Dayjs } from 'dayjs'
import { RiCalendarLine, RiCloseLine } from '@remixicon/react'
import dayjs from 'dayjs'
import { useCallback, useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  PortalToFollowElem,
  PortalToFollowElemContent,
  PortalToFollowElemTrigger,
} from '@/app/components/base/portal-to-follow-elem'
import { cn } from '@/utils/classnames'

type CustomDatetimeRangePickerProps = {
  startDate: Dayjs | null
  endDate: Dayjs | null
  onChange: (start: Dayjs, end: Dayjs) => void
  onClear: () => void
  displayFormat?: string
}

const DISPLAY_FORMAT = 'YYYY-MM-DD HH:mm'
const INPUT_FORMAT = 'YYYY-MM-DDTHH:mm'

const CustomDatetimeRangePicker = ({
  startDate,
  endDate,
  onChange,
  onClear,
  displayFormat = DISPLAY_FORMAT,
}: CustomDatetimeRangePickerProps) => {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)
  const [localStart, setLocalStart] = useState<string>('')
  const [localEnd, setLocalEnd] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [maxDateTime, setMaxDateTime] = useState<string>('')

  const handleOpenChange = useCallback((open: boolean) => {
    setIsOpen(open)
    if (open) {
      // Sync local state from props when opening
      setLocalStart(startDate ? startDate.format(INPUT_FORMAT) : '')
      setLocalEnd(endDate ? endDate.format(INPUT_FORMAT) : '')
      setMaxDateTime(dayjs().format(INPUT_FORMAT))
      setError('')
    }
  }, [startDate, endDate])

  const handleConfirm = useCallback(() => {
    if (!localStart || !localEnd) {
      setError(t('overview.dateTimeRange.bothRequired', { ns: 'custom' }))
      return
    }
    const start = dayjs(localStart)
    const end = dayjs(localEnd)
    if (!start.isValid() || !end.isValid()) {
      setError(t('overview.dateTimeRange.invalidDate', { ns: 'custom' }))
      return
    }
    if (start.isAfter(end)) {
      setError(t('overview.dateTimeRange.startBeforeEnd', { ns: 'custom' }))
      return
    }
    setError('')
    onChange(start, end)
    setIsOpen(false)
  }, [localStart, localEnd, onChange, t])

  const handleClear = useCallback(() => {
    setLocalStart('')
    setLocalEnd('')
    setError('')
    onClear()
    setIsOpen(false)
  }, [onClear])

  const handleTriggerClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    handleOpenChange(!isOpen)
  }, [isOpen, handleOpenChange])

  const hasValue = startDate && endDate
  const displayText = hasValue
    ? `${startDate.format(displayFormat)} ~ ${endDate.format(displayFormat)}`
    : ''

  return (
    <PortalToFollowElem
      open={isOpen}
      onOpenChange={handleOpenChange}
      placement="bottom-start"
    >
      <PortalToFollowElemTrigger>
        <div
          className={cn(
            'group flex h-9 cursor-pointer items-center gap-x-1 rounded-lg border-0 bg-components-input-bg-normal pl-3 pr-2 transition-colors hover:bg-state-base-hover-alt',
            hasValue ? 'w-auto' : 'w-[220px]',
          )}
          onClick={handleTriggerClick}
        >
          <RiCalendarLine className="h-4 w-4 shrink-0 text-text-quaternary" />
          {hasValue
            ? (
                <span className="system-sm-regular truncate text-components-input-text-filled">
                  {displayText}
                </span>
              )
            : (
                <span className="system-sm-regular text-components-input-text-placeholder">
                  {t('overview.dateTimeRange.placeholder', { ns: 'custom' })}
                </span>
              )}
          {hasValue && (
            <RiCloseLine
              className="ml-0.5 hidden h-3.5 w-3.5 shrink-0 text-text-quaternary hover:text-text-secondary group-hover:block"
              onClick={(e) => {
                e.stopPropagation()
                handleClear()
              }}
            />
          )}
        </div>
      </PortalToFollowElemTrigger>
      <PortalToFollowElemContent className="z-[11]">
        <div className="mt-1 w-[320px] rounded-xl border-[0.5px] border-components-panel-border bg-components-panel-bg p-3 shadow-lg shadow-shadow-shadow-5">
          <div className="mb-3 flex flex-col gap-2">
            <div>
              <label className="system-xs-medium mb-1 block text-text-secondary">
                {t('overview.dateTimeRange.startTime', { ns: 'custom' })}
              </label>
              <input
                type="datetime-local"
                className="system-xs-regular w-full rounded-lg border-[0.5px] border-components-input-border-active bg-components-input-bg-normal px-2 py-1.5 text-components-input-text-filled outline-none transition-colors focus:border-components-input-border-active focus:shadow-xs"
                value={localStart}
                max={maxDateTime}
                onChange={e => setLocalStart(e.target.value)}
              />
            </div>
            <div>
              <label className="system-xs-medium mb-1 block text-text-secondary">
                {t('overview.dateTimeRange.endTime', { ns: 'custom' })}
              </label>
              <input
                type="datetime-local"
                className="system-xs-regular w-full rounded-lg border-[0.5px] border-components-input-border-active bg-components-input-bg-normal px-2 py-1.5 text-components-input-text-filled outline-none transition-colors focus:border-components-input-border-active focus:shadow-xs"
                value={localEnd}
                max={maxDateTime}
                onChange={e => setLocalEnd(e.target.value)}
              />
            </div>
          </div>
          {error && (
            <p className="system-xs-regular mb-2 text-text-destructive">{error}</p>
          )}
          <div className="flex items-center justify-end gap-2">
            <button
              type="button"
              className="system-xs-medium rounded-lg px-3 py-1.5 text-text-secondary transition-colors hover:bg-state-base-hover"
              onClick={handleClear}
            >
              {t('overview.dateTimeRange.clear', { ns: 'custom' })}
            </button>
            <button
              type="button"
              className="system-xs-medium rounded-lg bg-primary-600 px-3 py-1.5 text-white transition-colors hover:bg-primary-700"
              onClick={handleConfirm}
            >
              {t('overview.dateTimeRange.confirm', { ns: 'custom' })}
            </button>
          </div>
        </div>
      </PortalToFollowElemContent>
    </PortalToFollowElem>
  )
}

export default CustomDatetimeRangePicker
// [/CUSTOM]
