<template>
  <div class="page">
    <h2>我的工时</h2>

    <!-- 日期选择 -->
    <el-row :gutter="16" style="margin-top:12px" align="middle">
      <el-col :xs="24" :sm="6">
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日期"
          value-format="YYYY-MM-DD"
          @change="onDateChange"
          @visible-change="onVisibleChange"
          style="width:100%"
        />
      </el-col>
      <el-col :xs="24" :sm="6">
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
import { ref, onMounted, onUnmounted } from 'vue'
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

// 有工时记录的日期集合（存储为 ISO 日期字符串）
const workDateSet = ref(new Set<string>())

function fmtDate(d: string | Date): string {
  if (d instanceof Date) return d.toISOString().slice(0, 10)
  return d
}

// ====== 全局 MutationObserver：自动高亮任何日期选择器面板 ======
let _bodyObserver: MutationObserver | null = null
const _panelObservers: MutationObserver[] = []  // 保存所有面板 observer 引用
let _panelTimers: ReturnType<typeof setTimeout>[] = []

function findAndHighlightPanel() {
  tryHighlightAll()
}

function doHighlight(panel: HTMLElement) {
  // 从面板文本中提取年份和月份（匹配"2026年6月"等格式）
  const text = panel.textContent || ''
  const m = text.match(/(\d{4})\s*年\s*(\d{1,2})\s*月/)
  // 或者匹配 month table 中的表头
  const m2 = text.match(/(\d{4})\s*[年/\-]\s*(\d{1,2})/)
  const matched = m || m2
  if (!matched) return
  const y = parseInt(matched[1]), mo = parseInt(matched[2])
  const prefix = `${y}-${String(mo).padStart(2, '0')}-`

  // 找到所有当前月份的日期单元格
  // 优先用 td.available（Element Plus 标准类名），fallback 到排除 prev/next-month 的 td
  let tds = panel.querySelectorAll('td.available')
  if (tds.length === 0) {
    tds = panel.querySelectorAll('td:not(.prev-month):not(.next-month)')
  }
  if (tds.length < 5) {
    // 最后兜底：所有 td
    tds = panel.querySelectorAll('td')
  }
  tds.forEach(td => {
    td.classList.remove('work-day')
    // 获取 td 内的纯数字文本（1-31）
    const numText = td.textContent?.trim() || ''
    const day = parseInt(numText)
    if (day < 1 || day > 31 || numText.length > 2) return
    // 确保不是年份或其他数字（额外检查：文本只能是1-2位数字）
    if (!/^\d{1,2}$/.test(numText)) return

    const ds = prefix + String(day).padStart(2, '0')
    if (workDateSet.value.has(ds)) {
      td.classList.add('work-day')
    }
  })
}

// 记录已处理的 panel
const _seenPanels = new WeakSet()

function tryHighlightAll() {
  document.querySelectorAll('.el-picker-panel').forEach(panel => {
    if (_seenPanels.has(panel)) return  // 跳过已处理的
    // 检查 panel 是否已渲染完毕
    const tds = panel.querySelectorAll('td')
    if (tds.length < 28) return  // 还没渲染完
    _seenPanels.add(panel as Element)

    doHighlight(panel as HTMLElement)

    // 监听内部变化（月份切换）
    const obs = new MutationObserver(() => {
      _panelTimers.push(setTimeout(() => doHighlight(panel as HTMLElement), 80))
    })
    obs.observe(panel, { childList: true, subtree: true, characterData: true })
    _panelObservers.push(obs)  // 保存引用以便清理
  })
}

function onVisibleChange(visible: boolean) {
  if (visible) {
    loadWorkDates().then(() => {
      _panelTimers.push(setTimeout(findAndHighlightPanel, 100))
      _panelTimers.push(setTimeout(findAndHighlightPanel, 300))
    })
  }
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

function onDateChange() {
  loadData()
}

// 加载所有工时记录日期（前后6个月）
async function loadWorkDates() {
  const now = new Date()
  const set = new Set<string>()
  for (let offset = -6; offset <= 6; offset++) {
    const d = new Date(now.getFullYear(), now.getMonth() + offset, 1)
    try {
      const res = await personalWorkApi.monthlyCalendar(d.getFullYear(), d.getMonth() + 1)
      for (const item of res.dates) set.add(item.date)
    } catch { /* skip */ }
  }
  workDateSet.value = set
  return set
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
  loadWorkDates() // 刷新日历高亮数据
}

async function handleDelete(id: string) {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await personalWorkApi.delete(id)
  ElMessage.success('已删除')
  loadData()
  loadWorkDates()
}

onMounted(() => {
  loadData()
  loadWorkDates()
  // 全局监听：检测任意日期选择器面板出现在 DOM 中
  _bodyObserver = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node instanceof HTMLElement) {
          if (node.classList.contains('el-picker-panel') || node.querySelector('.el-picker-panel')) {
            _panelTimers.push(setTimeout(findAndHighlightPanel, 100))
          }
        }
      }
    }
    // 兜底扫描
    _panelTimers.push(setTimeout(findAndHighlightPanel, 200))
  })
  _bodyObserver.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  _bodyObserver?.disconnect()
  _bodyObserver = null
  // 断开所有面板 observer
  _panelObservers.forEach(obs => obs.disconnect())
  _panelObservers.length = 0
  // 清理所有定时器
  _panelTimers.forEach(clearTimeout)
  _panelTimers.length = 0
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
/* 日期选择器日历：有工时记录的日期高亮（面板在 body 下） */
.el-picker-panel td.work-day {
  color: #67c23a !important;
  font-weight: 700 !important;
  position: relative;
}
.el-picker-panel td.work-day::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  margin-left: -2px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #67c23a;
}
</style>
