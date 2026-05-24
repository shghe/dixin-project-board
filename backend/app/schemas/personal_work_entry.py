from datetime import date, datetime
from pydantic import BaseModel


class PersonalWorkEntryCreate(BaseModel):
    record_date: date
    work_hours: float = 0
    work_content: str = ""
    category: str = "院务工作"


class PersonalWorkEntryUpdate(BaseModel):
    work_hours: float | None = None
    work_content: str | None = None
    category: str | None = None


class PersonalWorkEntryResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str | None = None
    record_date: date
    work_hours: float
    work_content: str | None = None
    category: str
    created_at: datetime

    class Config:
        from_attributes = True
