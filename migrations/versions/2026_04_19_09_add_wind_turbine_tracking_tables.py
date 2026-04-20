"""add wind turbine tracking tables

Revision ID: 2026_04_19_09
Revises: 2026_04_19_08
Create Date: 2026-04-19 19:08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_19_09"
down_revision: Union[str, Sequence[str], None] = "2026_04_19_08"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sites_gas_turbine",
        sa.Column("site_gas_turbine_id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(length=100), nullable=False),
        sa.Column("customer_name", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "sites_wind_turbine",
        sa.Column("site_wind_turbine_id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(length=100), nullable=False),
        sa.Column("customer_name", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "sites_wind_gas",
        sa.Column("site_wind_gas_id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(length=100), nullable=False),
        sa.Column("wind_units", sa.Integer(), nullable=True),
        sa.Column("gas_units", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "wind_turbine_leads",
        sa.Column("wind_turbine_lead_id", sa.Integer(), primary_key=True),
        sa.Column("customer_name", sa.String(length=100), nullable=False),
        sa.Column("contact_name", sa.String(length=100), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "wind_turbine_leads_details",
        sa.Column("wind_turbine_lead_detail_id", sa.Integer(), primary_key=True),
        sa.Column(
            "wind_turbine_lead_id",
            sa.Integer(),
            sa.ForeignKey("wind_turbine_leads.wind_turbine_lead_id"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("wind_turbine_leads_details")
    op.drop_table("wind_turbine_leads")
    op.drop_table("sites_wind_gas")
    op.drop_table("sites_wind_turbine")
    op.drop_table("sites_gas_turbine")
