import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectDesign(Base):
    __tablename__ = "project_design"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"), unique=True)
    key_personnel: Mapped[str | None] = mapped_column(Text)  # JSON: 项目主要人员 [{name, role}]
    task_content: Mapped[str | None] = mapped_column(Text)  # 富文本: 作业任务
    review_date: Mapped[date | None] = mapped_column(Date)  # 审核时间
    remark: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project")
