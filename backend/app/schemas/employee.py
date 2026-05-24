from datetime import date, datetime
from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    name: str
    work_type: str
    personnel_type: str = "事业人员"
    department: str = "地理信息院"
    position: str | None = None
    phone: str | None = None
    daily_wage: float = 0
    hire_date: date | None = None
    status: str = "在职"
    remark: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    work_type: str | None = None
    personnel_type: str | None = None
    department: str | None = None
    position: str | None = None
    phone: str | None = None
    daily_wage: float | None = None
    hire_date: date | None = None
    status: str | None = None
    remark: str | None = None


class EmployeeResponse(BaseModel):
    id: str
    employee_code: str
    name: str
    work_type: str
    personnel_type: str
    department: str
    position: str | None = None
    phone: str | None = None
    daily_wage: float
    hire_date: date | None = None
    status: str
    remark: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
