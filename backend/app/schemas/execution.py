from datetime import date, datetime
from pydantic import BaseModel


class ExecutionDetailCreate(BaseModel):
    employee_id: str
    work_hours: float = 0
    work_content: str | None = None
    is_leave: bool = False
    leave_reason: str | None = None


class DailyExecutionCreate(BaseModel):
    project_id: str
    record_date: date
    seq_number: int = 1

    # 费用科目
    subcontract_fee: float = 0
    inhouse_personnel: float = 0
    enterprise_personnel: float = 0
    dispatched_personnel: float = 0
    relevant_fee: float = 0
    material_fee: float = 0
    labor_fee: float = 0
    rental_fee: float = 0
    transport_fee: float = 0
    office_fee: float = 0
    entertainment_fee: float = 0
    other_fee: float = 0
    travel_fee: float = 0
    bidding_fee: float = 0
    commission_fee: float = 0
    tax_fee: float = 0

    # 备注
    remark: str | None = None
    registrant: str = ""

    # 人员明细
    details: list[ExecutionDetailCreate] = []


class ExecutionDetailResponse(BaseModel):
    id: str
    employee_id: str
    employee_name: str | None = None
    work_hours: float
    daily_rate: float
    cost: float
    work_content: str | None = None
    is_leave: bool
    leave_reason: str | None = None

    class Config:
        from_attributes = True


class DailyExecutionResponse(BaseModel):
    id: str
    project_id: str
    project_name: str | None = None
    record_date: date
    seq_number: int

    subcontract_fee: float
    inhouse_personnel: float
    enterprise_personnel: float
    dispatched_personnel: float
    relevant_fee: float
    material_fee: float
    labor_fee: float
    rental_fee: float
    transport_fee: float
    office_fee: float
    entertainment_fee: float
    other_fee: float
    travel_fee: float
    bidding_fee: float
    commission_fee: float
    tax_fee: float

    daily_cost: float
    cumulative_cost: float
    cumulative_profit: float
    profit_rate: float

    remark: str | None = None
    status: str
    registrant: str
    reviewer: str | None = None
    details: list[ExecutionDetailResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
