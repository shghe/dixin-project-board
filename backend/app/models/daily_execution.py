import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Text, Float, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DailyExecution(Base):
    """每日执行单 - 合并费用+人员+财务的统一记录"""
    __tablename__ = "daily_execution"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    seq_number: Mapped[int] = mapped_column(Integer, default=1)  # 序号

    # 各费用科目当日金额
    subcontract_fee: Mapped[float] = mapped_column(Float, default=0)  # 分包费
    inhouse_personnel: Mapped[float] = mapped_column(Float, default=0)  # 事业人员费
    enterprise_personnel: Mapped[float] = mapped_column(Float, default=0)  # 企业人员费
    dispatched_personnel: Mapped[float] = mapped_column(Float, default=0)  # 派遣人员费
    relevant_fee: Mapped[float] = mapped_column(Float, default=0)  # 相关费用(住宿/车票)
    material_fee: Mapped[float] = mapped_column(Float, default=0)  # 材料费
    labor_fee: Mapped[float] = mapped_column(Float, default=0)  # 劳务费
    rental_fee: Mapped[float] = mapped_column(Float, default=0)  # 租赁费
    transport_fee: Mapped[float] = mapped_column(Float, default=0)  # 交通运输费
    office_fee: Mapped[float] = mapped_column(Float, default=0)  # 办公费
    entertainment_fee: Mapped[float] = mapped_column(Float, default=0)  # 招待费
    other_fee: Mapped[float] = mapped_column(Float, default=0)  # 其他费用
    travel_fee: Mapped[float] = mapped_column(Float, default=0)  # 差旅费
    bidding_fee: Mapped[float] = mapped_column(Float, default=0)  # 招投标费用
    commission_fee: Mapped[float] = mapped_column(Float, default=0)  # 业务员提成
    tax_fee: Mapped[float] = mapped_column(Float, default=0)  # 税金

    # 自动计算
    daily_cost: Mapped[float] = mapped_column(Float, default=0)  # 当日成本合计
    cumulative_cost: Mapped[float] = mapped_column(Float, default=0)  # 累计成本
    cumulative_profit: Mapped[float] = mapped_column(Float, default=0)  # 累计利润额
    profit_rate: Mapped[float] = mapped_column(Float, default=0)  # 利润率

    # 财务数据（可选，仅在发生财务事件时填写）
    invoice_amount: Mapped[float] = mapped_column(Float, default=0)  # 开票
    output_value: Mapped[float] = mapped_column(Float, default=0)  # 产值
    received_amount: Mapped[float] = mapped_column(Float, default=0)  # 回款
    balance_amount: Mapped[float] = mapped_column(Float, default=0)  # 尾款
    receivable: Mapped[float] = mapped_column(Float, default=0)  # 应收账款
    unsettled_value: Mapped[float] = mapped_column(Float, default=0)  # 未结算产值

    # 工作内容备注
    remark: Mapped[str | None] = mapped_column(Text)  # 当日工作内容描述

    # 审核
    status: Mapped[str] = mapped_column(String(10), default="待审核")
    reviewer: Mapped[str | None] = mapped_column(String(50))
    registrant: Mapped[str] = mapped_column(String(50))  # 登记人

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
    details = relationship("ExecutionDetail", back_populates="execution", cascade="all, delete-orphan")


class ExecutionDetail(Base):
    """每日执行单 - 人员投入明细"""
    __tablename__ = "execution_detail"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id: Mapped[str] = mapped_column(String(36), ForeignKey("daily_execution.id"))
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employee.id"))
    work_hours: Mapped[float] = mapped_column(Float, default=0)  # 工时（小时）
    daily_rate: Mapped[float] = mapped_column(Float, default=0)  # 日工资（快照）
    cost: Mapped[float] = mapped_column(Float, default=0)  # 当日人力成本 = 工时/8 × 日工资
    work_content: Mapped[str | None] = mapped_column(Text)
    is_leave: Mapped[bool] = mapped_column(Boolean, default=False)
    leave_reason: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    execution = relationship("DailyExecution", back_populates="details")
    employee = relationship("Employee")
