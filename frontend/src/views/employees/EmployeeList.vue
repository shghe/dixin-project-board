<template>
  <div class="page">
    <div class="page-header"><h2>人员管理</h2><div><el-button type="warning" @click="openWageDialog" v-if="canEdit" style="margin-right:8px">工资标准设置</el-button><el-button type="primary" @click="openDialog()" v-if="canEdit">新增员工</el-button></div></div>
    <el-table :data="list" stripe v-loading="loading" style="margin-top:16px">
      <el-table-column prop="employee_code" label="编号" width="130" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="work_type" label="工种" width="100" />
      <el-table-column label="人员类别" width="100"><template #default="{row}"><el-tag :type="row.personnel_type==='事业人员'?'success':row.personnel_type==='企业人员'?'warning':'info'">{{ row.personnel_type }}</el-tag></template></el-table-column>
      <el-table-column prop="department" label="部门" width="140" />
      <el-table-column prop="position" label="职位" width="120" />
      <el-table-column label="日工资" width="100"><template #default="{row}">¥{{ row.daily_wage }}</template></el-table-column>
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="status" label="状态" width="80"><template #default="{row}"><el-tag :type="row.status==='在职'?'success':row.status==='借调'?'warning':'info'">{{ row.status }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="160" fixed="right" v-if="canEdit">
        <template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button><el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button></template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="wageDialogVisible" title="工资标准设置" width="400px">
      <el-form label-width="100px">
        <el-form-item label="事业编日工资"><el-input-number v-model="wageForm.事业人员" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="企业编日工资"><el-input-number v-model="wageForm.企业人员" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="派遣日工资"><el-input-number v-model="wageForm.派遣人员" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="wageDialogVisible=false">取消</el-button><el-button type="primary" @click="handleSaveWages">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="dialogVisible" :title="editingId?'编辑员工':'新增员工'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="工种"><el-select v-model="form.work_type" style="width:100%" @change="syncDailyWage"><el-option v-for="t in workTypes" :key="t" :label="t" :value="t" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="人员类别"><el-select v-model="form.personnel_type" style="width:100%" @change="syncDailyWage"><el-option label="事业人员" value="事业人员" /><el-option label="企业人员" value="企业人员" /><el-option label="派遣人员" value="派遣人员" /></el-select></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="部门"><el-input v-model="form.department" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="职位"><el-input v-model="form.position" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="日工资"><el-input-number v-model="form.daily_wage" :min="0" style="width:100%" disabled /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="入职日期"><el-date-picker v-model="form.hire_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="状态"><el-select v-model="form.status" style="width:100%"><el-option label="在职" value="在职" /><el-option label="离职" value="离职" /><el-option label="借调" value="借调" /></el-select></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { employeesApi } from '@/api/employees'; import type { EmployeeItem } from '@/api/employees'
import { settingsApi } from '@/api/settings'; import type { PersonnelWages } from '@/api/settings'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const canEdit = computed(() => authStore.user?.role === '院长')
const list = ref<EmployeeItem[]>([]); const loading = ref(false)
const dialogVisible = ref(false); const editingId = ref('')
const wageDialogVisible = ref(false)
const workTypes = ['院长','副院长','综合员','司机','项目经理','技术员']
const personnelWageMap = reactive<PersonnelWages>({ 事业人员: 650, 企业人员: 500, 派遣人员: 380 })
const wageForm = reactive<PersonnelWages>({ 事业人员: 650, 企业人员: 500, 派遣人员: 380 })
type EmployeeForm = {
  name: string
  work_type: string
  personnel_type: string
  department: string
  position: string
  phone: string
  daily_wage: number
  hire_date: string | null
  status: string
  remark: string
}
const defaultForm = (): EmployeeForm => ({ name:'',work_type:'',personnel_type:'事业人员',department:'地理信息院',position:'',phone:'',daily_wage:personnelWageMap['事业人员'],hire_date:null,status:'在职',remark:'' })
const toForm = (row: EmployeeItem): EmployeeForm => ({
  name: row.name,
  work_type: row.work_type,
  personnel_type: row.personnel_type,
  department: row.department,
  position: row.position ?? '',
  phone: row.phone ?? '',
  daily_wage: row.daily_wage,
  hire_date: row.hire_date || null,
  status: row.status,
  remark: row.remark ?? '',
})
const form = ref<EmployeeForm>(defaultForm())

function syncDailyWage() {
  const pt = form.value.personnel_type as keyof PersonnelWages
  form.value.daily_wage = personnelWageMap[pt] || 488
  if (!form.value.position) form.value.position = form.value.work_type
}

async function loadWages() {
  try {
    const wages = await settingsApi.getWages()
    Object.assign(personnelWageMap, wages)
  } catch { /* use defaults */ }
}

function openWageDialog() {
  wageForm.事业人员 = personnelWageMap.事业人员
  wageForm.企业人员 = personnelWageMap.企业人员
  wageForm.派遣人员 = personnelWageMap.派遣人员
  wageDialogVisible.value = true
}

async function handleSaveWages() {
  await settingsApi.updateWages({ ...wageForm })
  Object.assign(personnelWageMap, wageForm)
  await loadList()
  ElMessage.success('工资标准已更新，员工日工资已同步')
  wageDialogVisible.value = false
}

async function loadList() { loading.value=true; try{list.value=await employeesApi.list()}finally{loading.value=false} }

function openDialog(row?: EmployeeItem) {
  if (row) { editingId.value=row.id; form.value=toForm(row) }
  else { editingId.value=''; form.value=defaultForm(); syncDailyWage() }
  dialogVisible.value=true
}
async function handleSave() {
  if(editingId.value){await employeesApi.update(editingId.value,form.value);ElMessage.success('更新成功')}
  else{await employeesApi.create(form.value);ElMessage.success('新增成功')}
  dialogVisible.value=false; loadList()
}
async function handleDelete(id:string){await ElMessageBox.confirm('确定删除？','提示',{type:'warning'});await employeesApi.delete(id);ElMessage.success('删除成功');loadList()}
onMounted(async () => { await loadWages(); loadList() })
</script>
<style scoped>.page h2{font-size:20px}.page-header{display:flex;justify-content:space-between;align-items:center}</style>
