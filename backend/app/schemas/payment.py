from datetime import date, datetime
from pydantic import BaseModel


class PaymentCreate(BaseModel):
    project_id: str
    payment_date: date
    payment_type: str
    amount: float
    remark: str | None = None


class PaymentResponse(BaseModel):
    id: str
    project_id: str
    payment_date: date
    payment_type: str
    amount: float
    remark: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
