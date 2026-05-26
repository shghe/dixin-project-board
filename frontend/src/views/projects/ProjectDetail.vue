<template>
  <div class="page" v-loading="loading">
    <el-page-header @back="router.push('/projects')">
      <template #content><b>{{ project?.name }}</b></template>
    </el-page-header>

    <el-tabs v-model="activeTab" style="margin-top:16px" v-if="project">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目编号">{{ project.project_code }}</el-descriptions-item>
          <el-descriptions-item label="项目名称">{{ project.name }}</el-descriptions-item>
          <el-descriptions-item label="所在区域">{{ project.region_province }} / {{ project.region_city }}</el-descriptions-item>
          <el-descriptions-item label="甲方">{{ project.party_a }}</el-descriptions-item>
          <el-descriptions-item label="乙方">{{ project.party_b }}</el-descriptions-item>
          <el-descriptions-item label="联系人">{{ project.contact_person }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ project.contact_phone }}</el-descriptions-item>
          <el-descriptions-item label="资金来源">{{ project.fund_source }}</el-descriptions-item>
          <el-descriptions-item label="项目性质">{{ project.project_nature }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ project.status }}</el-descriptions-item>
          <el-descriptions-item label="项目经理">{{ project.manager_name }}</el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <!-- 合同信息 -->
      <el-tab-pane label="合同信息" name="contract">
        <el-form :model="contractForm" label-width="120px" v-if="contractForm">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item label="合同金额"><el-input-number v-model="contractForm.contract_amount" :min="0" style="width:100%" /></el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item label="折扣系数"><el-input-number v-model="contractForm.discount_rate" :min="0" :max="1" :step="0.01" style="width:100%" /></el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="实际金额"><b>¥{{ (contractForm.contract_amount * contractForm.discount_rate).toLocaleString() }}</b></el-form-item>
          <el-form-item label="签订日期"><el-date-picker v-model="contractForm.sign_date" type="date" /></el-form-item>
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12"><el-form-item label="合同起草人"><el-input v-model="contractForm.drafter" /></el-form-item></el-col>
            <el-col :xs="24" :sm="12"><el-form-item label="审核人"><el-input v-model="contractForm.reviewer" /></el-form-item></el-col>
          </el-row>
          <el-form-item label="付款约定"><el-input v-model="contractForm.payment_terms" type="textarea" :rows="4" /></el-form-item>
          <el-form-item><el-button type="primary" @click="saveContract">保存合同</el-button></el-form-item>
        </el-form>
        <el-empty v-else description="暂无合同信息">
          <el-button type="primary" @click="initContract">录入合同</el-button>
        </el-empty>
      </el-tab-pane>

      <!-- 分包情况 -->
      <el-tab-pane label="分包情况" name="subcontract">
        <div style="margin-bottom:12px">
          <el-button type="primary" size="small" @click="openSubDialog()" v-if="canEdit">添加分包</el-button>
        </div>
        <el-table :data="subcontracts" stripe>
          <el-table-column prop="company_name" label="公司名称" min-width="160" />
          <el-table-column prop="qualification" label="资质" width="100" />
          <el-table-column prop="company_scale" label="规模" width="80" />
          <el-table-column prop="contact_person" label="联系人" width="100" />
          <el-table-column prop="contact_phone" label="电话" width="130" />
          <el-table-column label="金额" width="120"><template #default="{row}">¥{{ row.amount.toLocaleString() }}</template></el-table-column>
          <el-table-column label="已结算" width="120"><template #default="{row}">¥{{ row.settled_amount.toLocaleString() }}</template></el-table-column>
          <el-table-column prop="content" label="分包内容" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" width="80" fixed="right" v-if="canEdit">
            <template #default="{row}"><el-button size="small" type="danger" @click="deleteSub(row.id)">删除</el-button></template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 预算科目 -->
      <el-tab-pane label="预算科目" name="budget">
        <div style="margin-bottom:12px">
          <el-button type="primary" size="small" @click="$router.push(`/projects/${projectId}/budget`)" v-if="canEdit">编制预算</el-button>
        </div>
        <el-table :data="budgetItems" stripe>
          <el-table-column prop="category" label="一级科目" width="120" />
          <el-table-column prop="sub_category" label="二级科目" width="120" />
          <el-table-column label="金额" width="130"><template #default="{row}">¥{{ row.amount.toLocaleString() }}</template></el-table-column>
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column prop="work_days" label="工日" width="70" />
          <el-table-column prop="unit_price" label="单价" width="90" />
          <el-table-column label="人员相关" width="90"><template #default="{row}"><el-tag :type="row.is_personnel?'success':'info'" size="small">{{ row.is_personnel ? '是' : '否' }}</el-tag></template></el-table-column>
          <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        </el-table>
        <el-empty v-if="budgetItems.length===0" description="暂无预算科目" />
      </el-tab-pane>

      <!-- 施工横道图 -->
      <el-tab-pane label="施工横道图" name="gantt">
        <div style="margin-bottom:12px">
          <el-button type="primary" size="small" @click="openTaskDialog()" v-if="canEdit">添加任务</el-button>
        </div>
        <!-- 简易甘特图 -->
        <div class="gantt-container" v-if="tasks.length">
          <div class="gantt-row" v-for="t in tasks" :key="t.id">
            <div class="gantt-label">{{ t.task_name }}</div>
            <div class="gantt-bar-wrap">
              <div class="gantt-bar" :style="ganttBarStyle(t)">
                {{ t.duration_days }}天
              </div>
            </div>
            <div class="gantt-actions" v-if="canEdit">
              <el-button size="small" @click="openTaskDialog(t)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteTask(t.id)">删除</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无施工任务" />
      </el-tab-pane>
    </el-tabs>

    <!-- 分包弹窗 -->
    <el-dialog v-model="subDialogVisible" title="添加分包" width="500px">
      <el-form :model="subForm" label-width="80px">
        <el-form-item label="公司名称"><el-input v-model="subForm.company_name" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="资质"><el-input v-model="subForm.qualification" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="规模"><el-input v-model="subForm.company_scale" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="联系人"><el-input v-model="subForm.contact_person" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="电话"><el-input v-model="subForm.contact_phone" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="金额"><el-input-number v-model="subForm.amount" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="已结算"><el-input-number v-model="subForm.settled_amount" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="分包内容"><el-input v-model="subForm.content" type="textarea" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="subForm.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="subDialogVisible=false">取消</el-button><el-button type="primary" @click="saveSub">保存</el-button></template>
    </el-dialog>

    <!-- 任务弹窗 -->
    <el-dialog v-model="taskDialogVisible" :title="editingTaskId?'编辑任务':'添加任务'" width="520px">
      <el-form :model="taskForm" label-width="80px">
        <el-form-item label="任务名称"><el-input v-model="taskForm.task_name" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="开始日期"><el-date-picker v-model="taskForm.start_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="结束日期"><el-date-picker v-model="taskForm.end_date" type="date" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="工期(天)"><el-input-number v-model="taskForm.duration_days" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="taskForm.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="taskDialogVisible=false">取消</el-button><el-button type="primary" @click="saveTask">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectsApi } from '@/api/projects'
