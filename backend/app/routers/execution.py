from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import DailyExecution, ExecutionDetail, Employee, Project, User, BudgetItem
from app.models.budget_v2 import (
    BudgetSummary, BudgetPersonnel, BudgetMaterial,
    BudgetEquipment, BudgetDirectCost, BudgetLabor,
    BudgetSubcontract, BudgetRDOther,
)
from app.schemas.execution import (
    DailyExecutionCreate, DailyExecutionResponse,
    ExecutionDetailCreate, ExecutionDetailResponse,
)

router = APIRouter(prefix="/api/executions", tags=["每日执行单"])

# 费用科目字段名与中文标签映射
FEE_FIELDS = [
    ("inhouse_personnel", "事业人员"),
    ("enterprise_personnel", "企业人员"),
    ("dispatched_personnel", "派遣人员"),
    ("subcontract_fee", "分包费"),
    ("relevant_fee", "相关费用"),
    ("material_fee", "材料费"),
    ("labor_fee", "劳务费"),
    ("rental_fee", "租赁费"),
    ("transport_fee", "交通费"),
    ("office_fee", "办公费"),
    ("entertainment_fee", "招待费"),
    ("other_fee", "其他费用"),
    ("travel_fee", "差旅费"),
    ("bidding_fee", "招投标费"),
    ("commission_fee", "提成"),
    ("tax_fee", "税金"),
]


def _compute_personnel_costs(details, db_employees):
    """根据人员明细计算三类人员费用"""
    inhouse = 0.0; enterprise = 0.0; dispatched = 0.0
    for d in details:
        emp = db_employees.get(d.employee_id)
        if not emp: continue
        cost = d.work_hours / 8.0 * emp.daily_wage if emp.daily_wage > 0 else 0
        if emp.personnel_type == "事业人员": inhouse += cost
        elif emp.personnel_type == "企业人员": enterprise += cost
        else: dispatched += cost
    return inhouse, enterprise, dispatched


def _calc_daily_cost(data, inhouse, enterprise, dispatched):
    return (
        data.subcontract_fee + inhouse + enterprise + dispatched +
        data.relevant_fee + data.material_fee + data.labor_fee + data.rental_fee +
        data.transport_fee + data.office_fee + data.entertainment_fee +
        data.other_fee + data.travel_fee + data.bidding_fee + data.commission_fee + data.tax_fee
    )


async def _build_budget_map_v2(db, project_id: str) -> dict:
    """从新预算表聚合为 {字段名: 预算金额}"""
    budget = {}

    # 1.1 人工费
    pers_result = await db.execute(
        select(BudgetPersonnel).where(BudgetPersonnel.project_id == project_id)
    )
    personnel_list = pers_result.scalars().all()
    inhouse = 0.0; enterprise = 0.0
    for p in personnel_list:
        t = round(p.total, 2)
        if p.category == "事业编人员":
            inhouse += t
        else:
            enterprise += t
    if inhouse > 0: budget["inhouse_personnel"] = round(inhouse, 2)
    if enterprise > 0: budget["enterprise_personnel"] = round(enterprise, 2)

    # 2.1 材料费
    mat_result = await db.execute(
        select(BudgetMaterial).where(BudgetMaterial.project_id == project_id)
    )
    mat_total = sum(m.amount for m in mat_result.scalars().all())
    if mat_total > 0: budget["material_fee"] = round(mat_total, 2)

    # 3.1 机械使用费 → rental_fee
    equip_result = await db.execute(
        select(BudgetEquipment).where(BudgetEquipment.project_id == project_id)
    )
    equip_total = sum(e.amount for e in equip_result.scalars().all())
    if equip_total > 0: budget["rental_fee"] = budget.get("rental_fee", 0) + round(equip_total, 2)

    # 4.1 其他直接费
    dc_result = await db.execute(
        select(BudgetDirectCost).where(BudgetDirectCost.project_id == project_id)
    )
    dc_map = {
        "运输费": "transport_fee", "装卸费": None, "试验检测费": None,
        "维修(护)费": None, "维修费": None,
        "办公费": "office_fee", "出版印刷费": None, "水电费": None,
        "邮电费": None, "取暖费": None, "交通费": "transport_fee",
    }
    for d in dc_result.scalars().all():
        field = dc_map.get(d.category)
        if field:
            budget[field] = budget.get(field, 0) + round(d.amount, 2)

    # 劳务费 → dispatched_personnel
    labor_result = await db.execute(
        select(BudgetLabor).where(BudgetLabor.project_id == project_id)
    )
    labor_total = sum(l.amount for l in labor_result.scalars().all())
    if labor_total > 0: budget["dispatched_personnel"] = budget.get("dispatched_personnel", 0) + round(labor_total, 2)

    # 分包费 → subcontract_fee
    sub_result = await db.execute(
        select(BudgetSubcontract).where(BudgetSubcontract.project_id == project_id)
    )
    sub_total = sum(s.amount for s in sub_result.scalars().all())
    if sub_total > 0: budget["subcontract_fee"] = budget.get("subcontract_fee", 0) + round(sub_total, 2)

    # 研发+其他 → other_fee
    rd_result = await db.execute(
        select(BudgetRDOther).where(BudgetRDOther.project_id == project_id)
    )
    rd_total = sum(r.amount for r in rd_result.scalars().all())
    if rd_total > 0: budget["other_fee"] = budget.get("other_fee", 0) + round(rd_total, 2)

    return budget


