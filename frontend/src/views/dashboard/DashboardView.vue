<template>
  <div class="dashboard">
    <!-- 欢迎区 -->
    <div class="welcome-bar">
      <div>
        <h2>工作台</h2>
        <p class="welcome-date">{{ todayStr }}</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="router.push('/projects')"><el-icon><Plus /></el-icon>新建项目</el-button>
        <el-button type="success" @click="router.push('/executions')"><el-icon><Tickets /></el-icon>每日执行单</el-button>
        <el-button type="info" @click="router.push('/reports/personnel')"><el-icon><DataAnalysis /></el-icon>人员报表</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="6" v-for="c in statCards" :key="c.label">
        <el-card shadow="hover" class="stat-card" @click="c.link && router.push(c.link)">
          <div class="sc-inner">
            <div class="sc-icon" :style="{background: c.color}"><el-icon :size="22"><component :is="c.icon" /></el-icon></div>
            <div class="sc-body">
              <div class="sc-value" :style="{color: c.color}">{{ c.value }}</div>
              <div class="sc-label">{{ c.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：预算vs成本 + 月度趋势 -->
    <el-row :gutter="16" style="margin-top:16px">
      <!-- 预算使用率 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">预算执行率</span></template>
          <div class="budget-compare">
            <div class="bc-item">
              <div class="bc-label">预算总额</div>
              <div class="bc-val">¥{{ stats.budget_total.toLocaleString() }}</div>
            </div>
            <div class="bc-divider"><div class="bc-bar-track">
              <div class="bc-bar-fill" :style="{width: budgetPercent + '%'}" :class="budgetPercent > 100 ? 'over' : ''"></div>
            </div></div>
            <div class="bc-item">
              <div class="bc-label">累计成本</div>
              <div class="bc-val">¥{{ stats.total_cost.toLocaleString() }}</div>
            </div>
            <div class="bc-pct">{{ budgetPercent.toFixed(1) }}%</div>
          </div>
        </el-card>
      </el-col>

      <!-- 月度成本趋势 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">近6个月成本趋势</span></template>
          <div class="month-bars">
            <div v-for="m in stats.monthly_trend" :key="m.month" class="mb-item">
              <div class="mb-bar-wrap">
                <div class="mb-bar" :style="{height: maxMonthCost ? (m.cost / maxMonthCost * 100) + '%' : '0%'}"></div>
              </div>
              <div class="mb-val">¥{{ (m.cost / 10000).toFixed(1) }}万</div>
              <div class="mb-label">{{ m.month.slice(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：最近项目 + 最近执行单 -->
    <el-row :gutter="16" style="margin-top:16px">
      <!-- 最近项目 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">最近项目</span>
              <el-tag size="small" round>共 {{ stats.total_projects }} 个</el-tag>
            </div>
          </template>
          <el-table :data="stats.recent_projects" size="small" stripe>
            <el-table-column prop="name" label="项目名称" min-width="140" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{row}"><el-tag size="small" :type="row.status === '进行中' ? 'success' : 'info'">{{ row.status }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="accumulated_cost" label="累计成本" width="110" align="right">
              <template #default="{row}">¥{{ row.accumulated_cost.toLocaleString() }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 最近执行单 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header-row">
              <span class="card-title">最近执行单</span>
              <el-tag size="small" round>本月 ¥{{ stats.month_cost.toLocaleString() }}</el-tag>
            </div>
          </template>
          <el-table :data="stats.recent_executions" size="small" stripe>
            <el-table-column prop="project_name" label="项目" min-width="120" show-overflow-tooltip />
            <el-table-column prop="record_date" label="日期" width="100" />
            <el-table-column prop="daily_cost" label="日成本" width="100" align="right">
              <template #default="{row}">¥{{ row.daily_cost.toLocaleString() }}</template>
            </el-table-column>
            <el-table-column prop="seq_number" label="序号" width="55" align="center" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Tickets, DataAnalysis, FolderOpened, Money, CircleCheck, TrendCharts } from '@element-plus/icons-vue'
import { reportsApi } from '@/api/reports'
import type { DashboardStats } from '@/api/reports'

const router = useRouter()

const todayStr = computed(() => {
  const d = new Date()
  const weekNames = ['日', '一', '二', '三', '四', '五', '六']
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekNames[d.getDay()]}`
})

const stats = ref<DashboardStats>({
  total_projects: 0, active_projects: 0,
  total_contract: 0, total_cost: 0, total_received: 0,
  total_employees: 0, month_cost: 0, budget_total: 0,
  project_statuses: {},
  monthly_trend: [],
  recent_projects: [],
  recent_executions: [],
})

const statCards = computed(() => [
  { label: '项目总数', value: String(stats.value.total_projects), icon: FolderOpened, color: '#409eff', link: '/projects' },
  { label: '进行中', value: String(stats.value.active_projects), icon: CircleCheck, color: '#67c23a' },
  { label: '合同总额', value: '¥' + stats.value.total_contract.toLocaleString(), icon: Money, color: '#e6a23c', link: '/projects' },
  { label: '本月成本', value: '¥' + stats.value.month_cost.toLocaleString(), icon: TrendCharts, color: '#f56c6c', link: '/executions' },
])

const budgetPercent = computed(() => {
  if (!stats.value.budget_total) return 0
  return Math.round(stats.value.total_cost / stats.value.budget_total * 1000) / 10
})

const maxMonthCost = computed(() => {
  return Math.max(...stats.value.monthly_trend.map(m => m.cost), 1)
})

onMounted(async () => {
  try {
    const s = await reportsApi.dashboard()
    stats.value = s
  } catch { /* keep defaults */ }
})
</script>

<style scoped>
.dashboard h2 { font-size: 22px; color: #303133; margin: 0; }

/* 欢迎区 */
.welcome-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.welcome-date { font-size: 13px; color: #909399; margin: 4px 0 0; }
.quick-actions { display: flex; gap: 8px; }

/* 统计卡片 */
.stat-row { margin-top: 0; }
.stat-card { cursor: pointer; }
.stat-card :deep(.el-card__body) { padding: 18px 16px; }
.sc-inner { display: flex; align-items: center; gap: 14px; }
.sc-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
.sc-value { font-size: 22px; font-weight: 700; }
.sc-label { font-size: 12px; color: #909399; margin-top: 2px; }

/* 卡片标题 */
.card-title { font-size: 14px; font-weight: 600; color: #303133; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; }

/* 预算执行率 */
.budget-compare { display: flex; align-items: center; gap: 12px; padding: 12px 0; }
.bc-item { text-align: center; flex-shrink: 0; }
.bc-label { font-size: 12px; color: #909399; }
.bc-val { font-size: 18px; font-weight: 700; color: #303133; margin-top: 2px; }
.bc-divider { flex: 1; padding: 0 8px; }
.bc-bar-track { height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden; }
.bc-bar-fill { height: 100%; background: linear-gradient(90deg, #67c23a, #409eff); border-radius: 5px; transition: width 0.6s; min-width: 2px; }
.bc-bar-fill.over { background: linear-gradient(90deg, #e6a23c, #f56c6c); }
.bc-pct { font-size: 14px; font-weight: 600; color: #409eff; flex-shrink: 0; min-width: 48px; text-align: right; }

/* 月度趋势柱状图 */
.month-bars { display: flex; align-items: flex-end; justify-content: space-around; height: 160px; padding: 8px 0; }
.mb-item { display: flex; flex-direction: column; align-items: center; flex: 1; }
.mb-bar-wrap { width: 32px; flex: 1; display: flex; align-items: flex-end; }
.mb-bar { width: 100%; background: linear-gradient(0deg, #409eff, #79bbff); border-radius: 4px 4px 0 0; min-height: 2px; transition: height 0.6s; }
.mb-val { font-size: 10px; color: #909399; margin-top: 4px; }
.mb-label { font-size: 11px; color: #c0c4cc; margin-top: 2px; }

@media (max-width: 767px) {
  .welcome-bar,
  .card-header-row,
  .budget-compare {
    flex-direction: column;
    align-items: stretch;
  }

  .quick-actions {
    flex-direction: column;
  }

  .quick-actions .el-button {
    width: 100%;
  }

  .month-bars {
    height: 180px;
  }
}
</style>
