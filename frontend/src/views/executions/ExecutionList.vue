<template>
  <div class="page">
    <div class="page-header">
      <h2>每日执行单</h2>
      <div style="display:flex;align-items:center;gap:12px">
        <el-radio-group v-model="viewMode" size="small" @change="onViewModeChange">
          <el-radio-button value="project">项目维度</el-radio-button>
          <el-radio-button value="personnel">人员维度</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="openDialog" v-if="isManager && viewMode === 'project'">新增执行单</el-button>
      </div>
    </div>

    <el-select v-model="selectedProject" placeholder="选择项目" clearable filterable style="width:260px;margin:12px 0" @change="onProjectChange">
      <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
    </el-select>

    <template v-if="selectedProject && viewMode === 'project'">
      <!-- 汇总卡片 -->
      <el-row :gutter="12" style="margin-bottom:12px">
        <el-col :span="6">
          <div class="stat-card"><div class="stat-label">累计成本</div><div class="stat-val">¥{{ (accumulated.daily_cost || 0).toLocaleString() }}</div></div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card"><div class="stat-label">预算总额</div><div class="stat-val blue">¥{{ totalBudget.toLocaleString() }}</div></div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card"><div class="stat-label">剩余预算</div><div class="stat-val" :class="budgetRemaining >= 0 ? 'green' : 'red'">¥{{ budgetRemaining.toLocaleString() }}</div></div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card"><div class="stat-label">执行天数</div><div class="stat-val">{{ list.length }} 天</div></div>
        </el-col>
      </el-row>

      <!-- 超预算报警 -->
      <div v-if="overBudgetFields.length" class="alert-bar">
        <span>预算超支：</span>
        <el-tag v-for="f in overBudgetFields" :key="f.field" type="danger" size="small" style="margin-left:6px">{{ f.label }} {{ (accumulated[f.field]||0).toLocaleString() }} / {{ (budget[f.field]||0).toLocaleString() }}</el-tag>
      </div>

      <!-- 宽表：预算行和已发生行作为 table 数据行，保证对齐 -->
      <div class="table-shell">
        <div class="table-scroll" ref="scrollBox">
          <el-table :data="tableData" stripe v-loading="loading" size="small" class="exec-table"
            :header-cell-style="{background:'#f5f7fa',color:'#606266',fontWeight:'600'}"
            :row-class-name="rowClassName"
          >
            <el-table-column type="expand" width="30">
              <template #default="{row}">
                <template v-if="row._sentinel">-</template>
                <div v-else class="expand-content">
                  <div v-if="row.details.length">
                    <span class="expand-label">人员：</span>
                    <el-tag v-for="d in row.details" :key="d.employee_id" size="small" style="margin:2px">{{ d.employee_name }} {{ d.work_hours }}h {{ d.work_content }}</el-tag>
                  </div>
                  <div v-if="row.remark" style="margin-top:6px"><span class="expand-label">内容：</span>{{ row.remark }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="record_date" label="日期" width="100">
              <template #default="{row}">
                <span v-if="row._sentinel === 'budget'" class="sentinel-label">预算</span>
                <span v-else-if="row._sentinel === 'actual'" class="sentinel-label actual">已发生</span>
                <span v-else>{{ row.record_date }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="seq_number" label="序号" width="50">
              <template #default="{row}"><span v-if="!row._sentinel">{{ row.seq_number }}</span></template>
            </el-table-column>
            <el-table-column v-for="col in feeColumns" :key="col.field" :label="col.label" width="90">
              <template #default="{row}">
                <template v-if="row._sentinel === 'budget'">
                  <span :class="{ 'sentinel-over': isOverBudget(col.field) }">{{ fmtBudget(col.field) }}</span>
                </template>
                <template v-else-if="row._sentinel === 'actual'">
                  <span :class="{ 'sentinel-over': isOverBudget(col.field) }">{{ (accumulated[col.field] || 0).toLocaleString() }}</span>
                </template>
                <template v-else>
                  <span v-if="row[col.field]" :class="{ 'cell-over': isOverBudgetCell(col.field, row[col.field]) }">{{ row[col.field].toLocaleString() }}</span>
                  <span v-else style="color:#dcdfe6">-</span>
                </template>
              </template>
            </el-table-column>
            <el-table-column label="当日合计" width="100">
              <template #default="{row}">
                <template v-if="row._sentinel === 'actual'"><b>¥{{ (accumulated.daily_cost || 0).toLocaleString() }}</b></template>
                <template v-else-if="!row._sentinel"><b>¥{{ row.daily_cost.toLocaleString() }}</b></template>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="55" v-if="isManager">
              <template #default="{row}">
                <el-button v-if="!row._sentinel" size="small" text type="primary" @click="openEditDialog(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <el-empty v-if="!list.length && !loading" description="暂无执行记录" />
    </template>

    <!-- 人员维度：按人查看每日工作 -->
    <template v-if="viewMode === 'personnel'">
      <!-- 人员维度筛选栏 -->
      <div class="personnel-filters">
        <el-select v-model="personnelFilter.employee_id" placeholder="全部人员" clearable filterable size="small" style="width:180px" @change="loadPersonnelDaily">
          <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
        <el-select v-model="personnelFilter.year" placeholder="全部年份" clearable size="small" style="width:110px" @change="loadPersonnelDaily">
          <el-option v-for="y in yearOptions" :key="y" :label="String(y)" :value="y" />
        </el-select>
        <el-select v-model="personnelFilter.month" placeholder="月份" clearable size="small" style="width:90px" @change="loadPersonnelDaily">
          <el-option v-for="m in 12" :key="m" :label="m+'月'" :value="m" />
        </el-select>
        <span v-if="personnelSummary.total_days" class="personnel-summary">
          共 <b>{{ personnelSummary.total_days }}</b> 天 · <b>{{ personnelItems.length }}</b> 条记录 · <b>{{ personnelSummary.total_hours }}h</b> · 成本 <b>¥{{ personnelSummary.total_cost.toLocaleString() }}</b>
        </span>
      </div>

      <el-table :data="personnelItems" stripe v-loading="loadingPersonnel" size="small" max-height="550">
        <el-table-column prop="record_date" label="日期" width="110" sortable />
        <el-table-column prop="employee_name" label="姓名" width="100" />
        <el-table-column prop="work_type" label="工种" width="90" />
        <el-table-column prop="department" label="部门" width="130" />
        <el-table-column prop="project_name" label="项目" min-width="160" show-overflow-tooltip />
        <el-table-column prop="work_hours" label="工时(h)" width="80" align="right" />
        <el-table-column prop="work_content" label="工作内容" min-width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="70">
          <template #default="{row}"><el-tag v-if="row.is_leave" type="warning" size="small">请假</el-tag><span v-else style="color:#67c23a">出勤</span></template>
        </el-table-column>
        <el-table-column prop="cost" label="成本" width="100" align="right">
          <template #default="{row}">¥{{ row.cost.toLocaleString() }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!personnelItems.length && !loadingPersonnel" description="暂无工作记录" />
    </template>

    <el-empty v-if="!selectedProject && viewMode === 'project'" description="请先选择一个项目" />

    <!-- 弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editingId?'编辑每日执行单':'新增每日执行单'" width="950px" top="3vh">
      <el-form :model="form" label-width="100px" size="small">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="日期"><el-date-picker v-model="form.record_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="项目">
            <el-select v-model="form.project_id" filterable style="width:100%" :disabled="!!editingId" @change="onProjectChange"><el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" /></el-select>
          </el-form-item></el-col>
          <el-col :span="8"><el-form-item label="序号"><el-input-number v-model="form.seq_number" :min="1" /></el-form-item></el-col>
        </el-row>

        <el-divider>人员投入（自动按日工资计算成本）</el-divider>
        <div v-for="(d, i) in form.details" :key="i" class="personnel-row">
          <div class="personnel-line">
            <el-select v-model="d.employee_id" filterable placeholder="选择人员" size="small" class="sel-emp"><el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" /></el-select>
            <el-input-number v-model="d.work_hours" :min="0" :max="24" size="small" controls-position="right" class="inp-hours" />
            <span class="hours-unit">h</span>
            <el-checkbox v-model="d.is_leave" size="small">请假</el-checkbox>
            <el-input v-show="d.is_leave" v-model="d.leave_reason" placeholder="请假原因" size="small" class="inp-leave" />
            <span class="cost-badge"><el-tag v-show="d.employee_id" size="small" type="success">¥{{ getEmployeeCost(d) }}</el-tag></span>
          </div>
          <div class="personnel-line" style="margin-top:4px">
            <el-input v-model="d.work_content" placeholder="工作内容" size="small" class="inp-content" />
            <el-button type="danger" :icon="Delete" circle size="small" @click="form.details.splice(i,1)" />
          </div>
        </div>
        <el-button type="primary" text size="small" @click="addDetail">+ 添加人员</el-button>

        <el-divider>费用登记</el-divider>
        <el-row :gutter="16">
          <el-col :span="6"><el-form-item label="分包费"><el-input-number v-model="form.subcontract_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="相关费用"><el-input-number v-model="form.relevant_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="材料费"><el-input-number v-model="form.material_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="劳务费"><el-input-number v-model="form.labor_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6"><el-form-item label="租赁费"><el-input-number v-model="form.rental_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="交通费"><el-input-number v-model="form.transport_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="办公费"><el-input-number v-model="form.office_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="招待费"><el-input-number v-model="form.entertainment_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6"><el-form-item label="其他费用"><el-input-number v-model="form.other_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="差旅费"><el-input-number v-model="form.travel_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="招投标费"><el-input-number v-model="form.bidding_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="提成"><el-input-number v-model="form.commission_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6"><el-form-item label="税金"><el-input-number v-model="form.tax_fee" :min="0" style="width:100%" size="small" /></el-form-item></el-col>
        </el-row>

        <el-form-item label="工作内容"><el-input v-model="form.remark" type="textarea" :rows="2" placeholder="今日工作内容描述..." /></el-form-item>
        <el-form-item label="填报人"><el-input :model-value="form.registrant" disabled size="small" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false" size="small">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving" size="small">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { executionApi } from '@/api/execution'
import type { ExecutionItem, PersonnelDailyItem } from '@/api/execution'
import { projectsApi } from '@/api/projects'
import type { ProjectItem } from '@/api/projects'
import { employeesApi } from '@/api/employees'
import type { EmployeeItem } from '@/api/employees'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isManager = computed(() => authStore.user?.role === 'manager')

const feeColumns = [
  { field: 'inhouse_personnel', label: '事业人员' },
  { field: 'enterprise_personnel', label: '企业人员' },
  { field: 'dispatched_personnel', label: '派遣人员' },
  { field: 'subcontract_fee', label: '分包费' },
  { field: 'relevant_fee', label: '相关费用' },
  { field: 'material_fee', label: '材料费' },
  { field: 'labor_fee', label: '劳务费' },
  { field: 'rental_fee', label: '租赁费' },
  { field: 'transport_fee', label: '交通费' },
  { field: 'office_fee', label: '办公费' },
  { field: 'entertainment_fee', label: '招待费' },
  { field: 'other_fee', label: '其他费用' },
  { field: 'travel_fee', label: '差旅费' },
  { field: 'bidding_fee', label: '招投标费' },
  { field: 'commission_fee', label: '提成' },
  { field: 'tax_fee', label: '税金' },
]

const list = ref<ExecutionItem[]>([])

const tableData = computed(() => {
  if (!list.value.length) return []
  const budgetRow: any = { _sentinel: 'budget' }
  const actualRow: any = { _sentinel: 'actual' }
  return [budgetRow, ...list.value, actualRow]
})

function rowClassName({ row }: { row: any }) {
  if (row._sentinel === 'budget') return 'sentinel-row budget-row'
  if (row._sentinel === 'actual') return 'sentinel-row actual-row'
  return ''
}

const loading = ref(false); const saving = ref(false); const loadingPersonnel = ref(false)
const dialogVisible = ref(false)
const editingId = ref('')
const projects = ref<ProjectItem[]>([])
const employees = ref<EmployeeItem[]>([])
const selectedProject = ref('')
const budget = ref<Record<string,number>>({})
const accumulated = ref<Record<string,number>>({})
const viewMode = ref<'project' | 'personnel'>('project')
const personnelItems = ref<PersonnelDailyItem[]>([])
const personnelSummary = ref({ total_days: 0, total_hours: 0, total_cost: 0 })
const personnelFilter = ref({ employee_id: '', year: null as number | null, month: null as number | null })

const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  const years = []
  for (let y = currentYear; y >= currentYear - 3; y--) years.push(y)
  return years
})

