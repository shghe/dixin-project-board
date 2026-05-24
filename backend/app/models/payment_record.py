import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Text, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PaymentRecord(Base):
    __tablename__ = "payment_record"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 首付/进度款/尾款/其他
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project = relationship("Project")
