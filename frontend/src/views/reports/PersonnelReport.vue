<template>
  <div class="page">
    <h2>人员工时统计报表</h2>

    <el-row :gutter="12" style="margin-top:12px" align="middle">
      <el-col :xs="24" :sm="6"><el-input-number v-model="year" :min="2020" :max="2030" @change="loadReport" /></el-col>
      <el-col :xs="24" :sm="12"><span style="font-size:16px;font-weight:bold">年度人员工时汇总</span></el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px" v-for="item in reportItems" :key="item.employee_id">
      <el-col :span="24">
        <el-card style="margin-bottom:12px">
          <template #header>
            <span style="font-weight:bold">{{ item.employee_name }}</span>
            <el-tag style="margin-left:8px" size="small">{{ item.work_type }}</el-tag>
            <el-tag style="margin-left:4px" size="small" type="info">{{ item.department }}</el-tag>
          </template>

          <el-row :gutter="12">
            <el-col :xs="12" :sm="6">
              <div class="mini-stat">
                <div class="mini-value">{{ item.total_hours }}</div>
                <div class="mini-label">总工时(h)</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="mini-stat">
                <div class="mini-value">{{ item.work_days }}</div>
                <div class="mini-label">工作日</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="mini-stat">
                <div class="mini-value" style="color:#67c23a">¥{{ item.total_cost.toLocaleString() }}</div>
                <div class="mini-label">人员成本</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6">
              <div class="mini-stat">
                <div class="mini-value">{{ item.projects.length }}</div>
                <div class="mini-label">参与项目</div>
              </div>
            </el-col>
          </el-row>

          <el-divider />
          <div style="margin-bottom:8px"><b>月度工时：</b></div>
          <div class="monthly-bar">
            <div v-for="m in item.monthly" :key="m.month" class="month-bar-item" :title="m.month+'月: '+m.hours+'h'">
              <div class="month-bar-fill" :style="{height: monthlyBarHeight(m.hours, item.monthly)}" :class="{ zero: m.hours === 0 }"></div>
              <span class="month-label">{{ m.month }}月</span>
            </div>
          </div>
          <div v-if="item.projects.length" style="margin-top:12px;margin-bottom:8px"><b>项目参与明细：</b></div>
          <el-table :data="item.projects" size="small" v-if="item.projects.length">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="hours" label="工时(h)" width="100" />
            <el-table-column label="成本" width="120"><template #default="{row}">¥{{ row.cost.toLocaleString() }}</template></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && reportItems.length === 0" description="暂无数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import type { PersonnelStats } from '@/api/reports'

const year = ref(new Date().getFullYear())
const reportItems = ref<PersonnelStats[]>([])
const loading = ref(false)

async function loadReport() {
  loading.value = true
  try {
    const res = await reportsApi.personnel({ year: year.value })
    reportItems.value = res.items
  } finally { loading.value = false }
}

function monthlyBarHeight(hours: number, monthly: PersonnelStats['monthly']) {
  const max = Math.max(...monthly.map(m => m.hours), 1)
  return Math.max((hours / max) * 80, hours > 0 ? 4 : 1) + 'px'
}

onMounted(loadReport)
</script>

<style scoped>
h2 { font-size: 20px; }
.mini-stat { text-align: center; padding: 8px; }
.mini-value { font-size: 24px; font-weight: bold; color: #409eff; }
.mini-label { font-size: 12px; color: #909399; }

.monthly-bar { display: flex; gap: 2px; align-items: flex-end; height: 90px; padding: 4px 0; }
.month-bar-item { display: flex; flex-direction: column; align-items: center; flex: 1; height: 100%; justify-content: flex-end; }
.month-bar-fill { width: 100%; max-width: 28px; background: #409eff; border-radius: 2px 2px 0 0; min-height: 1px; transition: height 0.3s; }
.month-bar-fill.zero { background: #e0e0e0; }
.month-label { font-size: 10px; color: #909399; margin-top: 2px; }
</style>