def _build_budget_map(budget_items):
    """将预算科目映射为 {字段名: 预算金额}"""
    budget_map = {}
    category_to_field = {
        "事业人员": "inhouse_personnel", "企业人员": "enterprise_personnel",
        "派遣人员": "dispatched_personnel", "分包费": "subcontract_fee",
        "相关费用": "relevant_fee", "材料费": "material_fee",
        "劳务费": "labor_fee", "租赁费": "rental_fee",
        "交通费": "transport_fee", "办公费": "office_fee",
        "招待费": "entertainment_fee", "其他费用": "other_fee",
        "差旅费": "travel_fee", "招投标费": "bidding_fee",
        "提成": "commission_fee", "税金": "tax_fee",
        "设备费": "rental_fee",  # 设备归入租赁费
    }
    personnel_total = 0.0
    for item in budget_items:
        field = category_to_field.get(item.category)
        if field:
            val = item.work_days * item.unit_price if item.is_personnel else item.amount
            budget_map[field] = budget_map.get(field, 0) + val
        elif item.is_personnel and item.category:
            # 通用"人员费"等：汇总后均分到三类人员
            personnel_total += item.work_days * item.unit_price
    if personnel_total > 0:
        split = round(personnel_total / 3, 2)
        # 前两列用均分值，最后一列补差避免精度损失
        fields = ("inhouse_personnel", "enterprise_personnel", "dispatched_personnel")
        budget_map[fields[0]] = budget_map.get(fields[0], 0) + split
        budget_map[fields[1]] = budget_map.get(fields[1], 0) + split
        budget_map[fields[2]] = budget_map.get(fields[2], 0) + round(personnel_total - 2 * split, 2)
    return budget_map