import type { ProjectItem, ContractItem, SubcontractItem, BudgetItemRow, TaskItem } from '@/api/projects'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const canEdit = computed(() => ['院长','副院长','项目经理'].includes(authStore.user?.role||''))

const loading = ref(false)
const activeTab = ref('info')
const project = ref<ProjectItem | null>(null)
const projectId = route.params.id as string

// 合同
const contractForm = ref<ContractItem | null>(null)

// 分包
const subcontracts = ref<SubcontractItem[]>([])
const subDialogVisible = ref(false)
const subForm = ref({
  company_name: '', qualification: '', company_scale: '',
  contact_person: '', contact_phone: '', content: '',
  amount: 0, settled_amount: 0, remark: '',
})

// 预算
const budgetItems = ref<BudgetItemRow[]>([])

// 施工任务
const tasks = ref<TaskItem[]>([])
const taskDialogVisible = ref(false)
const editingTaskId = ref('')
const taskForm = ref({
  task_name: '', start_date: null as string|null, duration_days: 0,
  end_date: null as string|null, sort_order: 0, remark: '',
})

// 甘特图全局日期范围
const ganttRange = computed(() => {
  if (!tasks.value.length) return { min: '', max: '', total: 1 }
  const dates = tasks.value.map(t => t.start_date).filter(Boolean)
  if (!dates.length) return { min: '', max: '', total: 1 }
  const min = dates.reduce((a,b) => a < b ? a : b)
  const max = tasks.value.map(t => t.end_date).reduce((a,b) => a > b ? a : b)
  const total = Math.max(1, Math.ceil((new Date(max).getTime() - new Date(min).getTime()) / 86400000) + 1)
  return { min, max, total }
})

