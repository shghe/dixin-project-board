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
  monthly: { month: number; hours: number; cost: number }[]
}

export interface DailyProjectEntry {
  project_name: string
  work_hours: number
  work_content: string
}

export interface DailyPersonalEntry {
  id: string
  work_hours: number
  work_content: string
  category: string
}

export interface PersonnelDay {
  date: string
  project_entries: DailyProjectEntry[]
  personal_entries: DailyPersonalEntry[]
  project_hours: number
  personal_hours: number
  total_hours: number
}

export interface PersonnelDailyItem {
  employee_id: string
  employee_name: string
  work_type: string
  department: string
  personnel_type: string
  total_project_hours: number
  total_personal_hours: number
  total_hours: number
  work_days: number
  days: PersonnelDay[]
}

export const reportsApi = {
  dashboard: () => get<DashboardStats>('/dashboard/stats'),
  personnel: (params?: any) => get<{ year: number; items: PersonnelStats[] }>('/reports/personnel', params),
  personnelDaily: (params: { year: number; month: number; employee_id?: string }) =>
    get<{ year: number; month: number; items: PersonnelDailyItem[] }>('/reports/personnel-daily', params),
}
