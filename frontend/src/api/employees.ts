import { get, post, put, del } from './request'

export interface EmployeeItem {
  id: string
  employee_code: string
  name: string
  work_type: string
  personnel_type: string
  department: string
  position: string | null
  phone: string | null
  daily_wage: number
  hire_date: string | null
  status: string
  remark: string | null
}

export const employeesApi = {
  list: (params?: any) => get<EmployeeItem[]>('/employees', params),
  get: (id: string) => get<EmployeeItem>(`/employees/${id}`),
  create: (data: any) => post<EmployeeItem>('/employees', data),
  update: (id: string, data: any) => put<EmployeeItem>(`/employees/${id}`, data),
  delete: (id: string) => del(`/employees/${id}`),
}