@router.get("", response_model=dict)
async def list_executions(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
    project_id: str | None = Query(None),
    start_date: str | None = Query(None), end_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director", "manager")),
):
    """项目经理和院长查看每日执行单流水"""
    query = select(DailyExecution).options(
        joinedload(DailyExecution.project),
        joinedload(DailyExecution.details).joinedload(ExecutionDetail.employee),
    ).where(DailyExecution.project_id == project_id if project_id else True)

    if start_date: query = query.where(DailyExecution.record_date >= start_date)
    if end_date: query = query.where(DailyExecution.record_date <= end_date)

    query = query.order_by(DailyExecution.record_date.asc(), DailyExecution.seq_number.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.unique().scalars().all()
    items = [_execution_to_response(r) for r in records]

    # 计算累计发生额和预算
    accumulated = {}
    budget = {}
    if project_id:
        # 累计发生额：该项目所有执行单的各字段汇总
        acc_result = await db.execute(
            select(
                func.sum(DailyExecution.inhouse_personnel),
                func.sum(DailyExecution.enterprise_personnel),
                func.sum(DailyExecution.dispatched_personnel),
                func.sum(DailyExecution.subcontract_fee),
                func.sum(DailyExecution.relevant_fee),
                func.sum(DailyExecution.material_fee),
                func.sum(DailyExecution.labor_fee),
                func.sum(DailyExecution.rental_fee),
                func.sum(DailyExecution.transport_fee),
                func.sum(DailyExecution.office_fee),
                func.sum(DailyExecution.entertainment_fee),
                func.sum(DailyExecution.other_fee),
                func.sum(DailyExecution.travel_fee),
                func.sum(DailyExecution.bidding_fee),
                func.sum(DailyExecution.commission_fee),
                func.sum(DailyExecution.tax_fee),
                func.sum(DailyExecution.daily_cost),
            ).where(DailyExecution.project_id == project_id)
        )
        row = acc_result.one()
        accumulated = {
            "inhouse_personnel": round(row[0] or 0, 2),
            "enterprise_personnel": round(row[1] or 0, 2),
            "dispatched_personnel": round(row[2] or 0, 2),
            "subcontract_fee": round(row[3] or 0, 2),
            "relevant_fee": round(row[4] or 0, 2),
            "material_fee": round(row[5] or 0, 2),
            "labor_fee": round(row[6] or 0, 2),
            "rental_fee": round(row[7] or 0, 2),
            "transport_fee": round(row[8] or 0, 2),
            "office_fee": round(row[9] or 0, 2),
            "entertainment_fee": round(row[10] or 0, 2),
            "other_fee": round(row[11] or 0, 2),
            "travel_fee": round(row[12] or 0, 2),
            "bidding_fee": round(row[13] or 0, 2),
            "commission_fee": round(row[14] or 0, 2),
            "tax_fee": round(row[15] or 0, 2),
            "daily_cost": round(row[16] or 0, 2),
        }

        # 预算（优先从新表聚合，旧表作为补充）
        budget = await _build_budget_map_v2(db, project_id)
        # 旧 BudgetItem 补充（兼容已有数据）
        budget_result = await db.execute(
            select(BudgetItem).where(BudgetItem.project_id == project_id)
        )
        old_items = budget_result.scalars().all()
        if old_items:
            old_budget = _build_budget_map(old_items)
            for k, v in old_budget.items():
                if k not in budget:
                    budget[k] = v

    return {
        "total": len(items), "items": items,
        "accumulated": accumulated, "budget": budget,
    }


@router.get("/personnel-daily")
async def personnel_daily_work(
    project_id: str | None = Query(None),
    employee_id: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    year: int | None = Query(None),
    month: int | None = Query(None, ge=1, le=12),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director", "manager")),
):
    """返回按人分组的每日工作情况（院长/管理员/项目经理），支持按员工、年月、日期范围筛选"""
    query = (
        select(ExecutionDetail, DailyExecution, Employee, Project.name)
        .join(DailyExecution, ExecutionDetail.execution_id == DailyExecution.id)
        .join(Employee, ExecutionDetail.employee_id == Employee.id)
        .outerjoin(Project, DailyExecution.project_id == Project.id)
    )
    if project_id:
        query = query.where(DailyExecution.project_id == project_id)
    if employee_id:
        query = query.where(ExecutionDetail.employee_id == employee_id)
    if year and month:
        query = query.where(
            DailyExecution.record_date >= f"{year}-{month:02d}-01",
            DailyExecution.record_date < (f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"),
        )
    elif year:
        query = query.where(
            DailyExecution.record_date >= f"{year}-01-01",
            DailyExecution.record_date < f"{year+1}-01-01",
        )
    if start_date:
        query = query.where(DailyExecution.record_date >= start_date)
    if end_date:
        query = query.where(DailyExecution.record_date <= end_date)

    query = query.order_by(DailyExecution.record_date.desc(), Employee.name.asc())
    result = await db.execute(query)
    rows = result.all()

    items = []
    for detail, execution, employee, project_name in rows:
        items.append({
            "id": detail.id,
            "record_date": execution.record_date.isoformat() if execution.record_date else "",
            "employee_name": employee.name,
            "work_type": employee.work_type or "",
            "department": employee.department or "",
            "personnel_type": employee.personnel_type or "",
            "project_name": project_name or "",
            "work_hours": detail.work_hours,
            "work_content": detail.work_content or "",
            "is_leave": detail.is_leave,
            "leave_reason": detail.leave_reason or "",
            "cost": round(detail.cost or 0, 2),
        })

    # 汇总统计
    total_hours = sum(i["work_hours"] for i in items)
    total_cost = sum(i["cost"] for i in items)
    total_days = len(set(i["record_date"] for i in items))

    return {
        "total": len(items), "items": items,
        "total_hours": total_hours, "total_cost": round(total_cost, 2),
        "total_days": total_days,
    }


@router.post("", response_model=DailyExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    data: DailyExecutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("manager")),
):
    """项目经理填写每日执行单"""
    # 预加载员工信息
    emp_ids = [d.employee_id for d in data.details]
    emp_map = {}
    if emp_ids:
        emp_result = await db.execute(select(Employee).where(Employee.id.in_(emp_ids)))
        for e in emp_result.scalars().all():
            emp_map[e.id] = e

    inhouse, enterprise, dispatched = _compute_personnel_costs(data.details, emp_map)
    daily_cost = _calc_daily_cost(data, inhouse, enterprise, dispatched)

    prev_result = await db.execute(
        select(func.sum(DailyExecution.daily_cost)).where(DailyExecution.project_id == data.project_id)
    )
    prev_total = prev_result.scalar() or 0
    cumulative_cost = prev_total + daily_cost

    exec = DailyExecution(
        project_id=data.project_id, record_date=data.record_date,
        seq_number=data.seq_number,
        subcontract_fee=data.subcontract_fee,
        inhouse_personnel=inhouse, enterprise_personnel=enterprise,
        dispatched_personnel=dispatched,
        relevant_fee=data.relevant_fee, material_fee=data.material_fee,
        labor_fee=data.labor_fee, rental_fee=data.rental_fee,
        transport_fee=data.transport_fee, office_fee=data.office_fee,
        entertainment_fee=data.entertainment_fee, other_fee=data.other_fee,
        travel_fee=data.travel_fee, bidding_fee=data.bidding_fee,
        commission_fee=data.commission_fee, tax_fee=data.tax_fee,
        daily_cost=daily_cost, cumulative_cost=cumulative_cost,
        cumulative_profit=0, profit_rate=0,
        remark=data.remark, registrant=data.registrant or (
            current_user.employee.name if current_user.employee else current_user.username
        ),
    )
    db.add(exec)
    await db.flush()

    for d in data.details:
        emp = emp_map.get(d.employee_id)
        rate = emp.daily_wage if emp else 0
        cost = d.work_hours / 8.0 * rate if rate > 0 else 0
        detail = ExecutionDetail(
            execution_id=exec.id, employee_id=d.employee_id,
            work_hours=d.work_hours, daily_rate=rate, cost=cost,
            work_content=d.work_content, is_leave=d.is_leave,
            leave_reason=d.leave_reason,
        )
        db.add(detail)

    await db.commit()

    result = await db.execute(
        select(DailyExecution).options(
            joinedload(DailyExecution.project),
            joinedload(DailyExecution.details).joinedload(ExecutionDetail.employee),
        ).where(DailyExecution.id == exec.id)
    )
    return _execution_to_response(result.unique().scalar_one())


@router.put("/{exec_id}", response_model=DailyExecutionResponse)
async def update_execution(
    exec_id: str, data: DailyExecutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("manager")),
):
    """项目经理编辑执行单"""
    result = await db.execute(
        select(DailyExecution).options(
            joinedload(DailyExecution.details).joinedload(ExecutionDetail.employee),
        ).where(DailyExecution.id == exec_id)
    )
    exec = result.unique().scalar_one_or_none()
    if not exec: raise HTTPException(status_code=404, detail="记录不存在")

    emp_ids = [d.employee_id for d in data.details]
    emp_map = {}
    if emp_ids:
        emp_result = await db.execute(select(Employee).where(Employee.id.in_(emp_ids)))
        for e in emp_result.scalars().all():
            emp_map[e.id] = e

    inhouse, enterprise, dispatched = _compute_personnel_costs(data.details, emp_map)
    daily_cost = _calc_daily_cost(data, inhouse, enterprise, dispatched)

    prev_result = await db.execute(
        select(func.sum(DailyExecution.daily_cost)).where(
            DailyExecution.project_id == exec.project_id,
            DailyExecution.id != exec_id,
        )
    )
    prev_total = prev_result.scalar() or 0
    cumulative_cost = prev_total + daily_cost

    exec.project_id = data.project_id
    exec.record_date = data.record_date
    exec.seq_number = data.seq_number
    exec.subcontract_fee = data.subcontract_fee
    exec.inhouse_personnel = inhouse
    exec.enterprise_personnel = enterprise
    exec.dispatched_personnel = dispatched
    exec.relevant_fee = data.relevant_fee
    exec.material_fee = data.material_fee
    exec.labor_fee = data.labor_fee
    exec.rental_fee = data.rental_fee
    exec.transport_fee = data.transport_fee
    exec.office_fee = data.office_fee
    exec.entertainment_fee = data.entertainment_fee
    exec.other_fee = data.other_fee
    exec.travel_fee = data.travel_fee
    exec.bidding_fee = data.bidding_fee
    exec.commission_fee = data.commission_fee
    exec.tax_fee = data.tax_fee
    exec.daily_cost = daily_cost
    exec.cumulative_cost = cumulative_cost
    exec.remark = data.remark
    exec.registrant = data.registrant or exec.registrant

    await db.execute(delete(ExecutionDetail).where(ExecutionDetail.execution_id == exec_id))
    for d in data.details:
        emp = emp_map.get(d.employee_id)
        rate = emp.daily_wage if emp else 0
        cost = d.work_hours / 8.0 * rate if rate > 0 else 0
        detail = ExecutionDetail(
            execution_id=exec.id, employee_id=d.employee_id,
            work_hours=d.work_hours, daily_rate=rate, cost=cost,
            work_content=d.work_content, is_leave=d.is_leave,
            leave_reason=d.leave_reason,
        )
        db.add(detail)

    await db.commit()

    result = await db.execute(
        select(DailyExecution).options(
            joinedload(DailyExecution.project),
            joinedload(DailyExecution.details).joinedload(ExecutionDetail.employee),
        ).where(DailyExecution.id == exec_id)
    )
    return _execution_to_response(result.unique().scalar_one())


