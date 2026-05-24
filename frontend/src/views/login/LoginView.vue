<template>
  <div class="login-page">
    <div class="login-card">
      <h1>项目管理系统</h1>
      <p class="subtitle">华北地质勘查局第四地质大队 · 地理信息院</p>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
      <p v-if="showHint" class="hint">测试账号：{{ defaultUsername }} / {{ defaultPassword }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)
const formRef = ref()
const defaultUsername = import.meta.env.DEV ? import.meta.env.VITE_DEMO_USERNAME || '' : ''
const defaultPassword = import.meta.env.DEV ? import.meta.env.VITE_DEMO_PASSWORD || '' : ''
const showHint = Boolean(defaultUsername && defaultPassword)

const form = reactive({ username: defaultUsername, password: defaultPassword })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  max-width: 90vw;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
h1 {
  text-align: center;
  color: #303133;
  margin-bottom: 8px;
}
.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 32px;
  font-size: 14px;
}
.hint {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  margin-top: 8px;
}
</style>