const totalBudget = computed(() => {
  return Object.values(budget.value).reduce((s, v) => s + v, 0)
})
const budgetRemaining = computed(() => {
  return totalBudget.value - (accumulated.value.daily_cost || 0)
})
const overBudgetFields = computed(() => {
  return feeColumns.filter(c => {
    const b = budget.value[c.field] || 0
    const a = accumulated.value[c.field] || 0
    return a > 0 && (b === 0 || a > b)
  })
})

function fmtBudget(field: string) {
  const v = budget.value[field]
  return v ? v.toLocaleString() : '-'
}

function isOverBudget(field: string) {
  const b = budget.value[field] || 0
  const a = accumulated.value[field] || 0
  return a > 0 && (b === 0 || a > b)
}

function isOverBudgetCell(field: string, _cellValue: number) {
  const b = budget.value[field] || 0
  const a = accumulated.value[field] || 0
  return a > 0 && (b === 0 || a > b)
}

const form = ref({
  project_id: '', record_date: new Date().toISOString().slice(0, 10), seq_number: 1,
  subcontract_fee: 0, relevant_fee: 0, material_fee: 0, labor_fee: 0,
  rental_fee: 0, transport_fee: 0, office_fee: 0, entertainment_fee: 0,
  other_fee: 0, travel_fee: 0, bidding_fee: 0, commission_fee: 0, tax_fee: 0,
  remark: '', registrant: '',
  details: [] as { employee_id: string; work_hours: number; work_content: string; is_leave: boolean; leave_reason: string }[],
})

