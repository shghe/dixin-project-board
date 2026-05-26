<template>
  <div class="login-page">
    <div class="login-card">
      <h1>项目管理系统</h1>
      <p class="subtitle">华北地质勘查局第四地质大队 · 地理信息院</p>
      <el-form ref="formRef" :model="form" :rules="rules" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" autocomplete="username" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" show-password autocomplete="current-password" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item prop="captcha_code">
          <div class="captcha-row">
            <el-input v-model="form.captcha_code" placeholder="验证码" maxlength="4" prefix-icon="Key" @keyup.enter="handleLogin" />
            <button class="captcha-image" type="button" :disabled="captchaLoading" @click="loadCaptcha">
              <img v-if="captchaImage" :src="captchaImage" alt="验证码" />
              <span v-else>刷新</span>
            </button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
      <p v-if="showHint" class="hint">测试账号：{{ defaultUsername }} / {{ defaultPassword }}</p>
      <p class="version">v1.2.0</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)
const captchaLoading = ref(false)
const captchaImage = ref('')
const formRef = ref()
const defaultUsername = import.meta.env.DEV ? import.meta.env.VITE_DEMO_USERNAME || '' : ''
const defaultPassword = import.meta.env.DEV ? import.meta.env.VITE_DEMO_PASSWORD || '' : ''
const showHint = Boolean(defaultUsername && defaultPassword)

const form = reactive({ username: defaultUsername, password: defaultPassword, captcha_id: '', captcha_code: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const res = await authApi.captcha()
    form.captcha_id = res.captcha_id
    form.captcha_code = ''
    captchaImage.value = res.image
  } finally {
    captchaLoading.value = false
  }
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (!form.captcha_id) {
    ElMessage.warning('请刷新验证码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.username.trim(), form.password, form.captcha_id, form.captcha_code)
    router.push('/dashboard')
  } catch (error) {
    await loadCaptcha()
    throw error
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
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
.version {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  margin-top: 16px;
}
.captcha-row {
  display: flex;
  width: 100%;
  gap: 10px;
}
.captcha-row .el-input {
  flex: 1;
}
.captcha-image {
  width: 140px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #f5f7fa;
  cursor: pointer;
  overflow: hidden;
  padding: 0;
  flex-shrink: 0;
}
.captcha-image img {
  display: block;
  width: 100%;
  height: 100%;
}
.captcha-image span {
  color: #909399;
}

@media (max-width: 420px) {
  .captcha-row {
    gap: 8px;
  }

  .captcha-image {
    width: 120px;
  }
}
</style>
