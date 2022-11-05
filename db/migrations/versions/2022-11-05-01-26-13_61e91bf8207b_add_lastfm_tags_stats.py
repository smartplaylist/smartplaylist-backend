"""Add lastfm tags stats

Revision ID: 61e91bf8207b
Revises: c346bf46e91a
Create Date: 2022-11-05 01:26:13.106139

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61e91bf8207b"
down_revision = "c346bf46e91a"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "db_stats", sa.Column("artists_with_null_lastfm_tags", sa.Integer)
    )
    op.add_column(
        "db_stats", sa.Column("albums_with_null_lastfm_tags", sa.Integer)
    )
    op.add_column(
        "db_stats", sa.Column("tracks_with_null_lastfm_tags", sa.Integer)
    )
    pass


def downgrade():
    op.drop_column("db_stats", "artists_with_null_lastfm_tags")
    op.drop_column("db_stats", "albums_with_null_lastfm_tags")
    op.drop_column("db_stats", "tracks_with_null_lastfm_tags")
    pass
