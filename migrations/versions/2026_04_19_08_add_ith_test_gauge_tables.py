"""add ith test gauge tables

Revision ID: 2026_04_19_08
Revises: 2026_04_19_07
Create Date: 2026-04-19 18:57:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_08"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ith_test_gauge_type",
        sa.Column("ith_test_gauge_type_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )
    op.create_table(
        "ith_test_gauge",
        sa.Column("ith_test_gauge_id", sa.Integer(), primary_key=True),
        sa.Column(
            "ith_test_gauge_type_id",
            sa.Integer(),
            sa.ForeignKey("ith_test_gauge_type.ith_test_gauge_type_id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=False, unique=True),
        sa.Column("calibration_due_date", sa.Date(), nullable=True),
        sa.Column("certification_due_date", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ith_test_gauge")
    op.drop_table("ith_test_gauge_type")
