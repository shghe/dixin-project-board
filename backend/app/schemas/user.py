from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    employee_id: str | None = None


class UserUpdate(BaseModel):
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    employee_id: str | None = None
    employee_name: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
