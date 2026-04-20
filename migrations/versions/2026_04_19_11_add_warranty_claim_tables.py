"""add warranty claim tables

Revision ID: 2026_04_19_11
Revises: 2026_04_19_10
Create Date: 2026-04-19 19:30:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_11"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "warranty_claim",
        sa.Column("warranty_claim_id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customer.customer_id"),
            nullable=False,
        ),
        sa.Column("claim_number", sa.String(length=75), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "warranty_claim_quote",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "warranty_claim_id",
            sa.Integer(),
            sa.ForeignKey("warranty_claim.warranty_claim_id"),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            sa.Integer(),
            sa.ForeignKey("service.service_id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("warranty_claim_quote")
    op.drop_table("warranty_claim")
