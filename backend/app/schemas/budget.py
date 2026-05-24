from datetime import datetime
from pydantic import BaseModel


class BudgetItemCreate(BaseModel):
    category: str
    sub_category: str | None = None
    amount: float = 0
    quantity: int = 0
    work_days: float = 0
    unit_price: float = 0
    is_personnel: bool = False
    sort_order: int = 0
    remark: str | None = None


class BudgetItemUpdate(BaseModel):
    category: str | None = None
    sub_category: str | None = None
    amount: float | None = None
    quantity: int | None = None
    work_days: float | None = None
    unit_price: float | None = None
    is_personnel: bool | None = None
    sort_order: int | None = None
    remark: str | None = None


class BudgetItemResponse(BaseModel):
    id: str
    project_id: str
    category: str
    sub_category: str | None = None
    amount: float
    quantity: int
    work_days: float
    unit_price: float
    is_personnel: bool
    sort_order: int
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
