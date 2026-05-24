import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Float, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BudgetItem(Base):
    """项目预算 - 费用科目体系"""
    __tablename__ = "budget_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # 一级科目
    sub_category: Mapped[str | None] = mapped_column(String(50))  # 二级科目
    amount: Mapped[float] = mapped_column(Float, default=0)  # 预算金额
    quantity: Mapped[int] = mapped_column(Integer, default=0)  # 人数/数量
    work_days: Mapped[float] = mapped_column(Float, default=0)  # 工日
    unit_price: Mapped[float] = mapped_column(Float, default=0)  # 单价/日工资
    is_personnel: Mapped[bool] = mapped_column(default=False)  # 是否人员成本
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
