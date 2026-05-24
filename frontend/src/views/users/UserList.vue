<template>
  <div class="page">
    <div class="page-header"><h2>账号管理</h2><el-button type="primary" @click="openDialog()">新增账号</el-button></div>

    <el-table :data="list" stripe v-loading="loading" style="margin-top:16px">
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="employee_name" label="关联员工" width="120">
        <template #default="{ row }"><span v-if="row.employee_name">{{ row.employee_name }}</span><span v-else style="color:#c0c4cc">未关联</span></template>
      </el-table-column>
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'director' ? 'danger' : row.role === 'manager' ? 'warning' : row.role === 'finance' ? 'success' : 'info'" size="small">
            {{ roleLabel(row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }"><el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ row.created_at?.slice(0, 10) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑账号' : '新增账号'" width="480px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="关联员工">
          <el-select v-model="form.employee_id" placeholder="选择员工（可选）" clearable filterable style="width:100%">
            <el-option v-for="e in employees" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户名"><el-input v-model="form.username" placeholder="登录用户名" /></el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" :placeholder="editingId ? '留空则不修改' : '设置登录密码'" show-password />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="院长" value="director" />
            <el-option label="项目经理" value="manager" />
            <el-option label="财务" value="finance" />
            <el-option label="员工" value="employee" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" v-if="editingId">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usersApi } from '@/api/users'
import type { UserItem } from '@/api/users'
import { employeesApi } from '@/api/employees'
import type { EmployeeItem } from '@/api/employees'

const list = ref<UserItem[]>([])
const employees = ref<EmployeeItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref('')

const form = ref({
  employee_id: '',
  username: '',
  password: '',
  role: 'employee',
  is_active: true,
})

function roleLabel(role: string) {
  const map: Record<string, string> = { director: '院长', manager: '项目经理', finance: '财务', employee: '员工' }
  return map[role] || role
}

async function loadList() {
  loading.value = true
  try {
    const [users, emps] = await Promise.all([usersApi.list(), employeesApi.list()])
    list.value = users
    employees.value = emps
  } finally { loading.value = false }
}

function openDialog(row?: UserItem) {
  if (row) {
    editingId.value = row.id
    form.value = {
      employee_id: row.employee_id || '',
      username: row.username,
      password: '',
      role: row.role,
      is_active: row.is_active,
    }
  } else {
    editingId.value = ''
    form.value = { employee_id: '', username: '', password: '', role: 'employee', is_active: true }
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.username) { ElMessage.warning('请输入用户名'); return }
  if (!editingId.value && !form.value.password) { ElMessage.warning('请设置密码'); return }
  if (editingId.value) {
    const data: any = { role: form.value.role, is_active: form.value.is_active }
    if (form.value.password) data.password = form.value.password
    await usersApi.update(editingId.value, data)
    ElMessage.success('更新成功')
  } else {
    await usersApi.create(form.value)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadList()
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定删除该账号？', '提示', { type: 'warning' })
  await usersApi.delete(id)
  ElMessage.success('删除成功')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.page h2 { font-size: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
</style>
