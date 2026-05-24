import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const instance: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

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
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
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
