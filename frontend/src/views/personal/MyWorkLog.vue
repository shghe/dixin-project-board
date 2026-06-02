<template>
  <div class="page">
    <h2>我的工时</h2>

    <!-- 日期选择 -->
    <el-row :gutter="16" style="margin-top:12px" align="middle">
      <el-col :xs="12" :sm="4">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          @change="loadData"
          @visible-change="onPickerVisible"
          style="width:100%"
        />
      </el-col>
      <el-col :xs="12" :sm="8">
        <span class="summary-text">
          合计 <b :style="{color: summary.total_hours>=8?'#67c23a':'#e6a23c'}">{{ summary.total_hours }}h</b>
          &nbsp;剩余 <b :style="{color: summary.remaining>0?'#f56c6c':'#67c23a'}">{{ summary.remaining }}h</b>
        </span>
      </el-col>
    </el-row>

    <!-- 项目工时 + 非项目工时 同级双栏 -->
    <el-row :gutter="16" style="margin-top:12px">
      <!-- 项目工时 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header><div class="card-title">项目工时 <span class="card-sum">{{ summary.project_hours }}h</span></div></template>
          <div v-if="summary.project_details.length" class="work-list">
            <div v-for="(p, i) in summary.project_details" :key="i" class="work-item">
              <div class="work-info"><span class="work-label">项目</span><span class="work-content">{{ p.project_name }}：{{ p.work_content }}</span></div>
              <span class="work-hours">{{ p.work_hours }}h</span>
            </div>
          </div>
          <el-empty v-else description="当日无项目工时" :image-size="40" />
        </el-card>
      </el-col>

      <!-- 非项目工时 -->
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-title">
              非项目工时 <span class="card-sum green">{{ summary.personal_hours }}h</span>
              <el-button type="primary" size="small" style="margin-left:auto" @click="openDialog()">添加</el-button>
            </div>
          </template>
          <div v-if="entries.length" class="work-list">
            <div v-for="e in entries" :key="e.id" class="work-item">
              <div class="work-info">
                <el-tag size="small" type="info">{{ e.category }}</el-tag>
                <span class="work-content">{{ e.work_content }}</span>
              </div>
              <div style="display:flex;align-items:center;gap:4px">
                <span class="work-hours" style="margin-right:8px">{{ e.work_hours }}h</span>
                <el-button size="small" text @click="openDialog(e)">编辑</el-button>
                <el-button size="small" text type="danger" @click="handleDelete(e.id)">删除</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无记录，点击添加" :image-size="40" />
        </el-card>
      </el-col>
    </el-row>

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
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { personalWorkApi } from '@/api/personalWork'
import type { PersonalWorkEntryItem, DailySummary } from '@/api/personalWork'

const selectedDate = ref(new Date().toISOString().slice(0, 10))
const summary = ref<DailySummary>({
  record_date: '', project_hours: 0, project_breakdown: [], project_details: [],
  personal_hours: 0, total_hours: 0, remaining: 8, entries: [],
})
const entries = ref<PersonalWorkEntryItem[]>([])
const dialogVisible = ref(false)
const editingId = ref('')
const form = ref({ category: '院务工作', work_hours: 0, work_content: '' })

// 有工时记录的日期集合（key: "YYYY-MM" → Set of day numbers）
const workDayMap = ref<Map<string, Set<number>>>(new Map())

function fmtDate(d: string | Date): string {
  if (d instanceof Date) return d.toISOString().slice(0, 10)
  return d
}

async function loadData() {
  const ds = fmtDate(selectedDate.value)
  const [s, e] = await Promise.all([
    personalWorkApi.dailySummary(ds),
    personalWorkApi.list({ record_date: ds }),
  ])
  summary.value = s
  entries.value = e
}

