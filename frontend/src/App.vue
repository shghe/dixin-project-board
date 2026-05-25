<template>
  <div id="app-container">
    <!-- PC 端布局 -->
    <template v-if="!isMobile">
      <el-container class="layout-pc">
        <el-aside v-if="authStore.isLoggedIn" width="220px" class="sidebar">
          <SideMenu />
        </el-aside>
        <el-container>
          <el-header v-if="authStore.isLoggedIn" class="pc-header">
            <HeaderBar />
          </el-header>
          <el-main>
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </template>

    <!-- 移动端布局 -->
    <template v-else>
      <div v-if="authStore.isLoggedIn" class="mobile-tabbar">
        <router-view />
        <van-tabbar v-model="mobileActive" route>
          <van-tabbar-item icon="home-o" to="/dashboard">首页</van-tabbar-item>
          <van-tabbar-item icon="orders-o" to="/projects">项目</van-tabbar-item>
          <van-tabbar-item v-if="canViewExec" icon="clock-o" to="/executions">执行单</van-tabbar-item>
          <van-tabbar-item icon="user-o" to="/employees">人员</van-tabbar-item>
          <van-tabbar-item icon="apps-o" @click="showMoreMenu = true">更多</van-tabbar-item>
        </van-tabbar>
        <van-action-sheet
          v-model:show="showMoreMenu"
          :actions="mobileMenuActions"
          cancel-text="取消"
          close-on-click-action
          @select="handleMobileMenuSelect"
        />
      </div>
      <div v-else class="mobile-full">
        <router-view />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import SideMenu from './components/SideMenu.vue'
import HeaderBar from './components/HeaderBar.vue'

const authStore = useAuthStore()
const router = useRouter()
const mobileActive = ref('')
const showMoreMenu = ref(false)
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)
const canViewExec = computed(() => ['director','manager'].includes(authStore.user?.role||''))
const isDirector = computed(() => authStore.user?.role === 'director')
const mobileMenuActions = computed(() => {
  const actions = [
    { name: '我的工时', path: '/my-work' },
    { name: '人员报表', path: '/reports/personnel' },
    { name: '修改密码', path: '/account/password' },
    { name: '退出登录', path: '/login', danger: true },
  ]
  if (isDirector.value) {
    actions.unshift({ name: '账号管理', path: '/users' })
  }
  return actions
})

const onResize = () => {
  windowWidth.value = window.innerWidth
}

function handleMobileMenuSelect(action: { path: string }) {
  if (action.path === '/login') {
    authStore.logout()
  }
  router.push(action.path)
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  authStore.checkAuth()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
#app-container {
  min-height: 100vh;
  background: #f5f7fa;
}
.layout-pc {
  min-height: 100vh;
}
.sidebar {
  background: #001529;
}
.pc-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.el-main {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
.mobile-tabbar {
  padding-bottom: 50px;
  min-height: 100vh;
}
.mobile-full {
  min-height: 100vh;
}
</style>
