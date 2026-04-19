"""add rental tables

Revision ID: 2026_04_19_05
Revises: 2026_04_19_04
Create Date: 2026-04-19 18:14:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_05"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "rental_status",
        sa.Column("rental_status_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )
    op.create_table(
        "rental",
        sa.Column("rental_id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customer.customer_id"),
            nullable=False,
        ),
        sa.Column(
            "customer_tools_id",
            sa.Integer(),
            sa.ForeignKey("customer_tools.id"),
            nullable=False,
        ),
        sa.Column(
            "rental_status_id",
            sa.Integer(),
            sa.ForeignKey("rental_status.rental_status_id"),
            nullable=False,
        ),
        sa.Column(
            "rental_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("return_date", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("rental")
    op.drop_table("rental_status")
