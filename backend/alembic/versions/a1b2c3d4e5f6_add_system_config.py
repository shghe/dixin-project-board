"""add_system_config

Revision ID: a1b2c3d4e5f6
Revises: 7f3a2b1c9d4e
Create Date: 2026-05-22 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "9b1d8f2a3c7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_config",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_system_config_key"), "system_config", ["key"])

    op.execute(
        "INSERT INTO system_config (id, key, value) VALUES "
        "('cfg_wage_1', 'wage_事业人员', '650'),"
        "('cfg_wage_2', 'wage_企业人员', '500'),"
        "('cfg_wage_3', 'wage_派遣人员', '380')"
    )


def downgrade() -> None:
    op.drop_table("system_config")
