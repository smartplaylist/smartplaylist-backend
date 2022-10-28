"""Add db stats table

Revision ID: fc0cc90a7b17
Revises: 2f2c3d5e6eb3
Create Date: 2022-10-28 21:47:44.006615

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fc0cc90a7b17"
down_revision = "2f2c3d5e6eb3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "db_stats",
        sa.Column("total_tracks", sa.Integer),
        sa.Column("total_albums", sa.Integer),
        sa.Column("total_artists", sa.Integer),
        sa.Column("tracks_with_audiofeature", sa.Integer),
        sa.Column("track_min_updated_at", sa.TIMESTAMP),
        sa.Column("track_max_updated_at", sa.TIMESTAMP),
        sa.Column("track_min_created_at", sa.TIMESTAMP),
        sa.Column("track_max_created_at", sa.TIMESTAMP),
        sa.Column("album_min_updated_at", sa.TIMESTAMP),
        sa.Column("album_max_updated_at", sa.TIMESTAMP),
        sa.Column("album_min_created_at", sa.TIMESTAMP),
        sa.Column("album_max_created_at", sa.TIMESTAMP),
        sa.Column("artist_min_updated_at", sa.TIMESTAMP),
        sa.Column("artist_max_updated_at", sa.TIMESTAMP),
        sa.Column("artist_min_created_at", sa.TIMESTAMP),
        sa.Column("artist_max_created_at", sa.TIMESTAMP),
        sa.Column("artist_albums_updated_at_min", sa.TIMESTAMP),
        sa.Column("artist_albums_updated_at_max", sa.TIMESTAMP),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
    )
    pass


def downgrade():
    op.drop_table("db_stats")
    pass
