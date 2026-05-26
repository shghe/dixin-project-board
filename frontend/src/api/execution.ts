import { get, post, put, del } from './request'

export interface ExecutionDetailItem {
  employee_id: string; employee_name?: string | null
  work_hours: number; daily_rate: number; cost: number
  work_content: string | null; is_leave: boolean; leave_reason: string | null
}

export interface ExecutionItem {
  id: string; project_id: string; project_name: string | null
  record_date: string; seq_number: number
  subcontract_fee: number; inhouse_personnel: number
  enterprise_personnel: number; dispatched_personnel: number
  relevant_fee: number; material_fee: number; labor_fee: number
  rental_fee: number; transport_fee: number; office_fee: number
  entertainment_fee: number; other_fee: number; travel_fee: number
  bidding_fee: number; commission_fee: number; tax_fee: number
  daily_cost: number; cumulative_cost: number
  cumulative_profit: number; profit_rate: number
  remark: string | null; status: string; registrant: string; reviewer: string | null
  details: ExecutionDetailItem[]; created_at: string
}

export interface BudgetMap {
  [key: string]: number
}

export interface ExecutionListResponse {
  total: number; items: ExecutionItem[]
  accumulated: BudgetMap; budget: BudgetMap
}

export interface PersonnelDailyItem {
  id: string; record_date: string; employee_name: string
  work_type: string; department: string; personnel_type: string
  project_name: string; work_hours: number; work_content: string
  is_leave: boolean; leave_reason: string; cost: number
}

export interface PersonnelDailyResponse {
  total: number; items: PersonnelDailyItem[]
  total_hours: number; total_cost: number; total_days: number
}

export const executionApi = {
  list: (params?: any) => get<ExecutionListResponse>('/executions', params),
  personnelDaily: (params?: any) => get<PersonnelDailyResponse>('/executions/personnel-daily', params),
  get: (id: string) => get<ExecutionItem>(`/executions/${id}`),
  getByDate: (project_id: string, record_date: string) => get<{ found: boolean; item: ExecutionItem | null }>('/executions/by-date', { project_id, record_date }),
  create: (data: any) => post<ExecutionItem>('/executions', data),
  update: (id: string, data: any) => put<ExecutionItem>(`/executions/${id}`, data),
  delete: (id: string) => del<{ message: string }>(`/executions/${id}`),
}
