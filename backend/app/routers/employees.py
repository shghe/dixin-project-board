from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import Employee, User
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/api/employees", tags=["人员管理"])


def generate_employee_code(employees: list[Employee]) -> str:
    year = str(date.today().year)
    codes = [e.employee_code for e in employees if e.employee_code.startswith(f"EMP{year}")]
    if codes:
        max_num = max(int(c[7:]) for c in codes if c[7:].isdigit())
        return f"EMP{year}{max_num + 1:03d}"
    return f"EMP{year}001"


@router.get("", response_model=list[EmployeeResponse])
async def list_employees(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Employee).order_by(Employee.employee_code)
    if status:
        query = query.where(Employee.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    result = await db.execute(select(Employee))
    code = generate_employee_code(list(result.scalars().all()))
    emp = Employee(employee_code=code, **data.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.get("/{emp_id}", response_model=EmployeeResponse)
async def get_employee(emp_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    return emp


@router.put("/{emp_id}", response_model=EmployeeResponse)
async def update_employee(
    emp_id: str, data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("director")),
):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(emp, k, v)
    await db.commit()
    await db.refresh(emp)
    return emp


@router.delete("/{emp_id}")
async def delete_employee(emp_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role("director"))):
    result = await db.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="员工不存在")
    await db.delete(emp)
    await db.commit()
    return {"message": "删除成功"}
