"""Add computed_genres_updated_at to tracks

Revision ID: 3c5111245113
Revises: bf1a5843503b
Create Date: 2022-11-06 22:21:20.934350

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3c5111245113"
down_revision = "bf1a5843503b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tracks", sa.Column("computed_genres_updated_at", sa.TIMESTAMP, nullable=True)
    )
    pass


def downgrade():
    op.drop_column("tracks", "computed_genres_updated_at")
    pass
