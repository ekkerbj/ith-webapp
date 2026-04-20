"""add part label table

Revision ID: 2026_04_20_03
Revises: 2026_04_20_02
Create Date: 2026-04-20 06:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_04_20_03"
down_revision: Union[str, Sequence[str], None] = "2026_04_20_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "part_label",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("check_in_id", sa.Integer(), sa.ForeignKey("check_in.id"), nullable=False),
        sa.Column(
            "check_in_sub_id",
            sa.Integer(),
            sa.ForeignKey("check_in_sub.id"),
            nullable=True,
        ),
        sa.Column("part_id", sa.Integer(), sa.ForeignKey("part.part_id"), nullable=True),
        sa.Column("part_number", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("warehouse", sa.String(length=100), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("part_label")
