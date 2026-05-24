import { get, post, put, del } from './request'

export interface UserItem {
  id: string
  username: string
  role: string
  employee_id: string | null
  employee_name: string | null
  is_active: boolean
  created_at: string
}

export const usersApi = {
  list: () => get<UserItem[]>('/users'),
  create: (data: any) => post<UserItem>('/users', data),
  update: (id: string, data: any) => put<UserItem>(`/users/${id}`, data),
  delete: (id: string) => del(`/users/${id}`),
}
