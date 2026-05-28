from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.identity import normalize_identity
from app.models import Project, Contract, Subcontract, BudgetItem, ConstructionTask, Employee, User, DailyExecution, ExecutionDetail, FinancialEvent
from app.models.budget_v2 import (
    BudgetSummary, BudgetPersonnel, BudgetMaterial,
    BudgetEquipment, BudgetDirectCost, BudgetLabor,
    BudgetSubcontract, BudgetRDOther,
)
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.contract import ContractCreate, ContractResponse
from app.schemas.subcontract import SubcontractCreate, SubcontractResponse
from app.schemas.budget import BudgetItemCreate, BudgetItemUpdate, BudgetItemResponse
from app.schemas.construction_task import ConstructionTaskCreate, ConstructionTaskResponse
from app.schemas.financial_event import FinancialEventCreate, FinancialEventUpdate, FinancialEventResponse

router = APIRouter(prefix="/api/projects", tags=["项目管理"])


def generate_project_code(projects: list[Project]) -> str:
    year = str(date.today().year)
    codes = [p.project_code for p in projects if p.project_code.startswith(f"DX{year}")]
    if codes:
        max_num = max(int(c[7:]) for c in codes if c[7:].isdigit())
        return f"DX{year}{max_num + 1:03d}"
    return f"DX{year}001"


# ========== 项目 CRUD ==========

