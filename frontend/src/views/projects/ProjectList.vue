<template>
  <div class="page">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="openDialog()" v-if="canEdit">新建项目</el-button>
    </div>

    <el-row :gutter="12" style="margin-top:12px">
      <el-col :xs="24" :sm="6"><el-input v-model="keyword" placeholder="搜索项目名称" clearable @change="loadList" /></el-col>
      <el-col :xs="24" :sm="4">
        <el-select v-model="filterStatus" placeholder="状态" clearable @change="loadList" style="width:100%">
          <el-option label="进行中" value="进行中" /><el-option label="已完成" value="已完成" /><el-option label="已暂停" value="已暂停" />
        </el-select>
      </el-col>
    </el-row>

    <el-table :data="list" stripe v-loading="loading" style="margin-top:12px" @row-click="(row:ProjectItem) => router.push('/projects/'+row.id)">
      <el-table-column prop="project_code" label="项目编号" width="130" />
      <el-table-column prop="name" label="项目名称" min-width="180" />
      <el-table-column prop="party_a" label="甲方" min-width="160" />
      <el-table-column prop="manager_name" label="项目经理" width="100" />
      <el-table-column prop="fund_source" label="资金来源" width="120" />
      <el-table-column prop="project_nature" label="项目性质" width="120" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status==='进行中'?'success':row.status==='已暂停'?'warning':'info'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click.stop="router.push('/projects/'+row.id)">详情</el-button>
          <el-button size="small" @click.stop="router.push('/projects/'+row.id+'/finance')">财务</el-button>
          <el-button v-if="canEdit" size="small" @click.stop="openDialog(row)">编辑</el-button>
          <el-button v-if="canDelete" size="small" type="danger" @click.stop="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page" :page-size="20" :total="total"
      layout="prev, pager, next" style="margin-top:16px;justify-content:center"
      @current-change="loadList"
    />

    <el-dialog v-model="dialogVisible" :title="editingId?'编辑项目':'新建项目'" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="项目编号"><el-input v-model="form.project_code" :placeholder="editingId?'':'留空自动生成'" /></el-form-item>
        <el-form-item label="项目名称"><el-input v-model="form.name" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="省"><el-input v-model="form.region_province" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="市"><el-input v-model="form.region_city" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="甲方"><el-input v-model="form.party_a" /></el-form-item>
        <el-form-item label="乙方"><el-input v-model="form.party_b" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.contact_phone" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12">
            <el-form-item label="资金来源">
              <el-select v-model="form.fund_source" style="width:100%"><el-option v-for="s in ['财政拨款','其他经费财政','自筹']" :key="s" :label="s" :value="s" /></el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="项目性质">
              <el-select v-model="form.project_nature" style="width:100%"><el-option v-for="s in ['工程测绘','地质勘查','其他']" :key="s" :label="s" :value="s" /></el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目经理">
          <el-select v-model="form.manager_id" filterable clearable style="width:100%" placeholder="选择项目经理">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%"><el-option label="进行中" value="进行中" /><el-option label="已完成" value="已完成" /><el-option label="已暂停" value="已暂停" /></el-select>
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectsApi } from '@/api/projects'
import type { ProjectItem } from '@/api/projects'
import { employeesApi } from '@/api/employees'
import type { EmployeeItem } from '@/api/employees'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const canEdit = computed(() => ['院长', '副院长', '项目经理'].includes(authStore.user?.role || ''))
const canDelete = computed(() => authStore.user?.role === '院长')

const list = ref<ProjectItem[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const keyword = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const editingId = ref('')
const employees = ref<EmployeeItem[]>([])

type ProjectForm = {
  project_code: string
  name: string
  region_province: string
  region_city: string
  party_a: string
  party_b: string
  contact_person: string
  contact_phone: string
  fund_source: string
  project_nature: string
  manager_id: string | null
  status: string
  remark: string
}
const defaultForm = (): ProjectForm => ({
  project_code: '', name: '', region_province: '', region_city: '', party_a: '', party_b: '',
  contact_person: '', contact_phone: '', fund_source: '', project_nature: '',
  manager_id: null, status: '进行中', remark: '',
})
const toForm = (row: ProjectItem): ProjectForm => ({
  project_code: row.project_code,
  name: row.name,
  region_province: row.region_province ?? '',
  region_city: row.region_city ?? '',
  party_a: row.party_a ?? '',
  party_b: row.party_b ?? '',
  contact_person: row.contact_person ?? '',
  contact_phone: row.contact_phone ?? '',
  fund_source: row.fund_source ?? '',
  project_nature: row.project_nature ?? '',
  manager_id: row.manager_id,
  status: row.status,
  remark: row.remark ?? '',
})
const nullableFields: Array<keyof ProjectForm> = [
  'project_code', 'region_province', 'region_city', 'party_a', 'party_b',
  'contact_person', 'contact_phone', 'fund_source', 'project_nature', 'manager_id', 'remark',
]
function projectPayload() {
  const payload: Partial<Record<keyof ProjectForm, string | null>> = { ...form.value }
  for (const key of nullableFields) {
    if (payload[key] === '') payload[key] = null
  }
  if (editingId.value && !payload.project_code) {
    delete payload.project_code
  }
  return payload
}
const form = ref<ProjectForm>(defaultForm())

async function loadList() {
  loading.value = true
  try {
    const res = await projectsApi.list({ page: page.value, page_size: 20, keyword: keyword.value, status: filterStatus.value || undefined })
    list.value = res.items; total.value = res.total
  } finally { loading.value = false }
}

async function openDialog(row?: ProjectItem) {
  if (!employees.value.length) { const res = await employeesApi.list(); employees.value = res }
  if (row) {
    editingId.value = row.id
    form.value = toForm(row)
  } else {
    editingId.value = ''
    form.value = defaultForm()
  }
  dialogVisible.value = true
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定删除该项目？将同时删除所有关联数据（合同、预算、执行单、财务事件等）。', '警告', { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' })
  await projectsApi.delete(id)
  ElMessage.success('项目已删除')
  loadList()
}

async function handleSave() {
  const payload = projectPayload()
  if (editingId.value) {
    await projectsApi.update(editingId.value, payload)
    ElMessage.success('更新成功')
  } else {
    await projectsApi.create(payload)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.page h2 { font-size: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
</style>
