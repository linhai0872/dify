/**
 * [CUSTOM] Date formatting utilities for admin pages.
 */

export function formatDate(timestamp: number | null | undefined): string {
  if (!timestamp)
    return '-'
  return new Date(timestamp * 1000).toLocaleDateString()
}
