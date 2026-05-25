<template>
  <div class="page" v-loading="loading">
    <el-page-header @back="router.push('/projects/'+projectId)">
      <template #content><b>{{ projectName }} - 财务汇总</b></template>
    </el-page-header>

    <!-- 汇总卡片 -->
    <el-row :gutter="16" style="margin-top:16px">
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">预算总额</div><div class="sv">¥{{ data.total_budget.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">已发生成本</div><div class="sv" style="color:#f56c6c">¥{{ data.total_cost.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">产值</div><div class="sv" style="color:#409eff">¥{{ data.total_output.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">开票金额</div><div class="sv" style="color:#e6a23c">¥{{ data.total_invoice.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">回款金额</div><div class="sv" style="color:#67c23a">¥{{ data.total_received.toLocaleString() }}</div></el-card>
      </el-col>
      <el-col :xs="12" :sm="4">
        <el-card shadow="hover"><div class="sc">应收</div><div class="sv" :style="{color: data.receivable>0?'#f56c6c':'#67c23a'}">¥{{ data.receivable.toLocaleString() }}</div></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:12px">
      <el-col :xs="12" :sm="6"><div class="sc">利润</div><div class="sv" :style="{color: data.profit>=0?'#67c23a':'#f56c6c'}">¥{{ data.profit.toLocaleString() }}</div></el-col>
      <el-col :xs="12" :sm="6"><div class="sc">利润率</div><div class="sv" :style="{color: data.profit_rate>=0?'#67c23a':'#f56c6c'}">{{ data.profit_rate }}%</div></el-col>
    </el-row>

    <!-- 财务事件 -->
    <el-card style="margin-top:16px">
      <template #header>
        <div class="card-header-row">
          <b>产值 / 开票 / 回款记录</b>
          <el-button type="primary" size="small" @click="openEventDialog()">添加记录</el-button>
        </div>
      </template>
      <el-table :data="events" stripe size="small">
        <el-table-column prop="event_date" label="日期" width="110" />
        <el-table-column prop="event_type" label="类型" width="90">
          <template #default="{row}">
            <el-tag :type="row.event_type==='产值'?'':row.event_type==='开票'?'warning':'success'" size="small">{{ row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="140"><template #default="{row}">¥{{ row.amount.toLocaleString() }}</template></el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="openEventDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteEvent(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!events.length" description="暂无财务记录" />
    </el-card>

    <!-- 预算科目明细 -->
    <el-card style="margin-top:16px" v-if="data.budget_detail.length">
      <template #header><b>预算科目明细</b></template>
      <el-table :data="data.budget_detail" stripe size="small">
        <el-table-column prop="category" label="科目" width="120" />
        <el-table-column prop="sub_category" label="二级科目" width="120" />
        <el-table-column label="预算金额" width="130"><template #default="{row}">¥{{ row.amount.toLocaleString() }}</template></el-table-column>
        <el-table-column label="类型" width="90">
          <template #default="{row}"><el-tag :type="row.is_personnel?'success':'info'" size="small">{{ row.is_personnel?'人员':'费用' }}</el-tag></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 财务事件弹窗 -->
    <el-dialog v-model="eventDialogVisible" :title="editingEventId?'编辑记录':'添加记录'" width="450px">
      <el-form :model="eventForm" label-width="80px">
        <el-form-item label="日期"><el-date-picker v-model="eventForm.event_date" type="date" style="width:100%" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="eventForm.event_type" style="width:100%">
            <el-option label="产值" value="产值" />
            <el-option label="开票" value="开票" />
            <el-option label="回款" value="回款" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额"><el-input-number v-model="eventForm.amount" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="eventForm.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="eventDialogVisible=false">取消</el-button><el-button type="primary" @click="saveEvent">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectsApi } from '@/api/projects'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const projectId = route.params.id as string
const projectName = ref('')

const data = ref({
  total_budget: 0, budget_personnel: 0, budget_non_personnel: 0,
  exec_count: 0, total_cost: 0, total_output: 0,
  total_invoice: 0, total_received: 0,
  receivable: 0, profit: 0, profit_rate: 0,
  budget_detail: [] as any[],
})

const events = ref<any[]>([])
const eventDialogVisible = ref(false)
const editingEventId = ref('')
const eventForm = ref({
  event_date: new Date().toISOString().slice(0, 10),
  event_type: '产值',
  amount: 0,
  remark: '',
})

async function loadAll() {
  loading.value = true
  try {
    const [proj, fin, evts] = await Promise.all([
      projectsApi.get(projectId),
      projectsApi.getFinance(projectId),
      projectsApi.listFinancialEvents(projectId),
    ])
    projectName.value = proj.name
    data.value = fin
    events.value = evts
  } finally { loading.value = false }
}

function openEventDialog(row?: any) {
  if (row) {
    editingEventId.value = row.id
    eventForm.value = { event_date: row.event_date, event_type: row.event_type, amount: row.amount, remark: row.remark || '' }
  } else {
    editingEventId.value = ''
    eventForm.value = { event_date: new Date().toISOString().slice(0, 10), event_type: '产值', amount: 0, remark: '' }
  }
  eventDialogVisible.value = true
}

async function saveEvent() {
  if (editingEventId.value) {
    await projectsApi.updateFinancialEvent(projectId, editingEventId.value, eventForm.value)
    ElMessage.success('更新成功')
  } else {
    await projectsApi.createFinancialEvent(projectId, eventForm.value)
    ElMessage.success('添加成功')
  }
  eventDialogVisible.value = false
  loadAll()
}

async function deleteEvent(eventId: string) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await projectsApi.deleteFinancialEvent(projectId, eventId)
  ElMessage.success('已删除')
  loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.sc { font-size: 13px; color: #909399; }
.sv { font-size: 22px; font-weight: bold; color: #409eff; }
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