@router.get("", response_model=dict)
async def list_projects(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None), keyword: str | None = Query(None),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    query = select(Project).options(joinedload(Project.manager))
    count_query = select(func.count(Project.id))
    if normalize_identity(current_user.role) == "项目经理" and current_user.employee_id:
        query = query.where(Project.manager_id == current_user.employee_id)
        count_query = count_query.where(Project.manager_id == current_user.employee_id)
    if status:
        query = query.where(Project.status == status); count_query = count_query.where(Project.status == status)
    if keyword:
        query = query.where(Project.name.contains(keyword)); count_query = count_query.where(Project.name.contains(keyword))

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    projects = (await db.execute(query)).scalars().all()

    items = [
        ProjectResponse(id=p.id, project_code=p.project_code, name=p.name,
            region_province=p.region_province, region_city=p.region_city,
            party_a=p.party_a, party_b=p.party_b, contact_person=p.contact_person,
            contact_phone=p.contact_phone, fund_source=p.fund_source,
            project_nature=p.project_nature, status=p.status, manager_id=p.manager_id,
            manager_name=p.manager.name if p.manager else None,
            remark=p.remark, created_at=p.created_at, updated_at=p.updated_at)
        for p in projects
    ]
    return {"total": total, "items": items}


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    project_data = data.model_dump()
    role = normalize_identity(current_user.role)
    # 非院长/副院长强制将项目经理设为自己
    if role not in ("院长", "副院长"):
        project_data["manager_id"] = current_user.employee_id
    code = project_data.pop("project_code", None)
    if not code:
        result = await db.execute(select(Project))
        code = generate_project_code(list(result.scalars().all()))
    project = Project(project_code=code, **project_data)
    db.add(project); await db.commit(); await db.refresh(project)
    result = await db.execute(select(Project).options(joinedload(Project.manager)).where(Project.id == project.id))
    p = result.scalar_one()
    return ProjectResponse(id=p.id, project_code=p.project_code, name=p.name,
        region_province=p.region_province, region_city=p.region_city,
        party_a=p.party_a, party_b=p.party_b, contact_person=p.contact_person,
        contact_phone=p.contact_phone, fund_source=p.fund_source,
        project_nature=p.project_nature, status=p.status, manager_id=p.manager_id,
        manager_name=p.manager.name if p.manager else None,
        remark=p.remark, created_at=p.created_at, updated_at=p.updated_at)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Project).options(joinedload(Project.manager)).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404, detail="项目不存在")
    return ProjectResponse(id=p.id, project_code=p.project_code, name=p.name,
        region_province=p.region_province, region_city=p.region_city,
        party_a=p.party_a, party_b=p.party_b, contact_person=p.contact_person,
        contact_phone=p.contact_phone, fund_source=p.fund_source,
        project_nature=p.project_nature, status=p.status, manager_id=p.manager_id,
        manager_name=p.manager.name if p.manager else None,
        remark=p.remark, created_at=p.created_at, updated_at=p.updated_at)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p: raise HTTPException(status_code=404, detail="项目不存在")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(p, k, v)
    await db.commit(); await db.refresh(p)
    result = await db.execute(select(Project).options(joinedload(Project.manager)).where(Project.id == p.id))
    p = result.scalar_one()
    return ProjectResponse(id=p.id, project_code=p.project_code, name=p.name,
        region_province=p.region_province, region_city=p.region_city,
        party_a=p.party_a, party_b=p.party_b, contact_person=p.contact_person,
        contact_phone=p.contact_phone, fund_source=p.fund_source,
        project_nature=p.project_nature, status=p.status, manager_id=p.manager_id,
        manager_name=p.manager.name if p.manager else None,
        remark=p.remark, created_at=p.created_at, updated_at=p.updated_at)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    """院长删除项目（级联删除关联数据）"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 先查所有执行单 ID，删除其明细
    exec_ids = (await db.execute(select(DailyExecution.id).where(DailyExecution.project_id == project_id))).scalars().all()
    if exec_ids:
        await db.execute(delete(ExecutionDetail).where(ExecutionDetail.execution_id.in_(exec_ids)))

    await db.execute(delete(FinancialEvent).where(FinancialEvent.project_id == project_id))
    await db.execute(delete(DailyExecution).where(DailyExecution.project_id == project_id))
    await db.execute(delete(ConstructionTask).where(ConstructionTask.project_id == project_id))
    await db.execute(delete(BudgetItem).where(BudgetItem.project_id == project_id))
    await db.execute(delete(Subcontract).where(Subcontract.project_id == project_id))
    await db.execute(delete(Contract).where(Contract.project_id == project_id))

    # 预算 v2 表
    for model in [BudgetPersonnel, BudgetMaterial, BudgetEquipment, BudgetDirectCost,
                  BudgetLabor, BudgetSubcontract, BudgetRDOther]:
        await db.execute(delete(model).where(model.project_id == project_id))
    await db.execute(delete(BudgetSummary).where(BudgetSummary.project_id == project_id))

    await db.delete(p)
    await db.commit()
    return {"message": "项目已删除"}


# ========== 合同 ==========

@router.get("/{project_id}/contract", response_model=ContractResponse)
async def get_contract(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Contract).where(Contract.project_id == project_id))
    c = result.scalar_one_or_none()
    if not c: raise HTTPException(status_code=404, detail="合同未录入")
    return c


@router.post("/{project_id}/contract", response_model=ContractResponse)
async def save_contract(project_id: str, data: ContractCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(Contract).where(Contract.project_id == project_id))
    c = result.scalar_one_or_none()
    actual = data.contract_amount * data.discount_rate
    if c:
        for k, v in data.model_dump().items(): setattr(c, k, v)
        c.actual_amount = actual
    else:
        c = Contract(project_id=project_id, actual_amount=actual, **data.model_dump())
        db.add(c)
    await db.commit(); await db.refresh(c)
    return c


# ========== 分包 ==========

@router.get("/{project_id}/subcontracts", response_model=list[SubcontractResponse])
async def list_subcontracts(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Subcontract).where(Subcontract.project_id == project_id))
    return result.scalars().all()


@router.post("/{project_id}/subcontracts", response_model=SubcontractResponse, status_code=status.HTTP_201_CREATED)
async def create_subcontract(project_id: str, data: SubcontractCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    sub = Subcontract(project_id=project_id, **data.model_dump())
    db.add(sub); await db.commit(); await db.refresh(sub)
    return sub


@router.delete("/{project_id}/subcontracts/{sub_id}")
async def delete_subcontract(project_id: str, sub_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(Subcontract).where(Subcontract.id == sub_id, Subcontract.project_id == project_id))
    sub = result.scalar_one_or_none()
    if not sub: raise HTTPException(status_code=404, detail="分包记录不存在")
    await db.delete(sub); await db.commit()
    return {"message": "删除成功"}


# ========== 预算（费用科目） ==========

@router.get("/{project_id}/budget", response_model=list[BudgetItemResponse])
async def list_budget_items(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(BudgetItem).where(BudgetItem.project_id == project_id).order_by(BudgetItem.sort_order))
    return result.scalars().all()


@router.post("/{project_id}/budget", response_model=BudgetItemResponse, status_code=status.HTTP_201_CREATED)
async def create_budget_item(project_id: str, data: BudgetItemCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    vals = data.model_dump()
    if vals.get("is_personnel"):
        vals["amount"] = vals.get("work_days", 0) * vals.get("unit_price", 0)
    item = BudgetItem(project_id=project_id, **vals)
    db.add(item); await db.commit(); await db.refresh(item)
    return item


@router.put("/{project_id}/budget/{item_id}", response_model=BudgetItemResponse)
async def update_budget_item(project_id: str, item_id: str, data: BudgetItemUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(BudgetItem).where(BudgetItem.id == item_id, BudgetItem.project_id == project_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="预算科目不存在")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(item, k, v)
    if item.is_personnel:
        item.amount = (item.work_days or 0) * (item.unit_price or 0)
    await db.commit(); await db.refresh(item)
    return item


@router.delete("/{project_id}/budget/{item_id}")
async def delete_budget_item(project_id: str, item_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(BudgetItem).where(BudgetItem.id == item_id, BudgetItem.project_id == project_id))
    item = result.scalar_one_or_none()
    if not item: raise HTTPException(status_code=404, detail="预算科目不存在")
    await db.delete(item); await db.commit()
    return {"message": "删除成功"}


# ========== 施工横道图 ==========

@router.get("/{project_id}/tasks", response_model=list[ConstructionTaskResponse])
async def list_tasks(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ConstructionTask).where(ConstructionTask.project_id == project_id).order_by(ConstructionTask.sort_order))
    return result.scalars().all()


@router.post("/{project_id}/tasks", response_model=ConstructionTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: str, data: ConstructionTaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    task = ConstructionTask(project_id=project_id, **data.model_dump())
    db.add(task); await db.commit(); await db.refresh(task)
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=ConstructionTaskResponse)
async def update_task(project_id: str, task_id: str, data: ConstructionTaskCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    result = await db.execute(select(ConstructionTask).where(ConstructionTask.id == task_id, ConstructionTask.project_id == project_id))
    task = result.scalar_one_or_none()
    if not task: raise HTTPException(status_code=404, detail="任务不存在")
    for k, v in data.model_dump().items(): setattr(task, k, v)
    await db.commit(); await db.refresh(task)
    return task


@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(project_id: str, task_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager"))):
    await db.execute(delete(ConstructionTask).where(ConstructionTask.id == task_id, ConstructionTask.project_id == project_id))
    await db.commit()
    return {"message": "删除成功"}


@router.get("/{project_id}/finance")
async def project_finance(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """项目财务汇总"""
    # 预算总额
    budget_result = await db.execute(
        select(func.sum(BudgetItem.amount)).where(BudgetItem.project_id == project_id, BudgetItem.is_personnel == False)
    )
    budget_non_personnel = budget_result.scalar() or 0

    personnel_result = await db.execute(
        select(func.sum(BudgetItem.work_days * BudgetItem.unit_price)).where(
            BudgetItem.project_id == project_id, BudgetItem.is_personnel == True
        )
    )
    budget_personnel = personnel_result.scalar() or 0
    total_budget = budget_non_personnel + budget_personnel

    # 执行汇总（成本）
    exec_result = await db.execute(
        select(
            func.count(DailyExecution.id),
            func.sum(DailyExecution.daily_cost),
        ).where(DailyExecution.project_id == project_id)
    )
    row = exec_result.one()
    exec_count = row[0] or 0
    total_cost = row[1] or 0

    # 财务事件汇总
    fin_result = await db.execute(
        select(
            func.sum(FinancialEvent.amount).filter(FinancialEvent.event_type == "开票"),
            func.sum(FinancialEvent.amount).filter(FinancialEvent.event_type == "产值"),
            func.sum(FinancialEvent.amount).filter(FinancialEvent.event_type == "回款"),
        ).where(FinancialEvent.project_id == project_id)
    )
    fin_row = fin_result.one()
    total_invoice = fin_row[0] or 0
    total_output = fin_row[1] or 0
    total_received = fin_row[2] or 0

    receivable = total_invoice - total_received
    profit = total_received - total_cost if total_received > 0 else 0
    profit_rate = round(profit / total_received * 100, 1) if total_received > 0 else 0

    # 预算科目明细
    budget_items_result = await db.execute(
        select(BudgetItem).where(BudgetItem.project_id == project_id).order_by(BudgetItem.sort_order)
    )
    budget_items = budget_items_result.scalars().all()
    budget_detail = []
    for item in budget_items:
        item_total = item.work_days * item.unit_price if item.is_personnel else item.amount
        budget_detail.append({
            "category": item.category,
            "sub_category": item.sub_category,
            "amount": item_total,
            "is_personnel": item.is_personnel,
        })

    return {
        "total_budget": round(total_budget, 2),
        "budget_personnel": round(budget_personnel, 2),
        "budget_non_personnel": round(budget_non_personnel, 2),
        "exec_count": exec_count,
        "total_cost": round(total_cost, 2),
        "total_output": round(total_output, 2),
        "total_invoice": round(total_invoice, 2),
        "total_received": round(total_received, 2),
        "receivable": round(receivable, 2),
        "profit": round(profit, 2),
        "profit_rate": profit_rate,
        "budget_detail": budget_detail,
    }


# ========== 财务事件 ==========

@router.get("/{project_id}/financial-events", response_model=list[FinancialEventResponse])
async def list_financial_events(project_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(FinancialEvent).where(FinancialEvent.project_id == project_id).order_by(FinancialEvent.event_date.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/financial-events", response_model=FinancialEventResponse, status_code=status.HTTP_201_CREATED)
async def create_financial_event(project_id: str, data: FinancialEventCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager", "finance"))):
    event = FinancialEvent(project_id=project_id, **data.model_dump())
    db.add(event); await db.commit(); await db.refresh(event)
    return event


@router.put("/{project_id}/financial-events/{event_id}", response_model=FinancialEventResponse)
async def update_financial_event(project_id: str, event_id: str, data: FinancialEventUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager", "finance"))):
    result = await db.execute(select(FinancialEvent).where(FinancialEvent.id == event_id, FinancialEvent.project_id == project_id))
    event = result.scalar_one_or_none()
    if not event: raise HTTPException(status_code=404, detail="记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(event, k, v)
    await db.commit(); await db.refresh(event)
    return event


@router.delete("/{project_id}/financial-events/{event_id}")
async def delete_financial_event(project_id: str, event_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director", "manager", "finance"))):
    await db.execute(delete(FinancialEvent).where(FinancialEvent.id == event_id, FinancialEvent.project_id == project_id))
    await db.commit()
    return {"message": "删除成功"}
