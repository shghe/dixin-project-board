<template>
  <div class="page">
    <h2>我的工时</h2>

    <!-- 日期选择 + 汇总 -->
    <el-row :gutter="16" style="margin-top:12px" align="middle">
      <el-col :xs="12" :sm="4">
        <el-date-picker v-model="selectedDate" type="date" placeholder="选择日期" @change="loadData" style="width:100%" />
      </el-col>
      <el-col :xs="12" :sm="16">
        <span style="font-size:16px">{{ selectedDate }} 工时汇总</span>
      </el-col>
    </el-row>

    <!-- 工时卡片 -->
    <el-row :gutter="16" style="margin-top:12px">
      <el-col :xs="24" :sm="6">
        <el-card shadow="hover">
          <div class="sc">项目工时</div>
          <div class="sv">{{ summary.project_hours }}h</div>
          <div v-if="summary.project_breakdown.length" class="breakdown">
            <div v-for="p in summary.project_breakdown" :key="p.project_name" class="breakdown-item">
              <span class="breakdown-name">{{ p.project_name }}</span>
              <span class="breakdown-hours">{{ p.hours }}h</span>
            </div>
          </div>
          <div v-else class="sc" style="margin-top:4px">-</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-card shadow="hover"><div class="sc">个人工时</div><div class="sv" style="color:#67c23a">{{ summary.personal_hours }}h</div></el-card>
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-card shadow="hover"><div class="sc">合计</div><div class="sv" :style="{color: summary.total_hours>=8?'#67c23a':'#e6a23c'}">{{ summary.total_hours }}h</div></el-card>
      </el-col>
      <el-col :xs="24" :sm="6">
        <el-card shadow="hover"><div class="sc">剩余</div><div class="sv" :style="{color: summary.remaining>0?'#f56c6c':'#67c23a'}">{{ summary.remaining }}h</div></el-card>
      </el-col>
    </el-row>

    <!-- 个人工时记录 -->
    <el-card style="margin-top:16px">
      <template #header>
        <div class="card-header-row">
          <span>非项目工作记录</span>
          <el-button type="primary" size="small" @click="openDialog()">添加记录</el-button>
        </div>
      </template>
      <el-table :data="entries" stripe size="small">
        <el-table-column prop="category" label="类别" width="110" />
        <el-table-column prop="work_hours" label="工时(h)" width="90" />
        <el-table-column prop="work_content" label="工作内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="entries.length===0" description="暂无记录" />
    </el-card>

    <!-- 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingId?'编辑记录':'添加记录'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类别">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="院务工作" value="院务工作" />
            <el-option label="行政事务" value="行政事务" />
            <el-option label="临时任务" value="临时任务" />
            <el-option label="培训学习" value="培训学习" />
            <el-option label="请假" value="请假" />
            <el-option label="出差" value="出差" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="工时(h)"><el-input-number v-model="form.work_hours" :min="0" :max="24" :step="0.5" style="width:100%" /></el-form-item>
        <el-form-item label="工作内容"><el-input v-model="form.work_content" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { personalWorkApi } from '@/api/personalWork'
import type { PersonalWorkEntryItem, DailySummary } from '@/api/personalWork'

const selectedDate = ref(new Date().toISOString().slice(0, 10))
const summary = ref<DailySummary>({
  record_date: '', project_hours: 0, project_breakdown: [],
  personal_hours: 0, total_hours: 0, remaining: 8, entries: [],
})
const entries = ref<PersonalWorkEntryItem[]>([])
const dialogVisible = ref(false)
const editingId = ref('')
const form = ref({ category: '院务工作', work_hours: 0, work_content: '' })

async function loadData() {
  const [s, e] = await Promise.all([
    personalWorkApi.dailySummary(selectedDate.value),
    personalWorkApi.list({ record_date: selectedDate.value }),
  ])
  summary.value = s
  entries.value = e
}

function openDialog(row?: PersonalWorkEntryItem) {
  if (row) {
    editingId.value = row.id
    form.value = { category: row.category, work_hours: row.work_hours, work_content: row.work_content || '' }
  } else {
    editingId.value = ''
    form.value = { category: '院务工作', work_hours: summary.value.remaining, work_content: '' }
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (editingId.value) {
    await personalWorkApi.update(editingId.value, form.value)
    ElMessage.success('更新成功')
  } else {
    await personalWorkApi.create({ ...form.value, record_date: selectedDate.value })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
  loadData()
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await personalWorkApi.delete(id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
h2 { font-size: 20px; }
.sc { font-size: 13px; color: #909399; }
.sv { font-size: 22px; font-weight: bold; color: #409eff; }
.breakdown { margin-top: 8px; border-top: 1px solid #ebeef5; padding-top: 6px; }
.breakdown-item { display: flex; justify-content: space-between; font-size: 12px; color: #606266; line-height: 1.8; }
.breakdown-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 70%; }
.breakdown-hours { font-weight: 600; color: #409eff; flex-shrink: 0; }
.card-header-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }

@media (max-width: 767px) {
  .card-header-row {
    flex-direction: column;
    align-items: stretch;
  }

  .card-header-row .el-button {
    width: 100%;
  }
}
</style>
