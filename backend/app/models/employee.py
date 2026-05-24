import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Text, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    work_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 工种
    personnel_type: Mapped[str] = mapped_column(String(20), default="事业人员")  # 事业人员/企业人员/派遣人员
    department: Mapped[str] = mapped_column(String(50), default="地理信息院")
    position: Mapped[str | None] = mapped_column(String(50))  # 职位
    phone: Mapped[str | None] = mapped_column(String(20))
    daily_wage: Mapped[float] = mapped_column(Float, default=0)  # 日工资
    hire_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(10), default="在职")  # 在职/离职/借调
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    personal_entries = relationship("PersonalWorkEntry", back_populates="employee")