function ganttBarStyle(task: TaskItem) {
  const { min, total } = ganttRange.value
  if (!min || !task.start_date) return {}
  const startOffset = Math.max(0, Math.ceil((new Date(task.start_date).getTime() - new Date(min).getTime()) / 86400000))
  const width = Math.max(2, (task.duration_days / Math.max(total, task.duration_days)) * 100)
  return {
    marginLeft: (startOffset / total) * 100 + '%',
    width: Math.min(width, 100 - (startOffset / total) * 100) + '%',
  }
}

async function loadAll() {
  loading.value = true
  try {
    const [proj, subs, items, t] = await Promise.all([
      projectsApi.get(projectId),
      projectsApi.listSubcontracts(projectId).catch(() => [] as SubcontractItem[]),
      projectsApi.listBudgetItems(projectId).catch(() => [] as BudgetItemRow[]),
      projectsApi.listTasks(projectId).catch(() => [] as TaskItem[]),
    ])
    project.value = proj
    subcontracts.value = subs
    budgetItems.value = items
    tasks.value = t
    try { contractForm.value = await projectsApi.getContract(projectId) } catch { contractForm.value = null }
  } finally { loading.value = false }
}

// 合同
function initContract() {
  contractForm.value = {
    id: '', project_id: projectId, contract_amount: 0, discount_rate: 1.0,
    actual_amount: 0, sign_date: null, drafter: '', reviewer: '', payment_terms: '',
  }
}

async function saveContract() {
  if (!contractForm.value) return
  await projectsApi.saveContract(projectId, {
    contract_amount: contractForm.value.contract_amount,
    discount_rate: contractForm.value.discount_rate,
    sign_date: contractForm.value.sign_date,
    drafter: contractForm.value.drafter,
    reviewer: contractForm.value.reviewer,
    payment_terms: contractForm.value.payment_terms,
  })
  ElMessage.success('保存成功')
  loadAll()
}

// 分包
function openSubDialog() {
  subForm.value = { company_name: '', qualification: '', company_scale: '', contact_person: '', contact_phone: '', content: '', amount: 0, settled_amount: 0, remark: '' }
  subDialogVisible.value = true
}

async function saveSub() {
  await projectsApi.createSubcontract(projectId, subForm.value)
  ElMessage.success('分包已添加')
  subDialogVisible.value = false
  loadAll()
}

async function deleteSub(subId: string) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await projectsApi.deleteSubcontract(projectId, subId)
  ElMessage.success('已删除')
  loadAll()
}

// 施工任务
function openTaskDialog(task?: TaskItem) {
  if (task) {
    editingTaskId.value = task.id
    taskForm.value = { task_name: task.task_name, start_date: task.start_date, duration_days: task.duration_days, end_date: task.end_date, sort_order: task.sort_order, remark: task.remark||'' }
  } else {
    editingTaskId.value = ''
    taskForm.value = { task_name: '', start_date: null, duration_days: 0, end_date: null, sort_order: 0, remark: '' }
  }
  taskDialogVisible.value = true
}

async function saveTask() {
  if (editingTaskId.value) {
    await projectsApi.updateTask(projectId, editingTaskId.value, taskForm.value)
    ElMessage.success('任务已更新')
  } else {
    await projectsApi.createTask(projectId, taskForm.value)
    ElMessage.success('任务已添加')
  }
  taskDialogVisible.value = false
  loadAll()
}

async function deleteTask(taskId: string) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await projectsApi.deleteTask(projectId, taskId)
  ElMessage.success('已删除')
  loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.gantt-container { border: 1px solid #ebeef5; border-radius: 4px; }
.gantt-row { display: flex; align-items: center; padding: 6px 12px; border-bottom: 1px solid #ebeef5; }
.gantt-row:last-child { border-bottom: none; }
.gantt-label { width: 120px; flex-shrink: 0; font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.gantt-bar-wrap { flex: 1; height: 28px; background: #f5f7fa; border-radius: 4px; position: relative; margin: 0 12px; }
.gantt-bar { height: 100%; background: #409eff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 11px; min-width: 40px; white-space: nowrap; }
.gantt-actions { flex-shrink: 0; display: flex; gap: 4px; }

@media (max-width: 767px) {
  .gantt-container {
    overflow-x: auto;
  }

  .gantt-row {
    min-width: 640px;
  }

  .gantt-label {
    width: 96px;
  }
}
</style>
