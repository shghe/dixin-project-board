import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Subcontract(Base):
    __tablename__ = "subcontract"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    company_name: Mapped[str] = mapped_column(String(200))  # 分包商名称
    qualification: Mapped[str | None] = mapped_column(String(100))  # 测绘资质
    company_scale: Mapped[str | None] = mapped_column(String(100))  # 公司规模
    contact_person: Mapped[str | None] = mapped_column(String(50))
    contact_phone: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str | None] = mapped_column(Text)  # 分包内容/任务
    amount: Mapped[float] = mapped_column(Float, default=0)  # 分包合同额
    settled_amount: Mapped[float] = mapped_column(Float, default=0)  # 已结算金额
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
