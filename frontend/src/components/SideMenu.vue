<template>
  <div class="side-menu">
    <div class="logo"><span v-show="!appStore.sidebarCollapsed">地理信息院</span></div>
    <el-menu :default-active="currentRoute" router background-color="#001529" text-color="#ffffffa6" active-text-color="#fff" :collapse="appStore.sidebarCollapsed">
      <el-menu-item index="/dashboard"><el-icon><Odometer /></el-icon><span>首页</span></el-menu-item>
      <el-menu-item index="/users" v-if="isDirector"><el-icon><Setting /></el-icon><span>账号管理</span></el-menu-item>
      <el-menu-item index="/employees"><el-icon><User /></el-icon><span>人员管理</span></el-menu-item>
      <el-menu-item index="/projects"><el-icon><Folder /></el-icon><span>项目管理</span></el-menu-item>
      <el-menu-item index="/executions" v-if="canViewExec"><el-icon><Tickets /></el-icon><span>每日执行单</span></el-menu-item>
      <el-menu-item index="/my-work"><el-icon><Clock /></el-icon><span>我的工时</span></el-menu-item>
      <el-menu-item index="/reports/personnel"><el-icon><DataAnalysis /></el-icon><span>人员报表</span></el-menu-item>
      <el-menu-item index="/account/password"><el-icon><Lock /></el-icon><span>修改密码</span></el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { Odometer, User, Folder, Tickets, DataAnalysis, Clock, Setting, Lock } from '@element-plus/icons-vue'

const route = useRoute()
const appStore = useAppStore()
const authStore = useAuthStore()
const currentRoute = computed(() => route.path)
const isDirector = computed(() => authStore.user?.role === '院长')
const canViewExec = computed(() => ['院长','副院长','项目经理'].includes(authStore.user?.role||''))
</script>

<style scoped>
.side-menu { height: 100vh; display: flex; flex-direction: column; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 18px; font-weight: bold; border-bottom: 1px solid rgba(255,255,255,0.1); }
.el-menu { border-right: none; flex: 1; overflow-y: auto; }
</style>
