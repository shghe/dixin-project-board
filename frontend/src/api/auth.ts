import { post, get } from './request'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  id: string
  username: string
  role: string
  employee_id: string | null
  employee_name: string | null
}

export interface UserInfo {
  id: string
  username: string
  role: string
  employee_id: string | null
  employee_name: string | null
}

export const authApi = {
  login: (data: LoginRequest) => post<LoginResponse>('/auth/login', data),
  me: () => get<UserInfo>('/auth/me'),
}
