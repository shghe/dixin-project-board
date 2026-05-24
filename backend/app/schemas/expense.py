from datetime import date, datetime
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    project_id: str
    record_date: date
    expense_type: str
    amount: float
    detail: str | None = None
    registrant: str


class ExpenseUpdate(BaseModel):
    expense_type: str | None = None
    amount: float | None = None
    detail: str | None = None
    status: str | None = None  # 审核用


class ExpenseResponse(BaseModel):
    id: str
    project_id: str
    project_name: str | None = None
    record_date: date
    expense_type: str
    amount: float
    detail: str | None = None
    attachment: str | None = None
    registrant: str
    status: str
    reviewer: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
