"""add consignment list table

Revision ID: 2026_04_19_03
Revises: 2026_04_19_02
Create Date: 2026-04-19 17:45:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_03"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "consignment_list",
        sa.Column("consignment_list_id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customer.customer_id"), nullable=False),
        sa.Column("part_id", sa.Integer(), sa.ForeignKey("part.part_id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("consignment_list")
