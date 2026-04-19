"""add parts sold table

Revision ID: 2026_04_19_02
Revises: 710365a126bc
Create Date: 2026-04-19 17:28:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_02"
down_revision: Union[str, Sequence[str], None] = "710365a126bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "parts_sold",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("part_id", sa.Integer(), sa.ForeignKey("part.part_id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("sold_date", sa.String(length=10), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("parts_sold")
