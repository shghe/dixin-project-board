"""测绘预算 V2 — Pydantic 请求/响应模型"""
from datetime import datetime
from pydantic import BaseModel


# ========== BudgetSummary ==========

class BudgetSummaryCreate(BaseModel):
    project_name: str | None = None
    party_a: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    planned_duration: str | None = None
    contract_amount: float = 0
    tax_rate: float = 0
    contract_no: str | None = None
    contract_sign_date: str | None = None
    implementing_unit: str | None = None
    project_manager: str | None = None
    tech_lead: str | None = None
    compilation_basis: str | None = None
    construction_conditions: str | None = None
    work_content: str | None = None
    other_info: str | None = None
    drafter: str | None = None
    checker: str | None = None
    reviewer: str | None = None


class BudgetSummaryResponse(BaseModel):
    id: str
    project_id: str
    project_name: str | None = None
    party_a: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    planned_duration: str | None = None
    contract_amount: float
    tax_rate: float
    contract_no: str | None = None
    contract_sign_date: str | None = None
    implementing_unit: str | None = None
    project_manager: str | None = None
    tech_lead: str | None = None
    compilation_basis: str | None = None
    construction_conditions: str | None = None
    work_content: str | None = None
    other_info: str | None = None
    drafter: str | None = None
    checker: str | None = None
    reviewer: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config: from_attributes = True


# ========== BudgetPersonnel ==========

class BudgetPersonnelCreate(BaseModel):
    category: str = "企业编人员"
    position: str | None = None
    employee_name: str | None = None
    base_salary: float = 0
    performance: float = 0
    field_allowance: float = 0
    heat_prevention: float = 0
    union_fee: float = 0
    unit_coordination: float = 0
    work_months: float = 0.1
    field_months: float = 0
    sort_order: int = 0


class BudgetPersonnelResponse(BaseModel):
    id: str
    project_id: str
    category: str
    position: str | None = None
    employee_name: str | None = None
    base_salary: float; performance: float; field_allowance: float
    heat_prevention: float; union_fee: float; unit_coordination: float
    work_months: float; field_months: float
    salary_subtotal: float; welfare_subtotal: float
    coordination_subtotal: float; union_subtotal: float
    total: float
    sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetMaterial ==========

class BudgetMaterialCreate(BaseModel):
    category: str = "原材料"
    name: str | None = None
    model: str | None = None
    unit: str | None = None
    unit_price: float = 0
    quantity: float = 0
    amount: float = 0
    remark: str | None = None
    sort_order: int = 0


class BudgetMaterialResponse(BaseModel):
    id: str; project_id: str
    category: str; name: str | None = None; model: str | None = None
    unit: str | None = None; unit_price: float; quantity: float; amount: float
    remark: str | None = None; sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetEquipment ==========

class BudgetEquipmentCreate(BaseModel):
    classification: str | None = None
    content: str | None = None
    counterparty: str | None = None
    model: str | None = None
    unit_price: float = 0
    quantity: float = 1
    amount: float = 0
    sort_order: int = 0


class BudgetEquipmentResponse(BaseModel):
    id: str; project_id: str
    classification: str | None = None; content: str | None = None
    counterparty: str | None = None; model: str | None = None
    unit_price: float; quantity: float; amount: float
    sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetDirectCost ==========

class BudgetDirectCostCreate(BaseModel):
    category: str
    content: str | None = None
    unit: str | None = None
    unit_price: float = 0
    quantity: float = 0
    amount: float = 0
    remark: str | None = None
    sort_order: int = 0


class BudgetDirectCostResponse(BaseModel):
    id: str; project_id: str
    category: str; content: str | None = None; unit: str | None = None
    unit_price: float; quantity: float; amount: float
    remark: str | None = None; sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetLabor ==========

class BudgetLaborCreate(BaseModel):
    category: str = "临时聘用人员"
    position: str | None = None
    employee_name: str | None = None
    unit: str | None = None
    quantity: float = 0
    unit_price: float = 0
    amount: float = 0
    remark: str | None = None
    sort_order: int = 0


class BudgetLaborResponse(BaseModel):
    id: str; project_id: str
    category: str; position: str | None = None; employee_name: str | None = None
    unit: str | None = None; quantity: float; unit_price: float; amount: float
    remark: str | None = None; sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetSubcontract ==========

class BudgetSubcontractCreate(BaseModel):
    category: str = "工程分包费"
    item_name: str | None = None
    counterparty: str | None = None
    workload: float = 1
    unit_price: float = 0
    amount: float = 0
    remark: str | None = None
    sort_order: int = 0


class BudgetSubcontractResponse(BaseModel):
    id: str; project_id: str
    category: str; item_name: str | None = None; counterparty: str | None = None
    workload: float; unit_price: float; amount: float
    remark: str | None = None; sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== BudgetRDOther ==========

class BudgetRDOtherCreate(BaseModel):
    cost_group: str = "研发费用"
    item: str | None = None
    unit: str | None = None
    base_price: float = 0
    quantity: float = 0
    amount: float = 0
    remark: str | None = None
    sort_order: int = 0


class BudgetRDOtherResponse(BaseModel):
    id: str; project_id: str
    cost_group: str; item: str | None = None; unit: str | None = None
    base_price: float; quantity: float; amount: float
    remark: str | None = None; sort_order: int
    created_at: datetime; updated_at: datetime
    class Config: from_attributes = True


# ========== Rollup (总表汇总) ==========

class BudgetRollupItem(BaseModel):
    """总表树节点"""
    level: int  # 1=一/二/..., 2=1.1/2.1/..., 3=⑴/⑵/...
    code: str  # 科目编号
    name: str  # 科目名称
    amount: float  # 金额
    remark: str | None = None  # 备注
    tax_rate: float = 0
    deductible_tax: float = 0
    children: list["BudgetRollupItem"] = []


class BudgetRollupResponse(BaseModel):
    total: float
    items: list[BudgetRollupItem]