function getEmployeeCost(d: { employee_id: string; work_hours: number }) {
  if (!d.employee_id) return 0
  const emp = employees.value.find(e => e.id === d.employee_id)
  if (!emp) return 0
  return Math.round(emp.daily_wage / 8 * d.work_hours)
}

async function loadData() {
  const [projRes, empRes] = await Promise.all([projectsApi.list({ page_size: 100 }), employeesApi.list()])
  projects.value = projRes.items; employees.value = empRes
}

async function loadList() {
  loading.value = true
  try {
    if (selectedProject.value) {
      const res = await executionApi.list({ project_id: selectedProject.value, page_size: 200 })
      list.value = res.items
      budget.value = res.budget || {}
      accumulated.value = res.accumulated || {}
    } else {
      list.value = []; budget.value = {}; accumulated.value = {}
    }
  } finally { loading.value = false }
}

async function loadPersonnelDaily() {
  loadingPersonnel.value = true
  try {
    const params: any = {}
    if (selectedProject.value) params.project_id = selectedProject.value
    if (personnelFilter.value.employee_id) params.employee_id = personnelFilter.value.employee_id
    if (personnelFilter.value.year) params.year = personnelFilter.value.year
    if (personnelFilter.value.month) params.month = personnelFilter.value.month
    const res = await executionApi.personnelDaily(params)
    personnelItems.value = res.items
    personnelSummary.value = { total_days: res.total_days, total_hours: res.total_hours, total_cost: res.total_cost }
  } finally { loadingPersonnel.value = false }
}

