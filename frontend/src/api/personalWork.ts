import { get, post, put, del } from './request'

export interface PersonalWorkEntryItem {
  id: string; employee_id: string; employee_name: string | null
  record_date: string; work_hours: number
  work_content: string | null; category: string
  created_at: string
}

export interface ProjectBreakdown {
  project_name: string
  hours: number
}

export interface ProjectDetail {
  project_name: string
  work_hours: number
  work_content: string
}

export interface DailySummary {
  record_date: string
  project_hours: number
  project_breakdown: ProjectBreakdown[]
  project_details: ProjectDetail[]
  personal_hours: number
  total_hours: number
  remaining: number
  entries: { id: string; work_hours: number; work_content: string; category: string }[]
}

export const personalWorkApi = {
  list: (params?: any) => get<PersonalWorkEntryItem[]>('/personal-work', params),
  create: (data: any) => post<PersonalWorkEntryItem>('/personal-work', data),
  update: (id: string, data: any) => put<PersonalWorkEntryItem>(`/personal-work/${id}`, data),
  delete: (id: string) => del(`/personal-work/${id}`),
  dailySummary: (recordDate: string) => get<DailySummary>('/personal-work/daily-summary', { record_date: recordDate }),
}
