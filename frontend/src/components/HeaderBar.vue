<template>
  <div class="header-bar">
    <el-button @click="appStore.toggleSidebar" :icon="Fold" circle />
    <div class="header-right">
      <el-tag>{{ roleLabel }}</el-tag>
      <span class="username">{{ authStore.user?.employee_name || authStore.user?.username }}</span>
      <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Fold } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const authStore = useAuthStore()
const appStore = useAppStore()
const router = useRouter()

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    director: '院长/主任',
    manager: '项目经理',
    finance: '财务',
    employee: '员工',
  }
  return map[authStore.user?.role || ''] || ''
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.header-bar {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  font-weight: 500;
}
</style>
