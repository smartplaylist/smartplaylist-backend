"""Add lastfm added tags stats

Revision ID: bf1a5843503b
Revises: 61e91bf8207b
Create Date: 2022-11-05 01:51:01.704959

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "bf1a5843503b"
down_revision = "61e91bf8207b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "db_stats",
        sa.Column(
            "artists_lastfm_tags_added", sa.Integer, nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "db_stats",
        sa.Column(
            "albums_lastfm_tags_added", sa.Integer, nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "db_stats",
        sa.Column(
            "tracks_lastfm_tags_added", sa.Integer, nullable=False, server_default="0"
        ),
    )
    pass


def downgrade():
    op.drop_column("db_stats", "artists_lastfm_tags_added")
    op.drop_column("db_stats", "albums_lastfm_tags_added")
    op.drop_column("db_stats", "tracks_lastfm_tags_added")
    pass
