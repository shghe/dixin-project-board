"""add_budget_v2_tables

Revision ID: 7f3a2b1c9d4e
Revises: e0a651d94cbe
Create Date: 2026-05-25 08:20:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7f3a2b1c9d4e"
down_revision: Union[str, None] = "e0a651d94cbe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _drop_table_if_exists(table_name: str) -> None:
    if _has_table(table_name):
        op.drop_table(table_name)


def upgrade() -> None:
    if not _has_table("budget_summary"):
        op.create_table(
            "budget_summary",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("project_name", sa.String(length=200), nullable=True),
            sa.Column("party_a", sa.String(length=200), nullable=True),
            sa.Column("contact_person", sa.String(length=50), nullable=True),
            sa.Column("contact_phone", sa.String(length=30), nullable=True),
            sa.Column("address", sa.Text(), nullable=True),
            sa.Column("location", sa.String(length=200), nullable=True),
            sa.Column("start_date", sa.String(length=50), nullable=True),
            sa.Column("end_date", sa.String(length=50), nullable=True),
            sa.Column("planned_duration", sa.String(length=50), nullable=True),
            sa.Column("contract_amount", sa.Float(), nullable=False),
            sa.Column("tax_rate", sa.Float(), nullable=False),
            sa.Column("contract_no", sa.String(length=50), nullable=True),
            sa.Column("contract_sign_date", sa.String(length=50), nullable=True),
            sa.Column("implementing_unit", sa.String(length=200), nullable=True),
            sa.Column("project_manager", sa.String(length=50), nullable=True),
            sa.Column("tech_lead", sa.String(length=50), nullable=True),
            sa.Column("compilation_basis", sa.Text(), nullable=True),
            sa.Column("construction_conditions", sa.Text(), nullable=True),
            sa.Column("work_content", sa.Text(), nullable=True),
            sa.Column("other_info", sa.Text(), nullable=True),
            sa.Column("drafter", sa.String(length=50), nullable=True),
            sa.Column("checker", sa.String(length=50), nullable=True),
            sa.Column("reviewer", sa.String(length=50), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("project_id"),
        )

    if not _has_table("budget_personnel"):
        op.create_table(
            "budget_personnel",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=20), nullable=False),
            sa.Column("position", sa.String(length=50), nullable=True),
            sa.Column("employee_name", sa.String(length=50), nullable=True),
            sa.Column("base_salary", sa.Float(), nullable=False),
            sa.Column("performance", sa.Float(), nullable=False),
            sa.Column("field_allowance", sa.Float(), nullable=False),
            sa.Column("heat_prevention", sa.Float(), nullable=False),
            sa.Column("union_fee", sa.Float(), nullable=False),
            sa.Column("unit_coordination", sa.Float(), nullable=False),
            sa.Column("work_months", sa.Float(), nullable=False),
            sa.Column("field_months", sa.Float(), nullable=False),
            sa.Column("salary_subtotal", sa.Float(), nullable=False),
            sa.Column("welfare_subtotal", sa.Float(), nullable=False),
            sa.Column("coordination_subtotal", sa.Float(), nullable=False),
            sa.Column("union_subtotal", sa.Float(), nullable=False),
            sa.Column("total", sa.Float(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_material"):
        op.create_table(
            "budget_material",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=30), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=True),
            sa.Column("model", sa.String(length=50), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("unit_price", sa.Float(), nullable=False),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_equipment"):
        op.create_table(
            "budget_equipment",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("classification", sa.String(length=50), nullable=True),
            sa.Column("content", sa.String(length=100), nullable=True),
            sa.Column("counterparty", sa.String(length=100), nullable=True),
            sa.Column("model", sa.String(length=50), nullable=True),
            sa.Column("unit_price", sa.Float(), nullable=False),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_direct_cost"):
        op.create_table(
            "budget_direct_cost",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False),
            sa.Column("content", sa.String(length=100), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("unit_price", sa.Float(), nullable=False),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_labor"):
        op.create_table(
            "budget_labor",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=30), nullable=False),
            sa.Column("position", sa.String(length=50), nullable=True),
            sa.Column("employee_name", sa.String(length=50), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("unit_price", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_subcontract"):
        op.create_table(
            "budget_subcontract",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=30), nullable=False),
            sa.Column("item_name", sa.String(length=100), nullable=True),
            sa.Column("counterparty", sa.String(length=100), nullable=True),
            sa.Column("workload", sa.Float(), nullable=False),
            sa.Column("unit_price", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("budget_rd_other"):
        op.create_table(
            "budget_rd_other",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("cost_group", sa.String(length=30), nullable=False),
            sa.Column("item", sa.String(length=100), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("base_price", sa.Float(), nullable=False),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    _drop_table_if_exists("budget_rd_other")
    _drop_table_if_exists("budget_subcontract")
    _drop_table_if_exists("budget_labor")
    _drop_table_if_exists("budget_direct_cost")
    _drop_table_if_exists("budget_equipment")
    _drop_table_if_exists("budget_material")
    _drop_table_if_exists("budget_personnel")
    _drop_table_if_exists("budget_summary")
