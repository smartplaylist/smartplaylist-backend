"""Add computed_genres columns to tracks

Revision ID: eede0f0f90b5
Revises: a6402b301348
Create Date: 2022-08-12 09:18:20.218248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eede0f0f90b5"
down_revision = "a6402b301348"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tracks",
        sa.Column(
            "computed_genres",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "computed_genres_string",
            sa.String(),
            nullable=True,
        ),
    )
    pass


def downgrade():
    op.drop_column("tracks", "computed_genres")
    op.drop_column("tracks", "computed_genres_string")
    pass