function onProjectChange() {
  if (viewMode.value === 'personnel') {
    loadPersonnelDaily()
  } else {
    loadList()
  }
}

function onViewModeChange() {
  if (viewMode.value === 'personnel') {
    loadPersonnelDaily()
  } else {
    loadList()
  }
}

async function openDialog() {
  editingId.value = ''
  await loadData()
  form.value = {
    project_id: selectedProject.value || '', record_date: new Date().toISOString().slice(0, 10), seq_number: 1,
    subcontract_fee: 0, relevant_fee: 0, material_fee: 0, labor_fee: 0,
    rental_fee: 0, transport_fee: 0, office_fee: 0, entertainment_fee: 0,
    other_fee: 0, travel_fee: 0, bidding_fee: 0, commission_fee: 0, tax_fee: 0,
    remark: '', registrant: authStore.user?.employee_name || '',
    details: [{ employee_id: '', work_hours: 8, work_content: '', is_leave: false, leave_reason: '' }],
  }
  const proj = projects.value.find(p => p.id === selectedProject.value)
  if (proj) form.value.registrant = proj.manager_name || ''
  dialogVisible.value = true
}

function addDetail() {
  form.value.details.push({ employee_id: '', work_hours: 8, work_content: '', is_leave: false, leave_reason: '' })
}