// 加载最近几个月工时记录日期
async function loadWorkDates() {
  const now = new Date()
  const map = new Map<string, Set<number>>()
  // 加载前3个月到后3个月
  for (let offset = -3; offset <= 3; offset++) {
    const d = new Date(now.getFullYear(), now.getMonth() + offset, 1)
    const y = d.getFullYear(), m = d.getMonth() + 1
    try {
      const res = await personalWorkApi.monthlyCalendar(y, m)
      for (const item of res.dates) {
        const dd = new Date(item.date + 'T00:00:00')
        const key = `${dd.getFullYear()}-${String(dd.getMonth() + 1).padStart(2, '0')}`
        if (!map.has(key)) map.set(key, new Set())
        map.get(key)!.add(dd.getDate())
      }
    } catch { /* skip */ }
  }
  workDayMap.value = map
  // 如果面板已打开，立即刷新高亮
  nextTick(() => highlightCalendar())
}

// DOM 方式高亮日期选择器面板中的日期
function highlightCalendar() {
  const panel = document.querySelector('.el-picker-panel__body')
  if (!panel) return
  // 找到当前显示的 year/month
  const monthLabels = panel.querySelectorAll('.el-date-table')
  // 获取面板头部显示的日期
  const headerSpan = document.querySelector('.el-date-picker__header-label')
  if (!headerSpan) return
  const headerText = headerSpan.textContent || ''
  const match = headerText.match(/(\d{4})\s*年\s*(\d{1,2})\s*月/)
  if (!match) return
  const key = `${match[1]}-${String(parseInt(match[2])).padStart(2, '0')}`
  const days = workDayMap.value.get(key)

  // 清除旧的高亮
  panel.querySelectorAll('.work-highlight').forEach(el => el.classList.remove('work-highlight'))

  if (!days || days.size === 0) return

  // 找到所有日期单元格并高亮
  const cells = panel.querySelectorAll('td.available .el-date-table-cell__text')
  cells.forEach(el => {
    const num = parseInt(el.textContent || '')
    if (days.has(num)) {
      const td = el.closest('td')
      if (td) td.classList.add('work-highlight')
    }
  })
}

// 面板可见时加载数据并高亮
function onPickerVisible(visible: boolean) {
  if (visible) {
    loadWorkDates()
    // 延迟执行 DOM 操作，等面板渲染完成
    setTimeout(() => highlightCalendar(), 100)
    // 监听月份切换
    setTimeout(() => {
      const prevBtn = document.querySelector('.el-date-picker__header button:first-child')
      const nextBtn = document.querySelector('.el-date-picker__header button:last-child')
      const headerEl = document.querySelector('.el-date-picker__header-label')
      const observer = new MutationObserver(() => {
        setTimeout(() => highlightCalendar(), 50)
      })
      if (headerEl) observer.observe(headerEl, { characterData: true, subtree: true, childList: true })
      if (prevBtn) prevBtn.addEventListener('click', () => setTimeout(() => highlightCalendar(), 100))
      if (nextBtn) nextBtn.addEventListener('click', () => setTimeout(() => highlightCalendar(), 100))
    }, 200)
  }
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
    await personalWorkApi.create({ ...form.value, record_date: fmtDate(selectedDate.value) })
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

onMounted(() => {
  loadData()
  loadWorkDates()
})
</script>

<style scoped>
h2 { font-size: 20px; }
.summary-text { font-size: 16px; color: #606266; }
.summary-text b { font-weight: 700; }
.card-title { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; }
.card-sum { font-size: 20px; font-weight: 700; color: #409eff; }
.card-sum.green { color: #67c23a; }
.work-list { max-height: 360px; overflow-y: auto; }
.work-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.work-item:last-child { border-bottom: none; }
.work-info { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
.work-label { font-size: 11px; color: #fff; background: #409eff; border-radius: 3px; padding: 1px 6px; flex-shrink: 0; }
.work-content { font-size: 13px; color: #606266; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.work-hours { font-size: 14px; font-weight: 700; color: #409eff; flex-shrink: 0; }
</style>

<style>
/* 全局样式：日期选择器中有工时记录的日期高亮 */
.el-picker-panel td.work-highlight .el-date-table-cell__text {
  color: #67c23a !important;
  font-weight: 700;
}
.el-picker-panel td.work-highlight .el-date-table-cell {
  position: relative;
}
.el-picker-panel td.work-highlight .el-date-table-cell::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #67c23a;
}
.el-picker-panel td.work-highlight.current .el-date-table-cell::after {
  background: #fff;
}
</style>
