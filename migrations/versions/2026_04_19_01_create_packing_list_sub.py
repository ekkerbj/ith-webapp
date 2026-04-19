"""
Revision ID: 2026_04_19_01
Revises: 
Create Date: 2026-04-19 15:36:00

Migration for PackingListSub model and packing_list_sub table.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026_04_19_01'
down_revision = '495af0c84c13'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'packing_list_sub',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('packing_list_id', sa.Integer(), sa.ForeignKey('packing_list.id'), nullable=False),
        sa.Column('harm_number', sa.String(32), nullable=True),
        sa.Column('EECN', sa.String(32), nullable=True),
        sa.Column('DDTC', sa.String(32), nullable=True),
        sa.Column('COO', sa.String(32), nullable=True),
        sa.Column('in_bond_code', sa.String(32), nullable=True),
    )

def downgrade():
    op.drop_table('packing_list_sub')
