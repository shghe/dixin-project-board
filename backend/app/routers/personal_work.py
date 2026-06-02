from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PersonalWorkEntry, Employee, User, DailyExecution, ExecutionDetail, Project
from app.schemas.personal_work_entry import (
    PersonalWorkEntryCreate,
    PersonalWorkEntryUpdate,
    PersonalWorkEntryResponse,
)

router = APIRouter(prefix="/api/personal-work", tags=["个人工时"])


@router.get("", response_model=list[PersonalWorkEntryResponse])
async def list_entries(
    record_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    employee_id = current_user.employee_id
    query = select(PersonalWorkEntry).options(joinedload(PersonalWorkEntry.employee)).where(
        PersonalWorkEntry.employee_id == employee_id
    )
    if record_date:
        query = query.where(PersonalWorkEntry.record_date == record_date)
    query = query.order_by(PersonalWorkEntry.record_date.desc())
    result = await db.execute(query)
    entries = result.scalars().all()
    return [
        PersonalWorkEntryResponse(
            id=e.id,
            employee_id=e.employee_id,
            employee_name=e.employee.name if e.employee else None,
            record_date=e.record_date,
            work_hours=e.work_hours,
            work_content=e.work_content,
            category=e.category,
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.post("", response_model=PersonalWorkEntryResponse)
async def create_entry(
    data: PersonalWorkEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee_id:
        raise HTTPException(status_code=400, detail="当前用户未关联员工")
    entry = PersonalWorkEntry(employee_id=current_user.employee_id, **data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    result = await db.execute(
        select(PersonalWorkEntry).options(joinedload(PersonalWorkEntry.employee)).where(
            PersonalWorkEntry.id == entry.id
        )
    )
    e = result.scalar_one()
    return PersonalWorkEntryResponse(
        id=e.id,
        employee_id=e.employee_id,
        employee_name=e.employee.name if e.employee else None,
        record_date=e.record_date,
        work_hours=e.work_hours,
        work_content=e.work_content,
        category=e.category,
        created_at=e.created_at,
    )


@router.put("/{entry_id}", response_model=PersonalWorkEntryResponse)
async def update_entry(
    entry_id: str,
    data: PersonalWorkEntryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PersonalWorkEntry).options(joinedload(PersonalWorkEntry.employee)).where(
            PersonalWorkEntry.id == entry_id,
            PersonalWorkEntry.employee_id == current_user.employee_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(entry, k, v)
    await db.commit()
    await db.refresh(entry)
    return PersonalWorkEntryResponse(
        id=entry.id,
        employee_id=entry.employee_id,
        employee_name=entry.employee.name if entry.employee else None,
        record_date=entry.record_date,
        work_hours=entry.work_hours,
        work_content=entry.work_content,
        category=entry.category,
        created_at=entry.created_at,
    )


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PersonalWorkEntry).where(
            PersonalWorkEntry.id == entry_id,
            PersonalWorkEntry.employee_id == current_user.employee_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(entry)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/daily-summary")
async def daily_summary(
    record_date: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询某日该员工的项目工时 + 个人工时汇总"""
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="当前用户未关联员工")

    # 项目工时明细（每条执行单人员明细，含工作内容）
    proj_detail_result = await db.execute(
        select(
            ExecutionDetail.work_hours,
            ExecutionDetail.work_content,
            Project.name,
        )
        .join(DailyExecution, ExecutionDetail.execution_id == DailyExecution.id)
        .join(Project, DailyExecution.project_id == Project.id)
        .where(
            ExecutionDetail.employee_id == employee_id,
            DailyExecution.record_date == record_date,
        )
        .order_by(Project.name)
    )
    proj_rows = proj_detail_result.all()
    project_details = [
        {
            "project_name": name,
            "work_hours": round(float(h or 0), 1),
            "work_content": wc or "",
        }
        for h, wc, name in proj_rows
    ]
    # 按项目汇总
    proj_sum: dict[str, float] = {}
    for p in project_details:
        proj_sum[p["project_name"]] = proj_sum.get(p["project_name"], 0) + p["work_hours"]
    project_breakdown = [
        {"project_name": k, "hours": round(v, 1)} for k, v in proj_sum.items()
    ]
    project_hours = round(float(sum(p["hours"] for p in project_breakdown)), 1)

    # 个人工时（非项目）
    personal_result = await db.execute(
        select(func.sum(PersonalWorkEntry.work_hours)).where(
            PersonalWorkEntry.employee_id == employee_id,
            PersonalWorkEntry.record_date == record_date,
        )
    )
    personal_hours = personal_result.scalar() or 0

    # 个人工时明细
    entries_result = await db.execute(
        select(PersonalWorkEntry)
        .where(
            PersonalWorkEntry.employee_id == employee_id,
            PersonalWorkEntry.record_date == record_date,
        )
        .order_by(PersonalWorkEntry.created_at.desc())
    )
    entries = entries_result.scalars().all()

    return {
        "record_date": record_date,
        "project_hours": project_hours,
        "project_breakdown": project_breakdown,
        "project_details": project_details,
        "personal_hours": round(float(personal_hours), 1),
        "total_hours": round(float(project_hours + personal_hours), 1),
        "remaining": round(float(max(0, 8 - project_hours - personal_hours)), 1),
        "entries": [
            {
                "id": e.id,
                "work_hours": e.work_hours,
                "work_content": e.work_content,
                "category": e.category,
            }
            for e in entries
        ],
    }


@router.get("/monthly-calendar")
async def monthly_calendar(
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """返回某月每天是否有工时记录及工时汇总"""
    employee_id = current_user.employee_id
    if not employee_id:
        raise HTTPException(status_code=400, detail="当前用户未关联员工")

    # 项目工时（按日汇总）
    proj_result = await db.execute(
        select(
            DailyExecution.record_date,
            func.sum(ExecutionDetail.work_hours),
        )
        .join(DailyExecution, ExecutionDetail.execution_id == DailyExecution.id)
        .where(
            ExecutionDetail.employee_id == employee_id,
            func.strftime("%Y", DailyExecution.record_date) == str(year),
            func.strftime("%m", DailyExecution.record_date) == f"{month:02d}",
        )
        .group_by(DailyExecution.record_date)
    )
    proj_hours = {row[0]: float(row[1] or 0) for row in proj_result.all()}

    # 个人工时（按日汇总）
    pers_result = await db.execute(
        select(
            PersonalWorkEntry.record_date,
            func.sum(PersonalWorkEntry.work_hours),
        )
        .where(
            PersonalWorkEntry.employee_id == employee_id,
            func.strftime("%Y", PersonalWorkEntry.record_date) == str(year),
            func.strftime("%m", PersonalWorkEntry.record_date) == f"{month:02d}",
        )
        .group_by(PersonalWorkEntry.record_date)
    )
    pers_hours = {row[0]: float(row[1] or 0) for row in pers_result.all()}

    # 合并
    all_dates = set(proj_hours.keys()) | set(pers_hours.keys())
    dates = []
    for d in sorted(all_dates):
        ph = proj_hours.get(d, 0)
        eh = pers_hours.get(d, 0)
        dates.append({
            "date": d,
            "project_hours": round(ph, 1),
            "personal_hours": round(eh, 1),
            "total_hours": round(ph + eh, 1),
        })

    return {"year": year, "month": month, "dates": dates}
