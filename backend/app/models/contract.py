import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Text, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contract(Base):
    __tablename__ = "contract"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"), unique=True)
    contract_amount: Mapped[float] = mapped_column(Float, default=0)  # 合同金额
    discount_rate: Mapped[float] = mapped_column(Float, default=1.0)  # 折扣系数
    actual_amount: Mapped[float] = mapped_column(Float, default=0)  # 实际合同金额 = 合同金额 × 折扣系数
    sign_date: Mapped[date | None] = mapped_column(Date)  # 签订日期
    drafter: Mapped[str | None] = mapped_column(String(50))  # 合同起草人
    reviewer: Mapped[str | None] = mapped_column(String(50))  # 经营部审核人
    payment_terms: Mapped[str | None] = mapped_column(Text)  # 付款约定（富文本）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
