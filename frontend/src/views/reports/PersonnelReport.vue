<template>
  <div class="page">
    <h2>人员工时报表</h2>

    <!-- 筛选栏 -->
    <el-row :gutter="12" style="margin-top:12px" align="middle">
      <el-col :xs="12" :sm="3">
        <el-select v-model="year" placeholder="年份" @change="loadReport">
          <el-option v-for="y in yearOptions" :key="y" :label="String(y)" :value="y" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="3">
        <el-select v-model="month" placeholder="月份" @change="loadReport">
          <el-option v-for="m in 12" :key="m" :label="m + '月'" :value="m" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="4" v-if="isAdmin">
        <el-select v-model="filterEmployeeId" placeholder="全部人员" clearable filterable @change="loadReport">
          <el-option v-for="e in employeeList" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
      </el-col>
      <el-col :xs="12" :sm="6">
        <span class="summary-text" v-if="reportItems.length">
          {{ reportItems.length }}人 · 合计 {{ totalAllHours }}h · 项目 {{ totalProjectHours }}h · 非项目 {{ totalPersonalHours }}h
        </span>
      </el-col>
    </el-row>

    <!-- 每人每日明细 -->
    <div v-for="item in reportItems" :key="item.employee_id" style="margin-top:12px">
      <el-card>
        <template #header>
          <div class="emp-header" @click="item._expanded = !item._expanded" style="cursor:pointer">
            <div class="emp-info">
              <span class="emp-name">{{ item.employee_name }}</span>
              <el-tag size="small">{{ item.work_type }}</el-tag>
              <el-tag size="small" type="info">{{ item.department }}</el-tag>
              <el-tag size="small" type="warning">{{ item.personnel_type }}</el-tag>
            </div>
            <div class="emp-summary">
              <span class="emp-stat">总工时 <b>{{ item.total_hours }}h</b></span>
              <span class="emp-stat">项目 <b class="blue">{{ item.total_project_hours }}h</b></span>
              <span class="emp-stat">非项目 <b class="green">{{ item.total_personal_hours }}h</b></span>
              <span class="emp-stat">出勤 <b>{{ item.work_days }}天</b></span>
              <el-icon :class="{ expanded: item._expanded }"><ArrowDown /></el-icon>
            </div>
          </div>
        </template>

        <div v-show="item._expanded">
          <!-- 每日明细 -->
          <div v-if="item.days.length" class="day-list">
            <div v-for="day in item.days" :key="day.date" class="day-card">
              <div class="day-header">
                <span class="day-date">{{ day.date }}</span>
                <span class="day-total">{{ day.total_hours }}h</span>
                <span class="day-breakdown" v-if="day.project_hours">项目 {{ day.project_hours }}h</span>
                <span class="day-breakdown green" v-if="day.personal_hours">非项目 {{ day.personal_hours }}h</span>
              </div>

              <!-- 项目工时明细 -->
              <div v-if="day.project_entries.length" class="entry-group">
                <div class="entry-group-label">项目工作</div>
                <div v-for="(pe, i) in day.project_entries" :key="'p'+i" class="entry-row">
                  <span class="entry-project">{{ pe.project_name }}</span>
                  <span class="entry-content">{{ pe.work_content }}</span>
                  <span class="entry-hours">{{ pe.work_hours }}h</span>
                </div>
              </div>

              <!-- 非项目工时明细 -->
              <div v-if="day.personal_entries.length" class="entry-group">
                <div class="entry-group-label">非项目工作</div>
                <div v-for="(pe, i) in day.personal_entries" :key="'e'+i" class="entry-row">
                  <el-tag size="small" type="info">{{ pe.category }}</el-tag>
                  <span class="entry-content">{{ pe.work_content }}</span>
                  <span class="entry-hours">{{ pe.work_hours }}h</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="该月无工作记录" :image-size="40" />
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && reportItems.length === 0" description="暂无数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { reportsApi } from '@/api/reports'
import type { PersonnelDailyItem } from '@/api/reports'
import { employeesApi } from '@/api/employees'
import type { EmployeeItem } from '@/api/employees'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => ['院长', '综合员'].includes(authStore.user?.role || ''))

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const filterEmployeeId = ref('')
const reportItems = ref<(PersonnelDailyItem & { _expanded: boolean })[]>([])
const loading = ref(false)
const employeeList = ref<EmployeeItem[]>([])

const yearOptions = computed(() => {
  const ys = []
  for (let y = now.getFullYear(); y >= 2020; y--) ys.push(y)
  return ys
})

const totalAllHours = computed(() => reportItems.value.reduce((s, i) => s + i.total_hours, 0))
const totalProjectHours = computed(() => reportItems.value.reduce((s, i) => s + i.total_project_hours, 0))
const totalPersonalHours = computed(() => reportItems.value.reduce((s, i) => s + i.total_personal_hours, 0))

async function loadReport() {
  loading.value = true
  try {
    if (isAdmin.value && !employeeList.value.length) {
      employeeList.value = await employeesApi.list()
    }
    const params: any = { year: year.value, month: month.value }
    if (filterEmployeeId.value) params.employee_id = filterEmployeeId.value
    const res = await reportsApi.personnelDaily(params)
    reportItems.value = (res.items || []).map(i => ({ ...i, _expanded: true }))
  } finally { loading.value = false }
}

onMounted(loadReport)
</script>

<style scoped>
h2 { font-size: 20px; }
.summary-text { font-size: 14px; color: #606266; }

/* 员工卡片头部 */
.emp-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.emp-info { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.emp-name { font-weight: 700; font-size: 15px; }
.emp-summary { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.emp-stat { font-size: 13px; color: #909399; }
.emp-stat b { color: #303133; }
.emp-stat b.blue { color: #409eff; }
.emp-stat b.green { color: #67c23a; }
.emp-summary .el-icon { transition: transform 0.2s; }
.emp-summary .el-icon.expanded { transform: rotate(180deg); }

/* 每日列表 */
.day-list { max-height: 500px; overflow-y: auto; }
.day-card { border: 1px solid #ebeef5; border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; }
.day-card:last-child { margin-bottom: 0; }
.day-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.day-date { font-weight: 600; font-size: 14px; color: #303133; min-width: 90px; }
.day-total { font-weight: 700; font-size: 14px; color: #e6a23c; }
.day-breakdown { font-size: 12px; color: #409eff; }
.day-breakdown.green { color: #67c23a; }

/* 条目 */
.entry-group { margin-bottom: 4px; }
.entry-group-label { font-size: 11px; color: #909399; margin: 4px 0; padding-left: 2px; }
.entry-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 13px; }
.entry-project { font-weight: 500; color: #409eff; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex-shrink: 0; max-width: 160px; }
.entry-content { color: #606266; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.entry-hours { font-weight: 600; color: #303133; flex-shrink: 0; min-width: 40px; text-align: right; }

/* 响应式 */
@media (max-width: 767px) {
  .emp-header { flex-direction: column; align-items: flex-start; }
  .emp-summary { width: 100%; justify-content: space-between; }
  .entry-row { flex-wrap: wrap; }
  .entry-project { max-width: 100%; }
}
</style>
