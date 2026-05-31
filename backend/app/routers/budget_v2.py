"""测绘预算 V2 — API 路由"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import User, Project
from app.models.contract import Contract
from app.models.budget_v2 import (
    BudgetSummary, BudgetPersonnel, BudgetMaterial,
    BudgetEquipment, BudgetDirectCost, BudgetLabor,
    BudgetSubcontract, BudgetRDOther,
)
from sqlalchemy.orm import selectinload
from app.schemas.budget_v2 import (
    BudgetSummaryCreate, BudgetSummaryResponse,
    BudgetPersonnelCreate, BudgetPersonnelResponse,
    BudgetMaterialCreate, BudgetMaterialResponse,
    BudgetEquipmentCreate, BudgetEquipmentResponse,
    BudgetDirectCostCreate, BudgetDirectCostResponse,
    BudgetLaborCreate, BudgetLaborResponse,
    BudgetSubcontractCreate, BudgetSubcontractResponse,
    BudgetRDOtherCreate, BudgetRDOtherResponse,
    BudgetRollupResponse, BudgetRollupItem,
)

router = APIRouter(prefix="/api/projects", tags=["预算V2"])

# ============================================================
# 辅助函数：为每个子表生成 CRUD 端点
# ============================================================

def make_crud(entity_name: str, model_class, create_schema, response_schema):
    """为给定模型生成 CRUD 端点"""

    @router.get(f"/{{project_id}}/budget/{entity_name}", response_model=list[response_schema])
    async def list_items(
        project_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        result = await db.execute(
            select(model_class).where(model_class.project_id == project_id).order_by(model_class.sort_order)
        )
        return result.scalars().all()

    @router.post(f"/{{project_id}}/budget/{entity_name}", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(
        project_id: str, data: create_schema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_role("director", "manager")),
    ):
        vals = data.model_dump()
        # 自动计算（匹配 DX20260411测绘预算.xlsx 公式）
        if entity_name == "personnel":
            wm = vals.get("work_months", 0) or 0
            fm = vals.get("field_months", 0) or 0
            vals["salary_subtotal"] = round((vals.get("base_salary", 0) + vals.get("performance", 0)) * wm + vals.get("field_allowance", 0) * fm, 2)
            vals["welfare_subtotal"] = round(vals.get("heat_prevention", 0) * wm, 2)
            vals["coordination_subtotal"] = round(vals.get("unit_coordination", 0) * wm, 2)
            vals["union_subtotal"] = round(vals.get("union_fee", 0) * wm, 2)
            vals["total"] = round(vals["salary_subtotal"] + vals["welfare_subtotal"] + vals["coordination_subtotal"] + vals["union_subtotal"], 2)
        elif entity_name in ("material", "direct_cost", "labor", "equipment"):
            vals["amount"] = round(vals.get("unit_price", 0) * vals.get("quantity", 0), 2)
        elif entity_name == "subcontract":
            vals["amount"] = round(vals.get("unit_price", 0) * vals.get("workload", 0), 2)
        elif entity_name == "rd_other":
            vals["amount"] = round(vals.get("base_price", 0) * vals.get("quantity", 0), 2)

        item = model_class(project_id=project_id, **vals)
        db.add(item); await db.commit(); await db.refresh(item)
        return item

    @router.put(f"/{{project_id}}/budget/{entity_name}/{{item_id}}", response_model=response_schema)
    async def update_item(
        project_id: str, item_id: str, data: create_schema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_role("director", "manager")),
    ):
        result = await db.execute(
            select(model_class).where(model_class.id == item_id, model_class.project_id == project_id)
        )
        item = result.scalar_one_or_none()
        if not item: raise HTTPException(status_code=404, detail="记录不存在")

        vals = data.model_dump()
        # 自动计算（匹配 DX20260411测绘预算.xlsx 公式）
        if entity_name == "personnel":
            wm = vals.get("work_months", 0) or 0
            fm = vals.get("field_months", 0) or 0
            vals["salary_subtotal"] = round((vals.get("base_salary", 0) + vals.get("performance", 0)) * wm + vals.get("field_allowance", 0) * fm, 2)
            vals["welfare_subtotal"] = round(vals.get("heat_prevention", 0) * wm, 2)
            vals["coordination_subtotal"] = round(vals.get("unit_coordination", 0) * wm, 2)
            vals["union_subtotal"] = round(vals.get("union_fee", 0) * wm, 2)
            vals["total"] = round(vals["salary_subtotal"] + vals["welfare_subtotal"] + vals["coordination_subtotal"] + vals["union_subtotal"], 2)
        elif entity_name in ("material", "direct_cost", "labor", "equipment"):
            vals["amount"] = round(vals.get("unit_price", 0) * vals.get("quantity", 0), 2)
        elif entity_name == "subcontract":
            vals["amount"] = round(vals.get("unit_price", 0) * vals.get("workload", 0), 2)
        elif entity_name == "rd_other":
            vals["amount"] = round(vals.get("base_price", 0) * vals.get("quantity", 0), 2)

        for k, v in vals.items(): setattr(item, k, v)
        await db.commit(); await db.refresh(item)
        return item

    @router.delete(f"/{{project_id}}/budget/{entity_name}/{{item_id}}")
    async def delete_item(
        project_id: str, item_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_role("director", "manager")),
    ):
        result = await db.execute(
            select(model_class).where(model_class.id == item_id, model_class.project_id == project_id)
        )
        item = result.scalar_one_or_none()
        if not item: raise HTTPException(status_code=404, detail="记录不存在")
        await db.delete(item); await db.commit()
        return {"message": "删除成功"}

    return list_items, create_item, update_item, delete_item


# 为每个子表生成 CRUD
_personnel_crud = make_crud("personnel", BudgetPersonnel, BudgetPersonnelCreate, BudgetPersonnelResponse)
_material_crud = make_crud("material", BudgetMaterial, BudgetMaterialCreate, BudgetMaterialResponse)
_equipment_crud = make_crud("equipment", BudgetEquipment, BudgetEquipmentCreate, BudgetEquipmentResponse)
_direct_cost_crud = make_crud("direct_cost", BudgetDirectCost, BudgetDirectCostCreate, BudgetDirectCostResponse)
_labor_crud = make_crud("labor", BudgetLabor, BudgetLaborCreate, BudgetLaborResponse)
_subcontract_crud = make_crud("subcontract", BudgetSubcontract, BudgetSubcontractCreate, BudgetSubcontractResponse)
_rd_other_crud = make_crud("rd_other", BudgetRDOther, BudgetRDOtherCreate, BudgetRDOtherResponse)


# ============================================================
# 预算概况
# ============================================================

def _project_info(project: Project | None) -> dict:
    """从项目对象提取预算概况中需要展示的项目信息"""
    if not project:
        return {}
    manager_name = project.manager.name if project.manager else None
    return {
        "project_name": project.name,
        "party_a": project.party_a,
        "contact_person": project.contact_person,
        "contact_phone": project.contact_phone,
        "project_manager": manager_name,
    }


def _contract_info(contract: Contract | None) -> dict:
    """从合同对象提取预算概况中需要展示的合同信息"""
    if not contract:
        return {}
    return {
        "contract_no": contract.contract_no,
        "contract_amount": contract.contract_amount,
        "contract_sign_date": str(contract.sign_date) if contract.sign_date else None,
        "drafter": contract.drafter,
        "reviewer": contract.reviewer,
    }


@router.get("/{project_id}/budget/summary")
async def get_budget_summary(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(BudgetSummary).where(BudgetSummary.project_id == project_id)
    )
    summary = result.scalar_one_or_none()
    proj_result = await db.execute(
        select(Project).options(selectinload(Project.manager)).where(Project.id == project_id)
    )
    project = proj_result.scalar_one_or_none()
    contract_result = await db.execute(
        select(Contract).where(Contract.project_id == project_id)
    )
    contract = contract_result.scalar_one_or_none()

    if summary:
        for k, v in _project_info(project).items():
            setattr(summary, k, v)
        for k, v in _contract_info(contract).items():
            setattr(summary, k, v)
        return summary
    if project:
        info = {**_project_info(project), **_contract_info(contract)}
        info["project_id"] = project_id
        return info
    return None


@router.put("/{project_id}/budget/summary", response_model=BudgetSummaryResponse)
async def save_budget_summary(
    project_id: str, data: BudgetSummaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director", "manager")),
):
    proj_result = await db.execute(
        select(Project).options(selectinload(Project.manager)).where(Project.id == project_id)
    )
    project = proj_result.scalar_one_or_none()
    contract_result = await db.execute(
        select(Contract).where(Contract.project_id == project_id)
    )
    contract = contract_result.scalar_one_or_none()
    vals = data.model_dump()
    vals.update(_project_info(project))
    vals.update(_contract_info(contract))

    result = await db.execute(select(BudgetSummary).where(BudgetSummary.project_id == project_id))
    item = result.scalar_one_or_none()
    if item:
        for k, v in vals.items(): setattr(item, k, v)
    else:
        item = BudgetSummary(project_id=project_id, **vals)
        db.add(item)
    await db.commit(); await db.refresh(item)
    return item


# ============================================================
# 总表汇总
# ============================================================

DIRECT_COST_CATEGORIES = [
    ("运输费", "transport_fee"),
    ("装卸费", None),
    ("试验检测费", None),
    ("维修(护)费", None),
    ("办公费", "office_fee"),
    ("出版印刷费", None),
    ("水电费", None),
    ("邮电费", None),
    ("取暖费", None),
    ("交通费", "transport_fee"),
]


@router.get("/{project_id}/budget/rollup", response_model=BudgetRollupResponse)
async def get_budget_rollup(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成总表汇总数据"""
    items = []

    # --- 1.1 人工费 ---
    pers_result = await db.execute(select(BudgetPersonnel).where(BudgetPersonnel.project_id == project_id))
    personnel_list = pers_result.scalars().all()
    # 分四类汇总
    salary_total = sum(p.salary_subtotal for p in personnel_list)
    welfare_total = sum(p.welfare_subtotal for p in personnel_list)
    coord_total = sum(p.coordination_subtotal for p in personnel_list)
    union_total = sum(p.union_subtotal for p in personnel_list)
    personnel_total = salary_total + welfare_total + coord_total + union_total

    pers_children = [
        BudgetRollupItem(level=3, code="⑴", name="职工薪酬", amount=round(salary_total, 2)),
        BudgetRollupItem(level=3, code="⑵", name="职工福利费", amount=round(welfare_total, 2)),
        BudgetRollupItem(level=3, code="⑶", name="单位统筹", amount=round(coord_total, 2)),
        BudgetRollupItem(level=3, code="⑷", name="工会经费", amount=round(union_total, 2)),
    ]
    items.append(BudgetRollupItem(level=2, code="1.1", name="人工费", amount=round(personnel_total, 2), children=pers_children, remark="附明细"))

    # --- 2.1 材料费 ---
    mat_result = await db.execute(select(BudgetMaterial).where(BudgetMaterial.project_id == project_id))
    mat_list = mat_result.scalars().all()
    mat_by_cat = {}
    for m in mat_list:
        cat = m.category or "原材料"
        mat_by_cat[cat] = mat_by_cat.get(cat, 0) + m.amount
    mat_total = sum(mat_by_cat.values())
    mat_children = [
        BudgetRollupItem(level=3, code="⑴", name="原材料", amount=round(mat_by_cat.get("原材料", 0), 2)),
        BudgetRollupItem(level=3, code="⑵", name="专用材料费", amount=round(mat_by_cat.get("专用材料费", 0) + mat_by_cat.get("专用材料", 0), 2)),
        BudgetRollupItem(level=3, code="⑶", name="燃油", amount=round(mat_by_cat.get("燃油", 0) + mat_by_cat.get("燃油费", 0), 2)),
        BudgetRollupItem(level=3, code="⑷", name="技术资料费", amount=round(mat_by_cat.get("技术资料费", 0) + mat_by_cat.get("技术资料", 0), 2)),
    ]
    items.append(BudgetRollupItem(level=2, code="2.1", name="材料费", amount=round(mat_total, 2), children=mat_children))

    # --- 3.1 机械使用费 ---
    equip_result = await db.execute(select(BudgetEquipment).where(BudgetEquipment.project_id == project_id))
    equip_list = equip_result.scalars().all()
    equip_total = sum(e.amount for e in equip_list)
    equip_children = [
        BudgetRollupItem(level=3, code="⑴", name="设备租赁费", amount=round(equip_total, 2)),
    ]
    items.append(BudgetRollupItem(level=2, code="3.1", name="机械使用费", amount=round(equip_total, 2), children=equip_children))

    # --- 4.1 其他直接费 ---
    dc_result = await db.execute(select(BudgetDirectCost).where(BudgetDirectCost.project_id == project_id))
    dc_list = dc_result.scalars().all()
    dc_by_cat = {}
    for d in dc_list:
        dc_by_cat[d.category] = dc_by_cat.get(d.category, 0) + d.amount

    # 劳务费
    labor_result = await db.execute(select(BudgetLabor).where(BudgetLabor.project_id == project_id))
    labor_list = labor_result.scalars().all()
    labor_total = sum(l.amount for l in labor_list)

    # 分包费
    sub_result = await db.execute(select(BudgetSubcontract).where(BudgetSubcontract.project_id == project_id))
    sub_list = sub_result.scalars().all()
    sub_by_cat = {}
    for s in sub_list:
        sub_by_cat[s.category] = sub_by_cat.get(s.category, 0) + s.amount
    sub_total = sum(sub_by_cat.values())

    # 研发费用（4.1.19 和 二 都需要）
    rd_result = await db.execute(
        select(BudgetRDOther).where(BudgetRDOther.project_id == project_id, BudgetRDOther.cost_group == "研发费用")
    )
    rd_list = rd_result.scalars().all()
    rd_total = sum(r.amount for r in rd_list)

    # 其他费用
    other_result = await db.execute(
        select(BudgetRDOther).where(BudgetRDOther.project_id == project_id, BudgetRDOther.cost_group != "研发费用")
    )
    other_list = other_result.scalars().all()
    other_total = sum(o.amount for o in other_list)

    dc_children = [
        BudgetRollupItem(level=3, code="⑴", name="运输费", amount=round(dc_by_cat.get("运输费", 0), 2)),
        BudgetRollupItem(level=3, code="⑵", name="装卸费", amount=round(dc_by_cat.get("装卸费", 0), 2)),
        BudgetRollupItem(level=3, code="⑶", name="检验试验费", amount=round(dc_by_cat.get("试验检测费", 0), 2)),
        BudgetRollupItem(level=3, code="⑷", name="维修（护）费", amount=round(dc_by_cat.get("维修(护)费", 0) + dc_by_cat.get("维修费", 0), 2)),
        BudgetRollupItem(level=3, code="⑸", name="劳务费", amount=round(labor_total, 2)),
        BudgetRollupItem(level=3, code="⑺", name="分包工程款", amount=round(sub_total, 2), remark="附明细", children=[
            BudgetRollupItem(level=4, code="①", name="工程分包费", amount=round(sub_by_cat.get("工程分包费", 0), 2)),
            BudgetRollupItem(level=4, code="②", name="劳务分包费", amount=round(sub_by_cat.get("劳务分包费", 0), 2)),
            BudgetRollupItem(level=4, code="③", name="委托技术服务费", amount=round(sub_by_cat.get("委托技术服务费", 0), 2)),
            BudgetRollupItem(level=4, code="④", name="委托试验费", amount=round(sub_by_cat.get("委托试验费", 0), 2)),
        ]),
        BudgetRollupItem(level=3, code="⑻", name="办公费", amount=round(dc_by_cat.get("办公费", 0), 2)),
        BudgetRollupItem(level=3, code="⑼", name="出版印刷费", amount=round(dc_by_cat.get("出版印刷费", 0), 2)),
        BudgetRollupItem(level=3, code="⑽", name="水电费", amount=round(dc_by_cat.get("水电费", 0), 2), children=[
            BudgetRollupItem(level=4, code="①", name="水费", amount=0),
            BudgetRollupItem(level=4, code="②", name="电费", amount=0),
        ]),
        BudgetRollupItem(level=3, code="⑾", name="邮电费", amount=round(dc_by_cat.get("邮电费", 0), 2), children=[
            BudgetRollupItem(level=4, code="①", name="邮寄费", amount=round(dc_by_cat.get("邮电费", 0), 2)),
            BudgetRollupItem(level=4, code="②", name="电话费", amount=0),
            BudgetRollupItem(level=4, code="③", name="网络费", amount=0),
        ]),
        BudgetRollupItem(level=3, code="⑿", name="取暖费", amount=round(dc_by_cat.get("取暖费", 0), 2)),
        BudgetRollupItem(level=3, code="⒀", name="交通费", amount=round(dc_by_cat.get("交通费", 0), 2), children=[
            BudgetRollupItem(level=4, code="①", name="市内交通费", amount=0),
            BudgetRollupItem(level=4, code="②", name="车辆保险费", amount=0),
            BudgetRollupItem(level=4, code="③", name="燃油费", amount=0),
            BudgetRollupItem(level=4, code="④", name="过路过桥停车费", amount=0),
            BudgetRollupItem(level=4, code="⑤", name="修理费", amount=0),
            BudgetRollupItem(level=4, code="⑥", name="交通工具租用费", amount=0),
            BudgetRollupItem(level=4, code="⑦", name="其他交通费", amount=0),
        ]),
        BudgetRollupItem(level=3, code="⒁", name="差旅费", amount=round(dc_by_cat.get("差旅费", 0), 2)),
        BudgetRollupItem(level=3, code="⒂", name="租赁费", amount=round(dc_by_cat.get("租赁费", 0), 2)),
        BudgetRollupItem(level=3, code="⒃", name="招待费", amount=round(dc_by_cat.get("招待费", 0), 2)),
        BudgetRollupItem(level=3, code="⒄", name="咨询费", amount=round(dc_by_cat.get("咨询费", 0), 2), children=[
            BudgetRollupItem(level=4, code="①", name="咨询费", amount=0),
            BudgetRollupItem(level=4, code="②", name="评审费", amount=0),
            BudgetRollupItem(level=4, code="③", name="翻译费", amount=0),
            BudgetRollupItem(level=4, code="④", name="其他中介费用支出", amount=0),
        ]),
        BudgetRollupItem(level=3, code="⒅", name="劳动保护费", amount=round(dc_by_cat.get("劳动保护费", 0), 2)),
        BudgetRollupItem(level=3, code="⒆", name="其他直接费", amount=round(rd_total + other_total, 2), children=[
            BudgetRollupItem(level=4, code="①", name="研发费用", amount=round(rd_total, 2)),
            BudgetRollupItem(level=4, code="②", name="其他费用", amount=round(other_total, 2)),
        ]),
    ]
    dc_total = sum(c.amount for c in dc_children)
    items.append(BudgetRollupItem(level=2, code="4.1", name="其他直接费", amount=round(dc_total, 2), children=dc_children, remark="附明细"))

    # --- 工程施工总计 ---
    construction_total = personnel_total + mat_total + equip_total + dc_total

    # 税务计算
    sum_result = await db.execute(select(BudgetSummary).where(BudgetSummary.project_id == project_id))
    summary = sum_result.scalar_one_or_none()
    tax_rate = summary.tax_rate if summary else 0
    contract_amount = summary.contract_amount if summary else 0
    han_shui = contract_amount
    xiao_xiang = round(han_shui / (1 + tax_rate) * tax_rate, 2) if tax_rate > 0 else 0
    jin_xiang = 0
    ying_jiao = round(xiao_xiang - jin_xiang, 2)
    fu_jia = round(ying_jiao * 0.12, 2)
    gong_cheng_cb = round(construction_total - rd_total + fu_jia, 2)
    shui_hou_sr = round(han_shui / (1 + tax_rate), 2) if tax_rate > 0 else han_shui
    mao_li_run = round(shui_hou_sr - gong_cheng_cb, 2)

    total_items = [
        BudgetRollupItem(level=1, code="一", name="工程施工", amount=round(construction_total, 2), children=items),
        BudgetRollupItem(level=1, code="二", name="公司承担研发费用", amount=round(rd_total, 2)),
        BudgetRollupItem(level=1, code="三", name=f"销项增值税（含税合同额/{1+tax_rate}×{tax_rate}）", amount=xiao_xiang),
        BudgetRollupItem(level=1, code="四", name="可抵扣进项增值税合计", amount=jin_xiang),
        BudgetRollupItem(level=1, code="五", name="应缴税额=（三-四）", amount=ying_jiao),
        BudgetRollupItem(level=1, code="六", name="附加税=五*附加税率", amount=fu_jia),
        BudgetRollupItem(level=1, code="七", name="工程成本费用=（一-二+六）", amount=gong_cheng_cb),
        BudgetRollupItem(level=1, code="八", name="税后收入=含税合同额/（1+税率）", amount=shui_hou_sr),
        BudgetRollupItem(level=1, code="九", name="工程预算毛利润=八-七", amount=mao_li_run),
    ]

    return BudgetRollupResponse(total=round(construction_total, 2), contract_amount=han_shui, tax_rate=tax_rate,
                                xiao_xiang=xiao_xiang, jin_xiang=jin_xiang, ying_jiao=ying_jiao,
                                fu_jia=fu_jia, gong_cheng_cb=gong_cheng_cb, shui_hou_sr=shui_hou_sr, mao_li_run=mao_li_run,
                                items=total_items)


# ============================================================
# Excel 导出
# ============================================================

@router.get("/{project_id}/budget/export")
async def export_budget(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """导出预算 Excel 文件"""
    from app.services.budget_export import export_budget_excel
    from app.models import Project
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    filename = f"{project.name or '项目'}预算表.xlsx"
    encoded_filename = quote(filename)

    output = await export_budget_excel(db, project_id)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )
