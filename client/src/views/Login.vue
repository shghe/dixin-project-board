<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-center text-gray-800 mb-8">地信院项目看板</h1>

      <div v-if="!showRegister">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="username"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="请输入密码"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">验证码</label>
            <div class="flex space-x-2">
              <input
                v-model="captcha"
                type="text"
                required
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="请输入验证码"
              />
              <img
                :src="captchaUrl"
                @click="refreshCaptcha"
                class="cursor-pointer rounded border border-gray-300"
                alt="验证码"
                title="点击刷新"
              />
            </div>
          </div>

          <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <p class="mt-4 text-center text-sm text-gray-500">
          默认账号: admin / admin123
        </p>
        <p class="mt-2 text-center text-sm text-blue-600">
          <button @click="showRegister = true" class="hover:underline">注册新账号</button>
        </p>
      </div>

      <div v-else>
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
            <input
              v-model="registerForm.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="请输入姓名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input
              v-model="registerForm.username"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="请输入用户名"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
            <input
              v-model="registerForm.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              placeholder="请输入密码"
            />
          </div>

          <div v-if="registerError" class="text-red-500 text-sm">{{ registerError }}</div>
          <div v-if="registerSuccess" class="text-green-500 text-sm">{{ registerSuccess }}</div>

          <div class="flex space-x-2">
            <button
              type="button"
              @click="showRegister = false"
              class="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
            >
              返回登录
            </button>
            <button
              type="submit"
              :disabled="loading"
              class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              {{ loading ? '注册中...' : '注册' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api/index.js';

const router = useRouter();
const username = ref('');
const password = ref('');
const captcha = ref('');
const error = ref('');
const loading = ref(false);
const captchaUrl = ref('');

const showRegister = ref(false);
const registerForm = ref({ username: '', password: '', name: '' });
const registerError = ref('');
const registerSuccess = ref('');

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

function refreshCaptcha() {
  captchaUrl.value = `${API_BASE}/captcha?t=${Date.now()}`;
}

async function handleLogin() {
  error.value = '';
  loading.value = true;

  try {
    const response = await api.post('/auth/login', {
      username: username.value,
      password: password.value,
      captcha: captcha.value
    });
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    router.push('/');
  } catch (err) {
    error.value = err.response?.data?.error || '登录失败';
    refreshCaptcha();
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  registerError.value = '';
  registerSuccess.value = '';
  loading.value = true;

  try {
    await api.post('/auth/register', registerForm.value);
    registerSuccess.value = '注册成功，请登录！';
    registerForm.value = { username: '', password: '', name: '' };
    refreshCaptcha();
    setTimeout(() => {
      showRegister.value = false;
    }, 1500);
  } catch (err) {
    registerError.value = err.response?.data?.error || '注册失败';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  refreshCaptcha();
});
</script>
