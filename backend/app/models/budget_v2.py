"""测绘预算 V2 - 对应 DX20260411测绘预算.xlsx 结构"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Float, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BudgetSummary(Base):
    """预算概况（说明 sheet）"""
    __tablename__ = "budget_summary"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"), unique=True)

    project_name: Mapped[str | None] = mapped_column(String(200))
    party_a: Mapped[str | None] = mapped_column(String(200))
    contact_person: Mapped[str | None] = mapped_column(String(50))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(200))
    start_date: Mapped[str | None] = mapped_column(String(50))
    end_date: Mapped[str | None] = mapped_column(String(50))
    planned_duration: Mapped[str | None] = mapped_column(String(50))
    contract_amount: Mapped[float] = mapped_column(Float, default=0)
    tax_rate: Mapped[float] = mapped_column(Float, default=0)
    contract_no: Mapped[str | None] = mapped_column(String(50))
    contract_sign_date: Mapped[str | None] = mapped_column(String(50))
    implementing_unit: Mapped[str | None] = mapped_column(String(200))
    project_manager: Mapped[str | None] = mapped_column(String(50))
    tech_lead: Mapped[str | None] = mapped_column(String(50))
    compilation_basis: Mapped[str | None] = mapped_column(Text)
    construction_conditions: Mapped[str | None] = mapped_column(Text)
    work_content: Mapped[str | None] = mapped_column(Text)
    other_info: Mapped[str | None] = mapped_column(Text)
    drafter: Mapped[str | None] = mapped_column(String(50))
    checker: Mapped[str | None] = mapped_column(String(50))
    reviewer: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetPersonnel(Base):
    """人工费明细（1.1人工费 sheet）"""
    __tablename__ = "budget_personnel"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(20), default="企业编人员")  # 事业编人员 / 企业编人员
    position: Mapped[str | None] = mapped_column(String(50))
    employee_name: Mapped[str | None] = mapped_column(String(50))

    # 工资构成
    base_salary: Mapped[float] = mapped_column(Float, default=0)       # 基本工资及津补贴
    performance: Mapped[float] = mapped_column(Float, default=0)       # 绩效
    field_allowance: Mapped[float] = mapped_column(Float, default=0)   # 野外津贴
    heat_prevention: Mapped[float] = mapped_column(Float, default=0)   # 防暑降温
    union_fee: Mapped[float] = mapped_column(Float, default=0)         # 工会经费
    unit_coordination: Mapped[float] = mapped_column(Float, default=0) # 单位统筹

    work_months: Mapped[float] = mapped_column(Float, default=0.1)     # 计划工作时间(月)
    field_months: Mapped[float] = mapped_column(Float, default=0)      # 野外时间(月)

    # 自动计算
    salary_subtotal: Mapped[float] = mapped_column(Float, default=0)     # 薪酬小计
    welfare_subtotal: Mapped[float] = mapped_column(Float, default=0)    # 福利费小计
    coordination_subtotal: Mapped[float] = mapped_column(Float, default=0)# 单位统筹小计
    union_subtotal: Mapped[float] = mapped_column(Float, default=0)      # 工会经费小计
    total: Mapped[float] = mapped_column(Float, default=0)               # 合计

    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetMaterial(Base):
    """材料费明细（2.1材料费 sheet）"""
    __tablename__ = "budget_material"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(30), default="原材料")  # 原材料/专用材料费/燃油/技术资料费
    name: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(20))
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)  # unit_price * quantity
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetEquipment(Base):
    """机械使用费明细（3.1机械费 sheet）"""
    __tablename__ = "budget_equipment"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    classification: Mapped[str | None] = mapped_column(String(50))  # 工程施工用
    content: Mapped[str | None] = mapped_column(String(100))
    counterparty: Mapped[str | None] = mapped_column(String(100))  # 对方单位名称
    model: Mapped[str | None] = mapped_column(String(50))
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    quantity: Mapped[float] = mapped_column(Float, default=1)
    amount: Mapped[float] = mapped_column(Float, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetDirectCost(Base):
    """其他直接费明细（4.1其他直接费 sheet）"""
    __tablename__ = "budget_direct_cost"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(50))  # 运输费/装卸费/试验检测费/维修(护)费/办公费/出版印刷费/水电费/邮电费/取暖费/交通费
    content: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str | None] = mapped_column(String(20))
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetLabor(Base):
    """外聘人工费明细（4.1.5劳务费 sheet）"""
    __tablename__ = "budget_labor"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(30), default="临时聘用人员")  # 临时聘用人员 / 野外雇工
    position: Mapped[str | None] = mapped_column(String(50))
    employee_name: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(20))
    quantity: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetSubcontract(Base):
    """分包工程款明细（4.1.7分包工程款 sheet）"""
    __tablename__ = "budget_subcontract"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(30), default="工程分包费")  # 工程分包费/劳务分包费/委托技术服务费/委托试验费
    item_name: Mapped[str | None] = mapped_column(String(100))
    counterparty: Mapped[str | None] = mapped_column(String(100))
    workload: Mapped[float] = mapped_column(Float, default=1)
    unit_price: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetRDOther(Base):
    """研发费用 + 其他费用明细（4.1.19.1 + 4.1.19.2 sheet）"""
    __tablename__ = "budget_rd_other"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    cost_group: Mapped[str] = mapped_column(String(30), default="研发费用")  # 研发费用/其他管理费/其他工料费
    item: Mapped[str | None] = mapped_column(String(100))  # 人员人工/直接投入/折旧费用/...
    unit: Mapped[str | None] = mapped_column(String(20))
    base_price: Mapped[float] = mapped_column(Float, default=0)
    quantity: Mapped[float] = mapped_column(Float, default=0)
    amount: Mapped[float] = mapped_column(Float, default=0)
    remark: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
