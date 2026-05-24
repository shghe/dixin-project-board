from datetime import date, datetime
from pydantic import BaseModel


class ContractCreate(BaseModel):
    contract_amount: float = 0
    discount_rate: float = 1.0
    sign_date: date | None = None
    drafter: str | None = None
    reviewer: str | None = None
    payment_terms: str | None = None


class ContractUpdate(BaseModel):
    contract_amount: float | None = None
    discount_rate: float | None = None
    sign_date: date | None = None
    drafter: str | None = None
    reviewer: str | None = None
    payment_terms: str | None = None


class ContractResponse(BaseModel):
    id: str
    project_id: str
    contract_amount: float
    discount_rate: float
    actual_amount: float
    sign_date: date | None = None
    drafter: str | None = None
    reviewer: str | None = None
    payment_terms: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
