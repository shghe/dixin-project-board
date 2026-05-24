import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, Integer, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConstructionTask(Base):
    """施工横道图 - 项目任务时间线"""
    __tablename__ = "construction_task"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("project.id"))
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)  # 任务名称
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=0)  # 时长（天）
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    remark: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project = relationship("Project")
