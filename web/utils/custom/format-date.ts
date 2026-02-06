/**
 * [CUSTOM] Date formatting utility for admin pages.
 *
 * Handles both Unix timestamps (seconds) and ISO date strings,
 * returning a safely formatted date or '-' for invalid values.
 */

import type { ConfigType } from 'dayjs'
import dayjs from 'dayjs'

/**
 * Format a date value to locale date string.
 *
 * Handles:
 * - Unix timestamps in seconds (number)
 * - Unix timestamps in milliseconds (number > 1e12)
 * - ISO date strings
 * - null/undefined values
 *
 * @param timestamp - The date value to format
 * @param format - Optional dayjs format string (default: 'YYYY-MM-DD')
 * @returns Formatted date string or '-' for invalid/empty values
 */
export const formatDate = (
  timestamp: ConfigType | null | undefined,
  format = 'YYYY-MM-DD',
): string => {
  if (timestamp === null || timestamp === undefined)
    return '-'

  let date: dayjs.Dayjs

  if (typeof timestamp === 'number') {
    // Detect if timestamp is in seconds or milliseconds
    // Unix timestamps in seconds are typically < 1e12 (until year 33658)
    // Timestamps in milliseconds are typically >= 1e12
    if (timestamp > 1e12) {
      date = dayjs(timestamp) // Already in milliseconds
    }
    else {
      date = dayjs(timestamp * 1000) // Convert seconds to milliseconds
    }
  }
  else {
    date = dayjs(timestamp)
  }

  if (!date.isValid())
    return '-'

  return date.format(format)
}

/**
 * Format a date value to locale date and time string.
 *
 * @param timestamp - The date value to format
 * @returns Formatted datetime string or '-' for invalid/empty values
 */
export const formatDateTime = (
  timestamp: ConfigType | null | undefined,
): string => {
  return formatDate(timestamp, 'YYYY-MM-DD HH:mm')
}
