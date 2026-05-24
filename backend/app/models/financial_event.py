import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class FinancialEvent(Base):
    __tablename__ = "financial_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"), nullable=False)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 产值 / 开票 / 回款
    amount: Mapped[float] = mapped_column(Float, default=0)
    remark: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
