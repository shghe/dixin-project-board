from datetime import date, datetime
from pydantic import BaseModel


class ConstructionTaskCreate(BaseModel):
    task_name: str
    start_date: date
    duration_days: int = 0
    end_date: date
    sort_order: int = 0
    remark: str | None = None


class ConstructionTaskResponse(BaseModel):
    id: str
    project_id: str
    task_name: str
    start_date: date
    duration_days: int
    end_date: date
    sort_order: int
    remark: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