async function openEditDialog(row: ExecutionItem) {
  editingId.value = row.id
  if (!employees.value.length) await loadData()
  form.value = {
    project_id: row.project_id, record_date: row.record_date, seq_number: row.seq_number,
    subcontract_fee: row.subcontract_fee || 0, relevant_fee: row.relevant_fee || 0, material_fee: row.material_fee || 0, labor_fee: row.labor_fee || 0,
    rental_fee: row.rental_fee || 0, transport_fee: row.transport_fee || 0, office_fee: row.office_fee || 0, entertainment_fee: row.entertainment_fee || 0,
    other_fee: row.other_fee || 0, travel_fee: row.travel_fee || 0, bidding_fee: row.bidding_fee || 0, commission_fee: row.commission_fee || 0, tax_fee: row.tax_fee || 0,
    remark: row.remark || '', registrant: row.registrant || '',
    details: row.details.map(d => ({
      employee_id: d.employee_id, work_hours: d.work_hours, work_content: d.work_content || '',
      is_leave: d.is_leave, leave_reason: d.leave_reason || '',
    })),
  }
  dialogVisible.value = true
}

async function handleSave() {
  saving.value = true
  try {
    if (editingId.value) {
      await executionApi.update(editingId.value, form.value)
      ElMessage.success('执行单已更新')
    } else {
      await executionApi.create(form.value)
      ElMessage.success('执行单已提交')
    }
    dialogVisible.value = false
    loadList()
  } finally { saving.value = false }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.page h2 { font-size: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }

/* 统计卡片 */
.stat-card { background: #fff; border: 1px solid #e4e7ed; border-radius: 6px; padding: 14px 16px; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.stat-val { font-size: 22px; font-weight: 700; color: #303133; }
.stat-val.blue { color: #409eff; }
.stat-val.green { color: #67c23a; }
.stat-val.red { color: #f56c6c; }

/* 表格壳 */
.table-shell { border: 1px solid #e4e7ed; border-radius: 6px; overflow: hidden; }
.table-scroll { overflow-x: auto; }

/* 预算 / 已发生 sentinel 行 */
:deep(.sentinel-row) { font-size: 12px; font-weight: 600; }
:deep(.budget-row) { background: #f0f9eb !important; }
:deep(.budget-row td) { color: #606266; padding: 6px 0 !important; }
:deep(.actual-row) { background: #fafafa !important; }
:deep(.actual-row td) { color: #303133; padding: 6px 0 !important; border-top: 2px solid #e4e7ed !important; }

.sentinel-label { font-weight: 600; }
.sentinel-label.actual { color: #303133; }
.sentinel-over { color: #f56c6c; font-weight: 700; background: #fef0f0; border-radius: 2px; padding: 1px 4px; }

/* 超预算报警条 */
.alert-bar {
  display: flex; align-items: center; padding: 8px 12px;
  background: #fef0f0; border: 1px solid #fab6b6; border-radius: 6px;
  color: #f56c6c; font-size: 13px; font-weight: 600; margin-bottom: 8px;
}

.exec-table { min-width: 1610px; width: auto !important; }
.exec-table :deep(.el-table__body-wrapper) { overflow-x: visible !important; }

/* 表格内超标标记 */
.cell-over { color: #f56c6c; font-weight: 600; }

/* 弹窗表单 */
.personnel-row { background: #fafafa; border-radius: 6px; padding: 8px 10px; margin-bottom: 8px; }
.personnel-line { display: flex; align-items: center; gap: 8px; }
.sel-emp { width: 200px; flex-shrink: 0; }
.inp-hours { width: 90px; flex-shrink: 0; }
.hours-unit { font-size: 12px; color: #909399; width: 16px; flex-shrink: 0; }
.inp-leave { width: 140px; flex-shrink: 0; }
.cost-badge { width: 80px; flex-shrink: 0; }
.inp-content { flex: 1; }
.expand-content { padding: 8px 0; font-size: 13px; }
.expand-label { font-weight: 600; color: #606266; }

/* 人员维度筛选栏 */
.personnel-filters { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding: 8px 12px; background: #fafafa; border-radius: 6px; }
.personnel-summary { font-size: 12px; color: #909399; margin-left: auto; }
.personnel-summary b { color: #303133; }
</style>
