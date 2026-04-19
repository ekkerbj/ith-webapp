"""merge packing_list_sub branch

Revision ID: 9ad1a86501e2
Revises: 06ed979ec000, 2026_04_19_01
Create Date: 2026-04-19 15:40:08.732833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ad1a86501e2'
down_revision: Union[str, Sequence[str], None] = ('06ed979ec000', '2026_04_19_01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
