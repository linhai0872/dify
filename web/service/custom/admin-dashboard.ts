import { get } from '@/service/base'
import { useQuery } from '@tanstack/react-query'

type DashboardStats = {
  total_users: number
  active_users: number
  banned_users: number
  total_workspaces: number
}

export const useAdminDashboard = () => {
  return useQuery<DashboardStats>({
    queryKey: ['admin', 'dashboard'],
    queryFn: () => get<DashboardStats>('/console/api/custom/admin/dashboard'),
  })
}
