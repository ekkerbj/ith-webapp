"""add audit trail changed by

Revision ID: 2026_04_20_02
Revises: 2026_04_20_01
Create Date: 2026-04-20 03:04:34.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2026_04_20_02"
down_revision: Union[str, Sequence[str], None] = "2026_04_20_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tblaudittrail",
        sa.Column("changed_by", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tblaudittrail", "changed_by")
