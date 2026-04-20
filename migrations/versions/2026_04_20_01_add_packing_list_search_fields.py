"""add packing list search fields

Revision ID: 2026_04_20_01
Revises: 2026_04_19_11
Create Date: 2026-04-20 01:01:23.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_04_20_01"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "packing_list",
        sa.Column("customer_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "packing_list",
        sa.Column("packing_date", sa.String(length=10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("packing_list", "packing_date")
    op.drop_column("packing_list", "customer_name")
