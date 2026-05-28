import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const instance: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

function getAuthHeader(headers: unknown): string {
  const headerBag = headers as Record<string, unknown> & { get?: (name: string) => unknown }
  if (!headerBag) return ''
  if (typeof headerBag.get === 'function') {
    const value = headerBag.get('Authorization') ?? headerBag.get('authorization')
    return typeof value === 'string' ? value : ''
  }
  const value = headerBag.Authorization ?? headerBag.authorization
  return typeof value === 'string' ? value : ''
}

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    let msg: string
    if (Array.isArray(detail)) {
      msg = detail.map((e: any) => e.msg || JSON.stringify(e)).join('; ')
    } else if (typeof detail === 'string' && detail.trim()) {
      msg = detail
    } else {
      msg = error.message || '请求失败'
    }
    if (status === 401) {
      const requestAuthHeader = getAuthHeader(error.config?.headers)
      const currentToken = localStorage.getItem('token')
      const requestToken = requestAuthHeader.startsWith('Bearer ')
        ? requestAuthHeader.slice(7)
        : ''
      const isLoginRequest = error.config?.url === '/auth/login'
      const isStaleAuthRequest = Boolean(requestToken && currentToken && requestToken !== currentToken)

      if (isLoginRequest) {
        ElMessage.error(msg)
      } else if (!isStaleAuthRequest) {
        ElMessage.error(msg)
        localStorage.removeItem('token')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      return Promise.reject(error)
    }
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export async function get<T>(url: string, params?: any): Promise<T> {
  const res = await instance.get<T>(url, { params })
  return res.data
}

export async function post<T>(url: string, data?: any): Promise<T> {
  const res = await instance.post<T>(url, data)
  return res.data
}

export async function put<T>(url: string, data?: any): Promise<T> {
  const res = await instance.put<T>(url, data)
  return res.data
}

export async function del<T>(url: string): Promise<T> {
  const res = await instance.delete<T>(url)
  return res.data
}

export default instance
