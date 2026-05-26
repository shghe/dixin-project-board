from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.identity import PERSONNEL_TYPE_WAGES, load_personnel_wages
from app.models import Employee, SystemConfig, User

router = APIRouter(prefix="/api/settings", tags=["系统设置"])


@router.get("/wages")
async def get_wages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await load_personnel_wages(db)


@router.put("/wages")
async def update_wages(
    data: dict[str, float],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    for personnel_type in ("事业人员", "企业人员", "派遣人员"):
        if personnel_type not in data:
            raise HTTPException(status_code=400, detail=f"缺少 {personnel_type} 的工资配置")
    for personnel_type, wage in data.items():
        key = f"wage_{personnel_type}"
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        config = result.scalar_one_or_none()
        if config:
            config.value = str(wage)
        else:
            db.add(SystemConfig(key=key, value=str(wage)))
        # 批量更新已有员工的日工资
        emp_result = await db.execute(
            select(Employee).where(Employee.personnel_type == personnel_type)
        )
        for emp in emp_result.scalars().all():
            emp.daily_wage = wage
    await db.commit()
    return {"message": "工资标准已更新，员工日工资已同步"}
