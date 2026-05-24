import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    __tablename__ = "project"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    region_province: Mapped[str | None] = mapped_column(String(50))
    region_city: Mapped[str | None] = mapped_column(String(50))
    party_a: Mapped[str | None] = mapped_column(String(200))  # 甲方
    party_b: Mapped[str | None] = mapped_column(String(200))  # 乙方
    contact_person: Mapped[str | None] = mapped_column(String(50))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    fund_source: Mapped[str | None] = mapped_column(String(30))  # 资金来源
    project_nature: Mapped[str | None] = mapped_column(String(30))  # 项目性质
    status: Mapped[str] = mapped_column(String(20), default="进行中")  # 进行中/已完成/已暂停
    manager_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("employee.id"))
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    manager = relationship("Employee", foreign_keys=[manager_id])
