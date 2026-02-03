'use client'
/**
 * [CUSTOM] Hook for formatting log timestamps with unified timezone support.
 *
 * This hook provides consistent timezone handling for log displays across all users.
 * When DIFY_CUSTOM_LOG_TIMEZONE is configured, all users will see log times in the
 * same timezone, regardless of their individual timezone settings.
 *
 * Priority:
 * 1. If system's log_timezone is set (via DIFY_CUSTOM_LOG_TIMEZONE), use that
 * 2. Otherwise, fall back to user's individual timezone setting
 *
 * Usage:
 * ```tsx
 * const { formatTime, formatDate, effectiveTimezone } = useCustomLogTimestamp()
 * // Format Unix timestamp
 * formatTime(1704067200, 'YYYY-MM-DD HH:mm:ss')
 * // Format ISO date string
 * formatDate('2024-01-01T00:00:00Z', 'YYYY-MM-DD HH:mm:ss')
 * ```
 */
import dayjs from 'dayjs'
import timezone from 'dayjs/plugin/timezone'
import utc from 'dayjs/plugin/utc'
import { useCallback } from 'react'
import { useAppContext } from '@/context/app-context'
import { useGlobalPublicStore } from '@/context/global-public-context'

dayjs.extend(utc)
dayjs.extend(timezone)

const useCustomLogTimestamp = () => {
  const { userProfile: { timezone: userTimezone } } = useAppContext()
  const systemFeatures = useGlobalPublicStore(s => s.systemFeatures)

  // Use system log timezone if configured, otherwise fall back to user timezone
  const effectiveTimezone = systemFeatures.log_timezone || userTimezone

  /**
   * Format Unix timestamp to string with effective timezone
   */
  const formatTime = useCallback((value: number, format: string) => {
    return dayjs.unix(value).tz(effectiveTimezone).format(format)
  }, [effectiveTimezone])

  /**
   * Format ISO date string to string with effective timezone
   */
  const formatDate = useCallback((value: string, format: string) => {
    return dayjs(value).tz(effectiveTimezone).format(format)
  }, [effectiveTimezone])

  return {
    formatTime,
    formatDate,
    effectiveTimezone,
    // Flag to indicate if unified timezone is active
    isUnifiedTimezone: !!systemFeatures.log_timezone,
  }
}

export default useCustomLogTimestamp
