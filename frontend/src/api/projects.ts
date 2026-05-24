import { get, post, put, del } from './request'

export interface ProjectItem {
  id: string; project_code: string; name: string
  region_province: string | null; region_city: string | null
  party_a: string | null; party_b: string | null
  contact_person: string | null; contact_phone: string | null
  fund_source: string | null; project_nature: string | null
  status: string; manager_id: string | null; manager_name: string | null
  remark: string | null; created_at: string; updated_at: string
}

export interface ContractItem {
  id: string; project_id: string
  contract_amount: number; discount_rate: number; actual_amount: number
  sign_date: string | null; drafter: string | null; reviewer: string | null
  payment_terms: string | null
}

export interface SubcontractItem {
  id: string; project_id: string; company_name: string
  qualification: string | null; company_scale: string | null
  contact_person: string | null; contact_phone: string | null
  content: string | null; amount: number; settled_amount: number
  remark: string | null
}

export interface BudgetItemRow {
  id: string; project_id: string; category: string; sub_category: string | null
  amount: number; quantity: number; work_days: number; unit_price: number
  is_personnel: boolean; sort_order: number; remark: string | null
}

export interface TaskItem {
  id: string; project_id: string; task_name: string
  start_date: string; duration_days: number; end_date: string
  sort_order: number; remark: string | null
}

export const projectsApi = {
  list: (params?: any) => get<{ total: number; items: ProjectItem[] }>('/projects', params),
  get: (id: string) => get<ProjectItem>(`/projects/${id}`),
  create: (data: any) => post<ProjectItem>('/projects', data),
  update: (id: string, data: any) => put<ProjectItem>(`/projects/${id}`, data),
  delete: (id: string) => del(`/projects/${id}`),

  getContract: (projectId: string) => get<ContractItem>(`/projects/${projectId}/contract`),
  saveContract: (projectId: string, data: any) => post<ContractItem>(`/projects/${projectId}/contract`, data),

  // 分包
  listSubcontracts: (projectId: string) => get<SubcontractItem[]>(`/projects/${projectId}/subcontracts`),
  createSubcontract: (projectId: string, data: any) => post<SubcontractItem>(`/projects/${projectId}/subcontracts`, data),
  deleteSubcontract: (projectId: string, subId: string) => del(`/projects/${projectId}/subcontracts/${subId}`),

  // 预算（费用科目）
  listBudgetItems: (projectId: string) => get<BudgetItemRow[]>(`/projects/${projectId}/budget`),
  createBudgetItem: (projectId: string, data: any) => post<BudgetItemRow>(`/projects/${projectId}/budget`, data),
  updateBudgetItem: (projectId: string, itemId: string, data: any) => put<BudgetItemRow>(`/projects/${projectId}/budget/${itemId}`, data),
  deleteBudgetItem: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/${itemId}`),

  getFinance: (projectId: string) => get<any>(`/projects/${projectId}/finance`),

  // 财务事件
  listFinancialEvents: (projectId: string) => get<any[]>(`/projects/${projectId}/financial-events`),
  createFinancialEvent: (projectId: string, data: any) => post<any>(`/projects/${projectId}/financial-events`, data),
  updateFinancialEvent: (projectId: string, eventId: string, data: any) => put<any>(`/projects/${projectId}/financial-events/${eventId}`, data),
  deleteFinancialEvent: (projectId: string, eventId: string) => del(`/projects/${projectId}/financial-events/${eventId}`),

  // 施工横道图
  listTasks: (projectId: string) => get<TaskItem[]>(`/projects/${projectId}/tasks`),
  createTask: (projectId: string, data: any) => post<TaskItem>(`/projects/${projectId}/tasks`, data),
  updateTask: (projectId: string, taskId: string, data: any) => put<TaskItem>(`/projects/${projectId}/tasks/${taskId}`, data),
  deleteTask: (projectId: string, taskId: string) => del(`/projects/${projectId}/tasks/${taskId}`),

  // 预算 V2
  getBudgetSummary: (projectId: string) => get<any>(`/projects/${projectId}/budget/summary`),
  saveBudgetSummary: (projectId: string, data: any) => put<any>(`/projects/${projectId}/budget/summary`, data),
  getBudgetRollup: (projectId: string) => get<any>(`/projects/${projectId}/budget/rollup`),
  getBudgetExportUrl: (projectId: string) => `/api/projects/${projectId}/budget/export`,

  // 人工费
  listBudgetPersonnel: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/personnel`),
  createBudgetPersonnel: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/personnel`, data),
  updateBudgetPersonnel: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/personnel/${itemId}`, data),
  deleteBudgetPersonnel: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/personnel/${itemId}`),

  // 材料费
  listBudgetMaterial: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/material`),
  createBudgetMaterial: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/material`, data),
  updateBudgetMaterial: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/material/${itemId}`, data),
  deleteBudgetMaterial: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/material/${itemId}`),

  // 机械费
  listBudgetEquipment: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/equipment`),
  createBudgetEquipment: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/equipment`, data),
  updateBudgetEquipment: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/equipment/${itemId}`, data),
  deleteBudgetEquipment: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/equipment/${itemId}`),

  // 其他直接费
  listBudgetDirectCost: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/direct_cost`),
  createBudgetDirectCost: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/direct_cost`, data),
  updateBudgetDirectCost: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/direct_cost/${itemId}`, data),
  deleteBudgetDirectCost: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/direct_cost/${itemId}`),

  // 劳务费
  listBudgetLabor: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/labor`),
  createBudgetLabor: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/labor`, data),
  updateBudgetLabor: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/labor/${itemId}`, data),
  deleteBudgetLabor: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/labor/${itemId}`),

  // 分包工程款
  listBudgetSubcontract: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/subcontract`),
  createBudgetSubcontract: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/subcontract`, data),
  updateBudgetSubcontract: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/subcontract/${itemId}`, data),
  deleteBudgetSubcontract: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/subcontract/${itemId}`),

  // 研发+其他费用
  listBudgetRDOther: (projectId: string) => get<any[]>(`/projects/${projectId}/budget/rd_other`),
  createBudgetRDOther: (projectId: string, data: any) => post<any>(`/projects/${projectId}/budget/rd_other`, data),
  updateBudgetRDOther: (projectId: string, itemId: string, data: any) => put<any>(`/projects/${projectId}/budget/rd_other/${itemId}`, data),
  deleteBudgetRDOther: (projectId: string, itemId: string) => del(`/projects/${projectId}/budget/rd_other/${itemId}`),
}
