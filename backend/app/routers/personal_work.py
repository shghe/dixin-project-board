from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PersonalWorkEntry, Employee, User, DailyExecution, ExecutionDetail
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

    # 项目工时
    proj_result = await db.execute(
        select(func.sum(ExecutionDetail.work_hours))
        .join(DailyExecution, ExecutionDetail.execution_id == DailyExecution.id)
        .where(
            ExecutionDetail.employee_id == employee_id,
            DailyExecution.record_date == record_date,
        )
    )
    project_hours = proj_result.scalar() or 0

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
        "project_hours": round(float(project_hours), 1),
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
