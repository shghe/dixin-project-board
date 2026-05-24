from datetime import date, datetime
from pydantic import BaseModel


class FinancialEventCreate(BaseModel):
    event_date: date
    event_type: str  # 产值 / 开票 / 回款
    amount: float = 0
    remark: str | None = None


class FinancialEventUpdate(BaseModel):
    event_date: date | None = None
    event_type: str | None = None
    amount: float | None = None
    remark: str | None = None


class FinancialEventResponse(BaseModel):
    id: str
    project_id: str
    event_date: date
    event_type: str
    amount: float
    remark: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
