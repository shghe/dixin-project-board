<template>
  <div class="page">
    <div class="page-header">
      <div>
        <el-button text @click="$router.back()"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
        <h2>{{ project?.name || '项目预算' }}</h2>
      </div>
      <div>
        <el-button type="success" @click="exportExcel" :loading="exporting" size="small">导出Excel</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" type="border-card" @tab-change="onTabChange">
      <!-- ==================== 项目概况 ==================== -->
      <el-tab-pane label="项目概况" name="summary">
        <div class="overview-table">
          <h3>工程概况</h3>
          <table class="info-table">
            <tr><td class="label">工程名称</td><td :colspan="3">{{ summary.project_name || '-' }}</td></tr>
            <tr><td class="label">甲方全称</td><td :colspan="3">{{ summary.party_a || '-' }}</td></tr>
            <tr>
              <td class="label">联系人</td><td>{{ summary.contact_person || '-' }}</td>
              <td class="label">电话</td><td>{{ summary.contact_phone || '-' }}</td>
            </tr>
            <tr><td class="label">甲方通讯地址</td><td :colspan="3">{{ summary.address || '-' }}</td></tr>
            <tr><td class="label">工程所在地</td><td :colspan="3">{{ summary.location || '-' }}</td></tr>
            <tr>
              <td class="label">开工日期</td><td>{{ summary.start_date || '-' }}</td>
              <td class="label">竣工日期</td><td>{{ summary.end_date || '-' }}</td>
            </tr>
            <tr>
              <td class="label">计划工期</td><td>{{ summary.planned_duration || '-' }}</td>
              <td class="label">合同签订时间</td><td>{{ summary.contract_sign_date || '-' }}</td>
            </tr>
            <tr>
              <td class="label">合同额</td><td>¥{{ (summary.contract_amount || 0).toLocaleString() }}</td>
              <td class="label">税率</td><td>{{ ((summary.tax_rate || 0) * 100).toFixed(0) }}%</td>
            </tr>
            <tr>
              <td class="label">合同编号</td><td>{{ summary.contract_no || '-' }}</td>
              <td class="label">实施单位</td><td>{{ summary.implementing_unit || '-' }}</td>
            </tr>
            <tr>
              <td class="label">项目经理</td><td>{{ summary.project_manager || '-' }}</td>
              <td class="label">技术负责</td><td>{{ summary.tech_lead || '-' }}</td>
            </tr>
          </table>

          <h3>编制依据</h3>
          <div class="info-text">{{ summary.compilation_basis || '-' }}</div>

          <h3>施工条件</h3>
          <div class="info-text">{{ summary.construction_conditions || '-' }}</div>

          <h3>工作内容</h3>
          <div class="info-text">{{ summary.work_content || '-' }}</div>

          <h3>其他</h3>
          <div class="info-text">{{ summary.other_info || '-' }}</div>

          <table class="info-table" style="margin-top:16px">
            <tr>
              <td class="label">填表</td><td>{{ summary.drafter || '-' }}</td>
              <td class="label">校核</td><td>{{ summary.checker || '-' }}</td>
              <td class="label">审核</td><td>{{ summary.reviewer || '-' }}</td>
            </tr>
          </table>
          <el-button type="primary" @click="openSummaryDialog" style="margin-top:12px" v-if="canEdit">编辑概况</el-button>
        </div>

        <!-- 编辑概况对话框 -->
        <el-dialog v-model="dlg.summary" title="编辑项目概况" width="700px">
          <el-form :model="summary" label-width="120px" size="small">
            <el-row :gutter="16">
              <el-col :xs="24" :sm="12"><el-form-item label="通讯地址"><el-input v-model="summary.address" /></el-form-item></el-col>
              <el-col :xs="24" :sm="12"><el-form-item label="工程所在地"><el-input v-model="summary.location" /></el-form-item></el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :xs="24" :sm="8"><el-form-item label="开工日期"><el-input v-model="summary.start_date" /></el-form-item></el-col>
              <el-col :xs="24" :sm="8"><el-form-item label="竣工日期"><el-input v-model="summary.end_date" /></el-form-item></el-col>
              <el-col :xs="24" :sm="8"><el-form-item label="计划工期"><el-input v-model="summary.planned_duration" /></el-form-item></el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :xs="24" :sm="12"><el-form-item label="税率"><el-input-number v-model="summary.tax_rate" :min="0" :max="1" :step="0.01" style="width:100%" /></el-form-item></el-col>
              <el-col :xs="24" :sm="12"><el-form-item label="实施单位"><el-input v-model="summary.implementing_unit" /></el-form-item></el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :xs="24" :sm="12"><el-form-item label="技术负责"><el-input v-model="summary.tech_lead" /></el-form-item></el-col>
              <el-col :xs="24" :sm="12"><el-form-item label="校核"><el-input v-model="summary.checker" /></el-form-item></el-col>
            </el-row>
            <el-form-item label="编制依据"><el-input v-model="summary.compilation_basis" type="textarea" :rows="2" /></el-form-item>
            <el-form-item label="施工条件"><el-input v-model="summary.construction_conditions" type="textarea" :rows="3" /></el-form-item>
            <el-form-item label="工作内容"><el-input v-model="summary.work_content" type="textarea" :rows="3" /></el-form-item>
            <el-form-item label="其他"><el-input v-model="summary.other_info" type="textarea" :rows="2" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="dlg.summary=false" size="small">取消</el-button><el-button type="primary" @click="saveSummary" :loading="saving" size="small">保存</el-button></template>
        </el-dialog>
      </el-tab-pane>

      <!-- ==================== 总表 ==================== -->
      <el-tab-pane label="总表" name="rollup">
        <div v-loading="loadingRollup">
          <el-row :gutter="12" style="margin-bottom:12px">
            <el-col :xs="12" :sm="4"><div class="stat-card"><div class="stat-label">工程总费用</div><div class="stat-val">¥{{ rollup?.total?.toLocaleString() || 0 }}</div></div></el-col>
            <el-col :xs="12" :sm="4"><div class="stat-card"><div class="stat-label">含税合同额</div><div class="stat-val">¥{{ (rollup?.contract_amount || 0).toLocaleString() }}</div></div></el-col>
            <el-col :xs="12" :sm="4"><div class="stat-card"><div class="stat-label">应缴税额</div><div class="stat-val">¥{{ (rollup?.ying_jiao || 0).toLocaleString() }}</div></div></el-col>
            <el-col :xs="12" :sm="4"><div class="stat-card"><div class="stat-label">附加税</div><div class="stat-val">¥{{ (rollup?.fu_jia || 0).toLocaleString() }}</div></div></el-col>
            <el-col :xs="12" :sm="4"><div class="stat-card"><div class="stat-label">工程成本</div><div class="stat-val">¥{{ (rollup?.gong_cheng_cb || 0).toLocaleString() }}</div></div></el-col>
            <el-col :xs="12" :sm="4"><div class="stat-card" :class="{ 'profit-positive': (rollup?.mao_li_run || 0) > 0, 'profit-negative': (rollup?.mao_li_run || 0) < 0 }"><div class="stat-label">毛利润</div><div class="stat-val">¥{{ (rollup?.mao_li_run || 0).toLocaleString() }}</div></div></el-col>
          </el-row>
          <el-table :data="flatRollup" border size="small">
            <el-table-column label="编号" width="80" align="center">
              <template #default="{row}">
                <span :style="{ fontWeight: row._level <= 1 ? 'bold' : 'normal' }">{{ row.code }}</span>
              </template>
            </el-table-column>
            <el-table-column label="科目" min-width="240">
              <template #default="{row}">
                <span :style="{ paddingLeft: (row._level * 24) + 'px', fontWeight: row._level <= 1 ? 'bold' : 'normal' }">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="科目代码" width="150">
              <template #default="{row}">{{ row.code_desc || '' }}</template>
            </el-table-column>
            <el-table-column label="包括事项" min-width="200" show-overflow-tooltip>
              <template #default="{row}">{{ row.includes || '' }}</template>
            </el-table-column>
            <el-table-column label="金额" width="160" align="right">
              <template #default="{row}">
                <span :style="{ fontWeight: row._level <= 2 ? 'bold' : 'normal', fontFamily: 'monospace' }">{{ row.amount?.toLocaleString() || 0 }}</span>
              </template>
            </el-table-column>
            <el-table-column label="备注" width="100">
              <template #default="{row}">{{ row.remark || '' }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- ==================== 人工费 ==================== -->
      <el-tab-pane label="人工费" name="personnel">
        <div style="margin-bottom:8px">
          <el-button size="small" type="primary" @click="openPersonnelDialog()" v-if="canEdit">添加人员</el-button>
        </div>
        <el-table :data="personnelList" border size="small">
          <el-table-column prop="category" label="类别" width="100" />
          <el-table-column prop="position" label="岗位" width="100" />
          <el-table-column prop="employee_name" label="姓名" width="100" />
          <el-table-column prop="work_months" label="工作月" width="70" align="right" />
          <el-table-column prop="field_months" label="野外月" width="70" align="right" />
          <el-table-column prop="salary_subtotal" label="薪酬小计" width="110" align="right">
            <template #default="{row}">¥{{ row.salary_subtotal?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="welfare_subtotal" label="福利费小计" width="110" align="right">
            <template #default="{row}">¥{{ row.welfare_subtotal?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="coordination_subtotal" label="单位统筹小计" width="120" align="right">
            <template #default="{row}">¥{{ row.coordination_subtotal?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="union_subtotal" label="工会经费小计" width="110" align="right">
            <template #default="{row}">¥{{ row.union_subtotal?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="合计" width="110" align="right">
            <template #default="{row}"><b>¥{{ row.total?.toLocaleString() }}</b></template>
          </el-table-column>
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openPersonnelDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deletePersonnel(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="personnelList.length" class="table-summary">
          <span class="sum-cell w100">合计</span>
          <span class="sum-cell w100" />
          <span class="sum-cell w100" />
          <span class="sum-cell w70 right">{{ pSum.work_months.toLocaleString() }}</span>
          <span class="sum-cell w70 right">{{ pSum.field_months.toLocaleString() }}</span>
          <span class="sum-cell w110 right">¥{{ pSum.salary_subtotal.toLocaleString() }}</span>
          <span class="sum-cell w110 right">¥{{ pSum.welfare_subtotal.toLocaleString() }}</span>
          <span class="sum-cell w120 right">¥{{ pSum.coordination_subtotal.toLocaleString() }}</span>
          <span class="sum-cell w110 right">¥{{ pSum.union_subtotal.toLocaleString() }}</span>
          <span class="sum-cell w110 right"><b>¥{{ pSum.total.toLocaleString() }}</b></span>
          <span class="sum-cell w130" v-if="canEdit" />
        </div>
        <el-empty v-if="!personnelList.length" description="暂无人员" />
      </el-tab-pane>

      <!-- ==================== 材料/机械 ==================== -->
      <el-tab-pane label="材料/机械" name="mat_equip">
        <h4 style="margin-bottom:8px">材料费</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openMatDialog()" v-if="canEdit">添加材料</el-button></div>
        <el-table :data="materialList" border size="small">
          <el-table-column prop="category" label="科目" width="120" />
          <el-table-column prop="name" label="名称" min-width="120" />
          <el-table-column prop="model" label="型号" width="100" />
          <el-table-column prop="unit" label="单位" width="60" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column prop="remark" label="说明" width="150" />
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openMatDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteMaterial(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <h4 style="margin:16px 0 8px">机械使用费</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openEquipDialog()" v-if="canEdit">添加设备</el-button></div>
        <el-table :data="equipList" border size="small">
          <el-table-column prop="classification" label="分类" width="120" />
          <el-table-column prop="content" label="内容" min-width="120" />
          <el-table-column prop="counterparty" label="对方单位" min-width="120" />
          <el-table-column prop="model" label="型号" width="100" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openEquipDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteEquipment(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- ==================== 其他费用 ==================== -->
      <el-tab-pane label="其他费用" name="others">
        <!-- 其他直接费 -->
        <h4 style="margin-bottom:8px">其他直接费</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openDCDialog()" v-if="canEdit">添加费用</el-button></div>
        <el-table :data="dcList" border size="small">
          <el-table-column prop="category" label="科目" width="120" />
          <el-table-column prop="content" label="内容" min-width="120" />
          <el-table-column prop="unit" label="单位" width="60" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column prop="remark" label="说明" width="150" />
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openDCDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteDC(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 劳务费 -->
        <h4 style="margin:16px 0 8px">劳务费（外聘）</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openLaborDialog()" v-if="canEdit">添加劳务</el-button></div>
        <el-table :data="laborList" border size="small">
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="position" label="岗位" width="100" />
          <el-table-column prop="employee_name" label="姓名" width="100" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openLaborDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteLabor(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分包工程款 -->
        <h4 style="margin:16px 0 8px">分包工程款</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openSubDialog()" v-if="canEdit">添加分包</el-button></div>
        <el-table :data="subList" border size="small">
          <el-table-column prop="category" label="类别" width="130" />
          <el-table-column prop="item_name" label="项目" min-width="120" />
          <el-table-column prop="counterparty" label="对方单位" min-width="120" />
          <el-table-column prop="workload" label="工作量" width="80" align="right" />
          <el-table-column prop="unit_price" label="单价" width="100" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openSubDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteSub(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 研发+其他 -->
        <h4 style="margin:16px 0 8px">研发 / 其他费用</h4>
        <div style="margin-bottom:8px"><el-button size="small" type="primary" @click="openRDOtherDialog()" v-if="canEdit">添加费用</el-button></div>
        <el-table :data="rdOtherList" border size="small">
          <el-table-column prop="cost_group" label="分组" width="120" />
          <el-table-column prop="item" label="项目" min-width="120" />
          <el-table-column prop="unit" label="单位" width="80" />
          <el-table-column prop="base_price" label="基价" width="100" align="right" />
          <el-table-column prop="quantity" label="数量" width="80" align="right" />
          <el-table-column label="金额" width="110" align="right"><template #default="{row}"><b>¥{{ row.amount?.toLocaleString() }}</b></template></el-table-column>
          <el-table-column label="操作" width="130" v-if="canEdit">
            <template #default="{row}">
              <div class="row-actions">
                <el-button size="small" text type="primary" @click="openRDOtherDialog(row)">编辑</el-button>
                <el-button size="small" text type="danger" @click="deleteRDOther(row.id)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- ========== 对话框：人工费 ========== -->
    <el-dialog v-model="dlg.personnel" title="人工费明细" width="700px">
      <el-form :model="fPersonnel" label-width="100px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="类别"><el-select v-model="fPersonnel.category"><el-option label="事业编人员" value="事业编人员" /><el-option label="企业编人员" value="企业编人员" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="岗位"><el-input v-model="fPersonnel.position" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="姓名"><el-input v-model="fPersonnel.employee_name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="基本工资"><el-input-number v-model="fPersonnel.base_salary" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="绩效"><el-input-number v-model="fPersonnel.performance" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="野外津贴"><el-input-number v-model="fPersonnel.field_allowance" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="防暑降温"><el-input-number v-model="fPersonnel.heat_prevention" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="工会经费"><el-input-number v-model="fPersonnel.union_fee" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单位统筹"><el-input-number v-model="fPersonnel.unit_coordination" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="工作月"><el-input-number v-model="fPersonnel.work_months" :min="0" :step="0.1" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="野外月"><el-input-number v-model="fPersonnel.field_months" :min="0" :step="0.1" style="width:100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer><el-button @click="dlg.personnel=false" size="small">取消</el-button><el-button type="primary" @click="savePersonnel" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <!-- ========== 对话框：材料费 / 机械费 / 其他直接费 / 劳务费 / 分包费 / 研发其他 ========== -->
    <el-dialog v-model="dlg.material" title="材料费" width="580px">
      <el-form :model="fMaterial" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="科目"><el-select v-model="fMaterial.category" filterable allow-create><el-option v-for="c in ['原材料','专用材料费','燃油','技术资料费']" :key="c" :label="c" :value="c" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="名称"><el-input v-model="fMaterial.name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="型号"><el-input v-model="fMaterial.model" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单位"><el-input v-model="fMaterial.unit" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单价"><el-input-number v-model="fMaterial.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="数量"><el-input-number v-model="fMaterial.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="金额"><span>¥{{ (fMaterial.unit_price * fMaterial.quantity).toLocaleString() }}</span></el-form-item></el-col>
        </el-row>
        <el-form-item label="说明"><el-input v-model="fMaterial.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.material=false" size="small">取消</el-button><el-button type="primary" @click="saveMaterial" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <el-dialog v-model="dlg.equipment" title="机械使用费" width="580px">
      <el-form :model="fEquipment" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="分类"><el-input v-model="fEquipment.classification" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="内容"><el-input v-model="fEquipment.content" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="对方单位"><el-input v-model="fEquipment.counterparty" /></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="型号"><el-input v-model="fEquipment.model" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="单价"><el-input-number v-model="fEquipment.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="数量"><el-input-number v-model="fEquipment.quantity" :min="1" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="金额"><span>¥{{ (fEquipment.unit_price * fEquipment.quantity).toLocaleString() }}</span></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer><el-button @click="dlg.equipment=false" size="small">取消</el-button><el-button type="primary" @click="saveEquipment" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <el-dialog v-model="dlg.dc" title="其他直接费" width="580px">
      <el-form :model="fDC" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="科目"><el-select v-model="fDC.category" filterable allow-create><el-option v-for="c in ['运输费','装卸费','试验检测费','维修(护)费','办公费','出版印刷费','水电费','邮电费','取暖费','交通费']" :key="c" :label="c" :value="c" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="内容"><el-input v-model="fDC.content" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="单位"><el-input v-model="fDC.unit" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单价"><el-input-number v-model="fDC.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="数量"><el-input-number v-model="fDC.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="说明"><el-input v-model="fDC.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.dc=false" size="small">取消</el-button><el-button type="primary" @click="saveDC" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <el-dialog v-model="dlg.labor" title="劳务费" width="580px">
      <el-form :model="fLabor" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="类别"><el-select v-model="fLabor.category"><el-option label="临时聘用人员" value="临时聘用人员" /><el-option label="野外雇工" value="野外雇工" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="岗位"><el-input v-model="fLabor.position" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="姓名"><el-input v-model="fLabor.employee_name" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单位"><el-input v-model="fLabor.unit" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="单价"><el-input-number v-model="fLabor.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="数量"><el-input-number v-model="fLabor.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="金额"><span>¥{{ (fLabor.unit_price * fLabor.quantity).toLocaleString() }}</span></el-form-item></el-col>
        </el-row>
        <el-form-item label="说明"><el-input v-model="fLabor.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.labor=false" size="small">取消</el-button><el-button type="primary" @click="saveLabor" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <el-dialog v-model="dlg.subcontract" title="分包工程款" width="580px">
      <el-form :model="fSub" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="类别"><el-select v-model="fSub.category"><el-option v-for="c in ['工程分包费','劳务分包费','委托技术服务费','委托试验费']" :key="c" :label="c" :value="c" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="项目"><el-input v-model="fSub.item_name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12"><el-col :span="24"><el-form-item label="对方单位"><el-input v-model="fSub.counterparty" /></el-form-item></el-col></el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="工作量"><el-input-number v-model="fSub.workload" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="单价"><el-input-number v-model="fSub.unit_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="金额"><span>¥{{ (fSub.unit_price * fSub.workload).toLocaleString() }}</span></el-form-item></el-col>
        </el-row>
        <el-form-item label="说明"><el-input v-model="fSub.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.subcontract=false" size="small">取消</el-button><el-button type="primary" @click="saveSub" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>

    <el-dialog v-model="dlg.rdother" title="研发/其他费用" width="580px">
      <el-form :model="fRDOther" label-width="80px" size="small">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12"><el-form-item label="分组"><el-select v-model="fRDOther.cost_group"><el-option label="研发费用" value="研发费用" /><el-option label="其他管理费" value="其他管理费" /><el-option label="其他工料费" value="其他工料费" /></el-select></el-form-item></el-col>
          <el-col :xs="24" :sm="12"><el-form-item label="项目"><el-input v-model="fRDOther.item" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :xs="24" :sm="8"><el-form-item label="单位"><el-input v-model="fRDOther.unit" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="基价"><el-input-number v-model="fRDOther.base_price" :min="0" style="width:100%" /></el-form-item></el-col>
          <el-col :xs="24" :sm="8"><el-form-item label="数量"><el-input-number v-model="fRDOther.quantity" :min="0" style="width:100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="fRDOther.remark" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dlg.rdother=false" size="small">取消</el-button><el-button type="primary" @click="saveRDOther" :loading="saving" size="small">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { projectsApi } from '@/api/projects'
import type { ProjectItem } from '@/api/projects'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()
const projectId = route.params.id as string
const project = ref<ProjectItem | null>(null)
const activeTab = ref('summary')
const saving = ref(false)
const exporting = ref(false)
const loadingRollup = ref(false)

const canEdit = computed(() => ['院长', '副院长', '项目经理'].includes(authStore.user?.role || ''))

// ===== 项目概况 =====
const summary = ref<Record<string, any>>({
  project_name: '', party_a: '', contact_person: '', contact_phone: '',
  address: '', location: '', start_date: '', end_date: '', planned_duration: '',
  contract_amount: 0, tax_rate: 0, contract_no: '', contract_sign_date: '',
  implementing_unit: '', project_manager: '', tech_lead: '',
  compilation_basis: '', construction_conditions: '', work_content: '', other_info: '',
  drafter: '', checker: '', reviewer: '',
})

async function loadSummary() {
  const s = await projectsApi.getBudgetSummary(projectId)
  if (s) {
    summary.value = { ...summary.value, ...s }
  }
  // 始终用项目信息覆盖重复字段
  if (project.value) {
    summary.value.project_name = project.value.name
    summary.value.party_a = project.value.party_a ?? ''
    summary.value.contact_person = project.value.contact_person ?? ''
    summary.value.contact_phone = project.value.contact_phone ?? ''
    summary.value.project_manager = project.value.manager_name ?? ''
  }
  // 始终用合同信息覆盖重复字段
  try {
    const contract = await projectsApi.getContract(projectId)
    if (contract) {
      summary.value.contract_no = contract.contract_no ?? ''
      summary.value.contract_amount = contract.contract_amount ?? 0
      summary.value.contract_sign_date = contract.sign_date ?? ''
      summary.value.drafter = contract.drafter ?? ''
      summary.value.reviewer = contract.reviewer ?? ''
    }
  } catch {
    // 没有合同数据时忽略
  }
}

function openSummaryDialog() { dlg.value.summary = true }

async function saveSummary() {
  saving.value = true
  try {
    await projectsApi.saveBudgetSummary(projectId, summary.value)
    dlg.value.summary = false
    ElMessage.success('概况已保存')
  } finally { saving.value = false }
}

// ===== 总表 =====
const rollup = ref<any>(null)
const flatRollup = ref<any[]>([])

function flattenRollup(items: any[], level = 0): any[] {
  const result: any[] = []
  for (const item of items) {
    const { children, ...rest } = item
    result.push({ ...rest, _level: level })
    if (children?.length) {
      result.push(...flattenRollup(children, level + 1))
    }
  }
  return result
}

async function loadRollup() {
  loadingRollup.value = true
  try {
    rollup.value = await projectsApi.getBudgetRollup(projectId)
    flatRollup.value = flattenRollup(rollup.value?.items || [])
  } finally { loadingRollup.value = false }
}

// ===== 人工费 =====
const personnelList = ref<any[]>([])
const fPersonnel = ref<any>({ category: '企业编人员', position: '', employee_name: '',
  base_salary: 0, performance: 0, field_allowance: 0, heat_prevention: 0,
  union_fee: 0, unit_coordination: 0, work_months: 1, field_months: 0, sort_order: 0 })
let _editingPersonnelId = ''

async function loadPersonnel() { personnelList.value = await projectsApi.listBudgetPersonnel(projectId) }
function openPersonnelDialog(row?: any) {
  _editingPersonnelId = row?.id || ''
  fPersonnel.value = row ? { ...row } : { category: '企业编人员', position: '', employee_name: '',
    base_salary: 0, performance: 0, field_allowance: 0, heat_prevention: 0,
    union_fee: 0, unit_coordination: 0, work_months: 1, field_months: 0, sort_order: 0 }
  dlg.value.personnel = true
}
async function savePersonnel() {
  saving.value = true
  try {
    if (_editingPersonnelId) {
      await projectsApi.updateBudgetPersonnel(projectId, _editingPersonnelId, fPersonnel.value)
    } else {
      await projectsApi.createBudgetPersonnel(projectId, fPersonnel.value)
    }
    dlg.value.personnel = false
    loadPersonnel()
    ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deletePersonnel(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetPersonnel(projectId, id)
  loadPersonnel()
}

const pSum = computed(() => {
  const list = personnelList.value
  const fields = ['work_months', 'field_months', 'salary_subtotal', 'welfare_subtotal', 'coordination_subtotal', 'union_subtotal', 'total']
  const sums: Record<string, number> = {}
  for (const f of fields) sums[f] = list.reduce((s, row) => s + (Number(row[f]) || 0), 0)
  return sums
})

// ===== 材料费 =====
const materialList = ref<any[]>([])
const fMaterial = ref<any>({ category: '原材料', name: '', model: '', unit: '', unit_price: 0, quantity: 0, remark: '' })
let _editingMatId = ''
async function loadMaterial() { materialList.value = await projectsApi.listBudgetMaterial(projectId) }
function openMatDialog(row?: any) {
  _editingMatId = row?.id || ''
  fMaterial.value = row ? { ...row } : { category: '原材料', name: '', model: '', unit: '', unit_price: 0, quantity: 0, remark: '' }
  dlg.value.material = true
}
async function saveMaterial() {
  saving.value = true
  try {
    fMaterial.value.amount = fMaterial.value.unit_price * fMaterial.value.quantity
    if (_editingMatId) {
      await projectsApi.updateBudgetMaterial(projectId, _editingMatId, fMaterial.value)
    } else {
      await projectsApi.createBudgetMaterial(projectId, fMaterial.value)
    }
    dlg.value.material = false; loadMaterial(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteMaterial(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetMaterial(projectId, id); loadMaterial()
}

// ===== 机械费 =====
const equipList = ref<any[]>([])
const fEquipment = ref<any>({ classification: '', content: '', counterparty: '', model: '', unit_price: 0, quantity: 1 })
let _editingEquipId = ''
async function loadEquipment() { equipList.value = await projectsApi.listBudgetEquipment(projectId) }
function openEquipDialog(row?: any) {
  _editingEquipId = row?.id || ''
  fEquipment.value = row ? { ...row } : { classification: '', content: '', counterparty: '', model: '', unit_price: 0, quantity: 1 }
  dlg.value.equipment = true
}
async function saveEquipment() {
  saving.value = true
  try {
    fEquipment.value.amount = fEquipment.value.unit_price * fEquipment.value.quantity
    if (_editingEquipId) {
      await projectsApi.updateBudgetEquipment(projectId, _editingEquipId, fEquipment.value)
    } else {
      await projectsApi.createBudgetEquipment(projectId, fEquipment.value)
    }
    dlg.value.equipment = false; loadEquipment(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteEquipment(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetEquipment(projectId, id); loadEquipment()
}

// ===== 其他直接费 =====
const dcList = ref<any[]>([])
const fDC = ref<any>({ category: '运输费', content: '', unit: '', unit_price: 0, quantity: 0, remark: '' })
let _editingDCId = ''
async function loadDC() { dcList.value = await projectsApi.listBudgetDirectCost(projectId) }
function openDCDialog(row?: any) {
  _editingDCId = row?.id || ''
  fDC.value = row ? { ...row } : { category: '运输费', content: '', unit: '', unit_price: 0, quantity: 0, remark: '' }
  dlg.value.dc = true
}
async function saveDC() {
  saving.value = true
  try {
    fDC.value.amount = fDC.value.unit_price * fDC.value.quantity
    if (_editingDCId) {
      await projectsApi.updateBudgetDirectCost(projectId, _editingDCId, fDC.value)
    } else {
      await projectsApi.createBudgetDirectCost(projectId, fDC.value)
    }
    dlg.value.dc = false; loadDC(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteDC(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetDirectCost(projectId, id); loadDC()
}

// ===== 劳务费 =====
const laborList = ref<any[]>([])
const fLabor = ref<any>({ category: '临时聘用人员', position: '', employee_name: '', unit: '', quantity: 0, unit_price: 0, remark: '' })
let _editingLaborId = ''
async function loadLabor() { laborList.value = await projectsApi.listBudgetLabor(projectId) }
function openLaborDialog(row?: any) {
  _editingLaborId = row?.id || ''
  fLabor.value = row ? { ...row } : { category: '临时聘用人员', position: '', employee_name: '', unit: '', quantity: 0, unit_price: 0, remark: '' }
  dlg.value.labor = true
}
async function saveLabor() {
  saving.value = true
  try {
    fLabor.value.amount = fLabor.value.unit_price * fLabor.value.quantity
    if (_editingLaborId) {
      await projectsApi.updateBudgetLabor(projectId, _editingLaborId, fLabor.value)
    } else {
      await projectsApi.createBudgetLabor(projectId, fLabor.value)
    }
    dlg.value.labor = false; loadLabor(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteLabor(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetLabor(projectId, id); loadLabor()
}

// ===== 分包 =====
const subList = ref<any[]>([])
const fSub = ref<any>({ category: '工程分包费', item_name: '', counterparty: '', workload: 1, unit_price: 0, remark: '' })
let _editingSubId = ''
async function loadSub() { subList.value = await projectsApi.listBudgetSubcontract(projectId) }
function openSubDialog(row?: any) {
  _editingSubId = row?.id || ''
  fSub.value = row ? { ...row } : { category: '工程分包费', item_name: '', counterparty: '', workload: 1, unit_price: 0, remark: '' }
  dlg.value.subcontract = true
}
async function saveSub() {
  saving.value = true
  try {
    fSub.value.amount = fSub.value.unit_price * fSub.value.workload
    if (_editingSubId) {
      await projectsApi.updateBudgetSubcontract(projectId, _editingSubId, fSub.value)
    } else {
      await projectsApi.createBudgetSubcontract(projectId, fSub.value)
    }
    dlg.value.subcontract = false; loadSub(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteSub(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetSubcontract(projectId, id); loadSub()
}

// ===== 研发+其他 =====
const rdOtherList = ref<any[]>([])
const fRDOther = ref<any>({ cost_group: '研发费用', item: '', unit: '', base_price: 0, quantity: 0, remark: '' })
let _editingRDOtherId = ''
async function loadRDOther() { rdOtherList.value = await projectsApi.listBudgetRDOther(projectId) }
function openRDOtherDialog(row?: any) {
  _editingRDOtherId = row?.id || ''
  fRDOther.value = row ? { ...row } : { cost_group: '研发费用', item: '', unit: '', base_price: 0, quantity: 0, remark: '' }
  dlg.value.rdother = true
}
async function saveRDOther() {
  saving.value = true
  try {
    fRDOther.value.amount = fRDOther.value.base_price * fRDOther.value.quantity
    if (_editingRDOtherId) {
      await projectsApi.updateBudgetRDOther(projectId, _editingRDOtherId, fRDOther.value)
    } else {
      await projectsApi.createBudgetRDOther(projectId, fRDOther.value)
    }
    dlg.value.rdother = false; loadRDOther(); ElMessage.success('已保存')
  } finally { saving.value = false }
}
async function deleteRDOther(id: string) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await projectsApi.deleteBudgetRDOther(projectId, id); loadRDOther()
}

// ===== 对话框状态 =====
const dlg = ref({
  summary: false,
  personnel: false, material: false, equipment: false,
  dc: false, labor: false, subcontract: false, rdother: false,
})

// ===== 导出 =====
async function exportExcel() {
  exporting.value = true
  try {
    const token = authStore.token
    const url = projectsApi.getBudgetExportUrl(projectId)
    const resp = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    if (!resp.ok) {
      const text = await resp.text().catch(() => '')
      throw new Error(text || '导出失败')
    }
    const blob = await resp.blob()
    const fileName = `${project.value?.name || '项目'}预算表.xlsx`
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    setTimeout(() => URL.revokeObjectURL(a.href), 1000)
  } catch (e: any) {
    ElMessage.error(e.message || '导出失败')
  } finally {
    exporting.value = false
  }
}

// Tab 切换加载数据
function onTabChange(name: string) {
  const loaders: Record<string, () => void> = {
    rollup: loadRollup,
    personnel: loadPersonnel,
    mat_equip: () => { loadMaterial(); loadEquipment() },
    others: () => { loadDC(); loadLabor(); loadSub(); loadRDOther() },
  }
  loaders[name]?.()
}

onMounted(async () => {
  project.value = await projectsApi.get(projectId)
  loadSummary()
})
</script>

<style scoped>
.row-actions { display: flex; align-items: center; gap: 0; white-space: nowrap; }
.page h2 { font-size: 20px; }
.page-header { display: flex; justify-content: space-between; align-items: center; }
.page-header > div:first-child { display: flex; align-items: center; gap: 8px; }
.stat-card { background: #fff; border: 1px solid #e4e7ed; border-radius: 6px; padding: 14px 16px; }
.stat-label { font-size: 12px; color: #909399; margin-bottom: 6px; }
.stat-val { font-size: 22px; font-weight: 700; color: #303133; }
.auto-hint { font-size: 11px; color: #909399; margin-left: 4px; white-space: nowrap; }
.profit-positive .stat-val { color: #67c23a; }
.profit-negative .stat-val { color: #f56c6c; }

.overview-table h3 {
  font-size: 14px;
  color: #303133;
  margin: 16px 0 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e4e7ed;
}
.overview-table h3:first-child { margin-top: 0; }
.info-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.info-table td { padding: 6px 10px; border: 1px solid #dcdfe6; vertical-align: middle; }
.info-table td.label { background: #f5f7fa; color: #606266; font-weight: 600; width: 100px; white-space: nowrap; }
.info-text { padding: 8px 12px; min-height: 36px; background: #fafafa; border: 1px solid #ebeef5; border-radius: 4px; font-size: 13px; color: #303133; white-space: pre-wrap; margin-bottom: 4px; }

.table-summary {
  display: flex;
  border: 1px solid #ebeef5;
  border-top: 2px solid #ebeef5;
  background: #f5f7fa;
  font-weight: 700;
  font-size: 12px;
}
.sum-cell {
  padding: 8px 6px;
  border-right: 1px solid #ebeef5;
  box-sizing: border-box;
  flex-shrink: 0;
}
.sum-cell:last-child { border-right: none; }
.sum-cell.right { text-align: right; }
.w100 { width: 100px; }
.w70 { width: 70px; }
.w110 { width: 110px; }
.w120 { width: 120px; }
.w130 { width: 130px; }
</style>
