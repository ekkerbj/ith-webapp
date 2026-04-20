"""add field service tables

Revision ID: 2026_04_19_04
Revises: 2026_04_19_03
Create Date: 2026-04-19 18:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_04"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "field_service_status",
        sa.Column("field_service_status_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )
    op.create_table(
        "field_service_type",
        sa.Column("field_service_type_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )
    op.create_table(
        "field_service",
        sa.Column("field_service_id", sa.Integer(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customer.customer_id"),
            nullable=False,
        ),
        sa.Column(
            "field_service_status_id",
            sa.Integer(),
            sa.ForeignKey("field_service_status.field_service_status_id"),
            nullable=False,
        ),
        sa.Column(
            "visit_date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("visit_notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "field_service_sub",
        sa.Column("field_service_sub_id", sa.Integer(), primary_key=True),
        sa.Column(
            "field_service_type_id",
            sa.Integer(),
            sa.ForeignKey("field_service_type.field_service_type_id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("field_service_sub")
    op.drop_table("field_service")
    op.drop_table("field_service_type")
    op.drop_table("field_service_status")
