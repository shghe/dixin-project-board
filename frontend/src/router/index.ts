import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/login/LoginView.vue'), meta: { public: true } },
    { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
    { path: '/users', name: 'Users', component: () => import('@/views/users/UserList.vue') },
    { path: '/employees', name: 'Employees', component: () => import('@/views/employees/EmployeeList.vue') },
    { path: '/projects', name: 'Projects', component: () => import('@/views/projects/ProjectList.vue') },
    { path: '/projects/:id', name: 'ProjectDetail', component: () => import('@/views/projects/ProjectDetail.vue') },
    { path: '/projects/:id/budget', name: 'ProjectBudget', component: () => import('@/views/projects/ProjectBudget.vue') },
    { path: '/projects/:id/finance', name: 'ProjectFinance', component: () => import('@/views/projects/ProjectFinance.vue') },
    { path: '/executions', name: 'Executions', component: () => import('@/views/executions/ExecutionList.vue') },
    { path: '/my-work', name: 'MyWorkLog', component: () => import('@/views/personal/MyWorkLog.vue') },
    { path: '/reports/personnel', name: 'PersonnelReport', component: () => import('@/views/reports/PersonnelReport.vue') },
    { path: '/account/password', name: 'ChangePassword', component: () => import('@/views/account/ChangePassword.vue') },
    { path: '/', redirect: '/dashboard' },
  ],
})

router.beforeEach((to, _from, next) => {
  if (to.meta.public) { next(); return }
  if (!useAuthStore().token) { next('/login'); return }
  next()
})

export default router
