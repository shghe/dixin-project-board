import uuid
from datetime import date, datetime
from sqlalchemy import String, Float, Date, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class PersonalWorkEntry(Base):
    __tablename__ = "personal_work_entry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id: Mapped[str] = mapped_column(String(36), ForeignKey("employee.id"), nullable=False)
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    work_hours: Mapped[float] = mapped_column(Float, default=0)
    work_content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(30), default="院务工作")  # 院务工作/行政事务/临时任务/培训学习
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="personal_entries")
