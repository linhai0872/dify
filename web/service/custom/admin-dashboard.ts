/**
 * [CUSTOM] Admin dashboard API service for multi-workspace permission control.
 */

import { useQuery } from '@tanstack/react-query'
import { get } from '../base'

export type DashboardStats = {
  total_users: number
  active_users: number
  banned_users: number
  total_workspaces: number
}

const NAME_SPACE = 'custom-admin'

export const dashboardQueryKeys = {
  stats: [NAME_SPACE, 'dashboard'] as const,
}

/**
 * Fetch admin dashboard statistics.
 */
export const useAdminDashboard = () => {
  return useQuery<DashboardStats>({
    queryKey: dashboardQueryKeys.stats,
    queryFn: () => get<DashboardStats>('/custom/admin/dashboard'),
  })
}
