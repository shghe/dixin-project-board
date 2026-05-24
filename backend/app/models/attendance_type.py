import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AttendanceType(Base):
    __tablename__ = "attendance_type"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 项目出勤/院务工作/行政事务/临时任务/请假
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # project/office/leave
    remark: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
