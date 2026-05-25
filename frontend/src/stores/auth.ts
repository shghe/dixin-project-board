import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  function checkAuth() {
    if (token.value) {
      fetchUser()
    }
  }

  async function login(username: string, password: string, captcha_id: string, captcha_code: string) {
    user.value = null
    const res = await authApi.login({ username, password, captcha_id, captcha_code })
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    user.value = {
      id: res.id,
      username: res.username,
      role: res.role,
      employee_id: res.employee_id,
      employee_name: res.employee_name,
    }
    return res
  }

  async function fetchUser() {
    const requestToken = token.value
    try {
      const res = await authApi.me()
      user.value = res
    } catch {
      if (token.value === requestToken) {
        logout()
      }
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, login, logout, checkAuth, fetchUser }
})
