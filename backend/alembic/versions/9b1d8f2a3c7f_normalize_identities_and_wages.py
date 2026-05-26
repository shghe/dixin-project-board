"""normalize identities and wages

Revision ID: 9b1d8f2a3c7f
Revises: 7f3a2b1c9d4e
Create Date: 2026-05-25 21:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b1d8f2a3c7f"
down_revision: Union[str, None] = "7f3a2b1c9d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_MAP = {
    "director": "院长",
    "manager": "项目经理",
    "finance": "综合员",
    "employee": "技术员",
}

WORK_TYPE_MAP = {
    "director": "院长",
    "manager": "项目经理",
    "finance": "综合员",
    "employee": "技术员",
    "项目负责": "项目经理",
    "测量员": "技术员",
    "绘图员": "技术员",
    "内业": "综合员",
}

WAGE_MAP = {
    "院长": 650,
    "副院长": 600,
    "综合员": 420,
    "司机": 380,
    "项目经理": 520,
    "技术员": 488,
}


def upgrade() -> None:
    bind = op.get_bind()
    user_table = sa.table(
        "user",
        sa.column("id", sa.String()),
        sa.column("role", sa.String()),
    )
    employee_table = sa.table(
        "employee",
        sa.column("id", sa.String()),
        sa.column("work_type", sa.String()),
        sa.column("position", sa.String()),
        sa.column("daily_wage", sa.Float()),
    )

    for old, new in ROLE_MAP.items():
        bind.execute(
            sa.update(user_table).where(user_table.c.role == old).values(role=new)
        )

    for old, new in WORK_TYPE_MAP.items():
        bind.execute(
            sa.update(employee_table).where(employee_table.c.work_type == old).values(
                work_type=new,
                position=sa.case((employee_table.c.position == old, new), else_=employee_table.c.position),
                daily_wage=WAGE_MAP[new],
            )
        )

    for identity, wage in WAGE_MAP.items():
        bind.execute(
            sa.update(employee_table).where(employee_table.c.work_type == identity).values(daily_wage=wage)
        )


def downgrade() -> None:
    pass
