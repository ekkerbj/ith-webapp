"""add projects table

Revision ID: 2026_04_19_06
Revises: 2026_04_19_05
Create Date: 2026-04-19 18:28:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_06"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "projects",
        sa.Column("project_id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customer.customer_id"),
            nullable=False,
        ),
        sa.Column("cardcode", sa.String(length=75), nullable=True),
        sa.Column("project_name", sa.String(length=100), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("projects")
