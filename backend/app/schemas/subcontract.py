from datetime import datetime
from pydantic import BaseModel


class SubcontractCreate(BaseModel):
    company_name: str
    qualification: str | None = None
    company_scale: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    content: str | None = None
    amount: float = 0
    settled_amount: float = 0
    remark: str | None = None


class SubcontractResponse(BaseModel):
    id: str
    project_id: str
    company_name: str
    qualification: str | None = None
    company_scale: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    content: str | None = None
    amount: float
    settled_amount: float
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
