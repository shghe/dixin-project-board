import { post, get } from './request'

export interface LoginRequest {
  username: string
  password: string
  captcha_id: string
  captcha_code: string
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

export interface CaptchaResponse {
  captcha_id: string
  image: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export const authApi = {
  login: (data: LoginRequest) => post<LoginResponse>('/auth/login', data),
  me: () => get<UserInfo>('/auth/me'),
  captcha: () => get<CaptchaResponse>('/auth/captcha'),
  changePassword: (data: ChangePasswordRequest) => post<{ message: string }>('/auth/change-password', data),
}
