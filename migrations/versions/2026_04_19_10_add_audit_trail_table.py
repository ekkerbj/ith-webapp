"""add audit trail table

Revision ID: 2026_04_19_10
Revises: 2026_04_19_09
Create Date: 2026-04-19 19:22:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_10"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tblaudittrail",
        sa.Column("audit_trail_id", sa.Integer(), primary_key=True),
        sa.Column("table_name", sa.String(length=100), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tblaudittrail")
