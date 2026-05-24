from datetime import datetime
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_code: str | None = None
    name: str
    region_province: str | None = None
    region_city: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    fund_source: str | None = None
    project_nature: str | None = None
    status: str = "进行中"
    manager_id: str | None = None
    remark: str | None = None


class ProjectUpdate(BaseModel):
    project_code: str | None = None
    name: str | None = None
    region_province: str | None = None
    region_city: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    fund_source: str | None = None
    project_nature: str | None = None
    status: str | None = None
    manager_id: str | None = None
    remark: str | None = None


class ProjectResponse(BaseModel):
    id: str
    project_code: str
    name: str
    region_province: str | None = None
    region_city: str | None = None
    party_a: str | None = None
    party_b: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    fund_source: str | None = None
    project_nature: str | None = None
    status: str
    manager_id: str | None = None
    manager_name: str | None = None
    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    total: int
    items: list[ProjectResponse]
