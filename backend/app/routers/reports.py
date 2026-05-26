from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.identity import normalize_identity
from app.models import Project, Contract, DailyExecution, ExecutionDetail, Employee, User
from app.models.budget_v2 import (
    BudgetPersonnel, BudgetMaterial, BudgetEquipment,
    BudgetDirectCost, BudgetLabor, BudgetSubcontract, BudgetRDOther,
)

router = APIRouter(prefix="/api", tags=["报表"])


@router.get("/dashboard/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """工作台首页数据"""
    is_manager = normalize_identity(current_user.role) == "项目经理" and current_user.employee_id

    # --- 基础统计 ---
    proj_query = select(func.count(Project.id))
    active_query = select(func.count(Project.id)).where(Project.status == "进行中")
    if is_manager:
        proj_query = proj_query.where(Project.manager_id == current_user.employee_id)
        active_query = active_query.where(Project.manager_id == current_user.employee_id)
    total_projects = (await db.execute(proj_query)).scalar()
    active_projects = (await db.execute(active_query)).scalar()

    total_contract = (await db.execute(select(func.sum(Contract.actual_amount)))).scalar() or 0
    total_cost = (await db.execute(select(func.sum(DailyExecution.daily_cost)))).scalar() or 0
    total_received = (await db.execute(select(func.sum(DailyExecution.received_amount)))).scalar() or 0
    total_employees = (await db.execute(select(func.count(Employee.id)).where(Employee.status == "在职"))).scalar()

    # --- 项目状态分布 ---
    status_query = select(Project.status, func.count(Project.id)).group_by(Project.status)
    if is_manager:
        status_query = status_query.where(Project.manager_id == current_user.employee_id)
    status_rows = (await db.execute(status_query)).all()
    project_statuses = {s: c for s, c in status_rows}

    # --- 预算总额（从新预算表聚合） ---
    budget_total = 0.0
    for model in [BudgetPersonnel, BudgetMaterial, BudgetEquipment,
                  BudgetDirectCost, BudgetLabor, BudgetSubcontract, BudgetRDOther]:
        # 每个模型有不同金额字段，统一处理
        if model is BudgetPersonnel:
            r = await db.execute(select(func.sum(BudgetPersonnel.total)))
        elif model is BudgetRDOther:
            r = await db.execute(select(func.sum(BudgetRDOther.amount)))
        else:
            r = await db.execute(select(func.sum(model.amount)))
        v = r.scalar()
        if v: budget_total += v
    budget_total = round(budget_total, 2)

    # --- 近 6 个月成本趋势 ---
    today = date.today()
    month_cost = 0.0
    monthly_trend = []
    for i in range(5, -1, -1):
        # 计算第 i 个月前的第一天
        y, m = today.year, today.month
        for _ in range(i):
            m -= 1
            if m == 0: m = 12; y -= 1
        ms = date(y, m, 1)
        me = date(y, m + 1, 1) if m < 12 else date(y + 1, 1, 1)
        mc = (await db.execute(
            select(func.sum(DailyExecution.daily_cost))
            .where(DailyExecution.record_date >= ms, DailyExecution.record_date < me)
        )).scalar() or 0
        monthly_trend.append({"month": f"{y}-{m:02d}", "cost": round(mc, 2)})
        if i == 0:
            month_cost = round(mc, 2)

    # --- 最近项目 ---
    recent_proj_query = select(Project).options(selectinload(Project.manager)).order_by(Project.created_at.desc()).limit(5)
    if is_manager:
        recent_proj_query = recent_proj_query.where(Project.manager_id == current_user.employee_id)
    recent_projects_result = (await db.execute(recent_proj_query)).scalars().all()

    # 批量查询所有最近项目的累计成本
    proj_ids = [p.id for p in recent_projects_result]
    proj_cost_map = {}
    if proj_ids:
        cost_rows = (await db.execute(
            select(DailyExecution.project_id, func.sum(DailyExecution.daily_cost))
            .where(DailyExecution.project_id.in_(proj_ids))
            .group_by(DailyExecution.project_id)
        )).all()
        proj_cost_map = {pid: round(c or 0, 2) for pid, c in cost_rows}

    recent_projects = []
    for p in recent_projects_result:
        recent_projects.append({
            "id": p.id, "name": p.name, "status": p.status,
            "manager_name": p.manager.name if p.manager else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "accumulated_cost": proj_cost_map.get(p.id, 0),
        })

    # --- 最近执行单 ---
    exec_query = (
        select(DailyExecution, Project.name)
        .outerjoin(Project, DailyExecution.project_id == Project.id)
        .order_by(DailyExecution.created_at.desc()).limit(8)
    )
    exec_rows = (await db.execute(exec_query)).all()
    recent_executions = []
    for ex, pname in exec_rows:
        recent_executions.append({
            "id": ex.id, "project_name": pname or "-",
            "record_date": ex.record_date.isoformat() if ex.record_date else "",
            "daily_cost": round(ex.daily_cost or 0, 2),
            "seq_number": ex.seq_number,
        })

    return {
        "total_projects": total_projects, "active_projects": active_projects,
        "total_contract": total_contract, "total_cost": total_cost,
        "total_received": total_received, "total_employees": total_employees,
        "month_cost": month_cost, "budget_total": budget_total,
        "project_statuses": project_statuses,
        "monthly_trend": monthly_trend,
        "recent_projects": recent_projects,
        "recent_executions": recent_executions,
    }


@router.get("/reports/personnel")
async def personnel_report(
    employee_id: str | None = Query(None), year: int = Query(2025),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    role = normalize_identity(current_user.role)
    if role not in {"院长", "综合员"}:
        employee_id = current_user.employee_id

    start_date = f"{year}-01-01"; end_date = f"{year}-12-31"
    query = (
        select(ExecutionDetail, DailyExecution, Employee, Project)
        .join(DailyExecution, ExecutionDetail.execution_id == DailyExecution.id)
        .join(Employee, ExecutionDetail.employee_id == Employee.id)
        .outerjoin(Project, DailyExecution.project_id == Project.id)
        .where(DailyExecution.record_date >= start_date)
        .where(DailyExecution.record_date <= end_date)
    )
    if employee_id: query = query.where(ExecutionDetail.employee_id == employee_id)
    result = await db.execute(query)
    rows = result.all()

    stats: dict = {}
    for detail, execution, employee, project in rows:
        eid = employee.id
        if eid not in stats:
            stats[eid] = {
                "employee_id": eid, "employee_name": employee.name,
                "work_type": employee.work_type, "department": employee.department,
                "total_hours": 0, "total_cost": 0, "projects": {},
                "monthly": {m: {"hours": 0, "cost": 0} for m in range(1, 13)},
            }
        s = stats[eid]
        s["total_hours"] += detail.work_hours
        s["total_cost"] += detail.cost
        month = execution.record_date.month
        s["monthly"][month]["hours"] += detail.work_hours
        s["monthly"][month]["cost"] += detail.cost
        if project:
            pname = project.name
            if pname not in s["projects"]:
                s["projects"][pname] = {"hours": 0, "cost": 0}
            s["projects"][pname]["hours"] += detail.work_hours
            s["projects"][pname]["cost"] += detail.cost

    items = []
    for eid, s in stats.items():
        project_list = [{"name": k, "hours": v["hours"], "cost": round(v["cost"], 2)}
                        for k, v in sorted(s["projects"].items(), key=lambda x: x[1]["hours"], reverse=True)]
        monthly_list = [{"month": m, "hours": round(s["monthly"][m]["hours"], 1),
                         "cost": round(s["monthly"][m]["cost"], 2)} for m in range(1, 13)]
        items.append({
            **s, "projects": project_list, "monthly": monthly_list,
            "work_days": round(s["total_hours"] / 8, 1),
        })
    return {"year": year, "items": items}
