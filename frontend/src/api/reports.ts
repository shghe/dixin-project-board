import { get } from './request'

export interface RecentProject {
  id: string; name: string; status: string
  manager_name: string | null; created_at: string | null
  accumulated_cost: number
}

export interface RecentExecution {
  id: string; project_name: string; record_date: string
  daily_cost: number; seq_number: number
}

export interface DashboardStats {
  total_projects: number; active_projects: number
  total_contract: number; total_cost: number; total_received: number
  total_employees: number; month_cost: number; budget_total: number
  project_statuses: Record<string, number>
  monthly_trend: { month: string; cost: number }[]
  recent_projects: RecentProject[]
  recent_executions: RecentExecution[]
}

export interface PersonnelStats {
  employee_id: string
  employee_name: string
  work_type: string
  department: string
  total_hours: number
  total_cost: number
  work_days: number
  projects: { name: string; hours: number; cost: number }[]
}

export const reportsApi = {
  dashboard: () => get<DashboardStats>('/dashboard/stats'),
  personnel: (params?: any) => get<{ year: number; items: PersonnelStats[] }>('/reports/personnel', params),
}
