from datetime import date, datetime
from pydantic import BaseModel


class AttendanceDetailCreate(BaseModel):
    employee_id: str
    work_hours: float = 0
    work_content: str | None = None
    is_leave: bool = False
    leave_reason: str | None = None


class AttendanceCreate(BaseModel):
    project_id: str
    record_date: date
    attendance_type_id: str
    remark: str | None = None
    details: list[AttendanceDetailCreate] = []


class AttendanceUpdate(BaseModel):
    project_id: str | None = None
    record_date: date | None = None
    attendance_type_id: str | None = None
    status: str | None = None
    remark: str | None = None
    details: list[AttendanceDetailCreate] | None = None


class AttendanceDetailResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str | None = None
    work_hours: float
    work_content: str | None = None
    is_leave: bool
    leave_reason: str | None = None

    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    id: str
    project_id: str
    project_name: str | None = None
    record_date: date
    manager_id: str
    manager_name: str | None = None
    attendance_type_id: str
    attendance_type_name: str | None = None
    status: str
    remark: str | None = None
    details: list[AttendanceDetailResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