@router.get("/{exec_id}", response_model=DailyExecutionResponse)
async def get_execution(
    exec_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director", "manager")),
):
    result = await db.execute(
        select(DailyExecution).options(
            joinedload(DailyExecution.project),
            joinedload(DailyExecution.details).joinedload(ExecutionDetail.employee),
        ).where(DailyExecution.id == exec_id)
    )
    r = result.unique().scalar_one_or_none()
    if not r: raise HTTPException(status_code=404, detail="记录不存在")
    return _execution_to_response(r)


def _execution_to_response(r: DailyExecution) -> DailyExecutionResponse:
    details = [
        ExecutionDetailResponse(
            id=d.id, employee_id=d.employee_id,
            employee_name=d.employee.name if d.employee else None,
            work_hours=d.work_hours, daily_rate=d.daily_rate, cost=d.cost,
            work_content=d.work_content, is_leave=d.is_leave,
            leave_reason=d.leave_reason,
        )
        for d in r.details
    ]
    return DailyExecutionResponse(
        id=r.id, project_id=r.project_id,
        project_name=r.project.name if r.project else None,
        record_date=r.record_date, seq_number=r.seq_number,
        subcontract_fee=r.subcontract_fee, inhouse_personnel=r.inhouse_personnel,
        enterprise_personnel=r.enterprise_personnel, dispatched_personnel=r.dispatched_personnel,
        relevant_fee=r.relevant_fee, material_fee=r.material_fee,
        labor_fee=r.labor_fee, rental_fee=r.rental_fee,
        transport_fee=r.transport_fee, office_fee=r.office_fee,
        entertainment_fee=r.entertainment_fee, other_fee=r.other_fee,
        travel_fee=r.travel_fee, bidding_fee=r.bidding_fee,
        commission_fee=r.commission_fee, tax_fee=r.tax_fee,
        daily_cost=r.daily_cost, cumulative_cost=r.cumulative_cost,
        cumulative_profit=r.cumulative_profit, profit_rate=r.profit_rate,
        remark=r.remark, status=r.status, registrant=r.registrant,
        reviewer=r.reviewer, details=details, created_at=r.created_at,
    )
