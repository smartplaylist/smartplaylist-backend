"""Add updated_at and created_at indexes

Revision ID: 2f2c3d5e6eb3
Revises: a00eef33851a
Create Date: 2022-10-28 19:41:15.403481

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f2c3d5e6eb3"
down_revision = "a00eef33851a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("idx_tracks_updated_at", "tracks", ["updated_at"])
    op.create_index("idx_tracks_created_at", "tracks", ["created_at"])
    op.create_index("idx_albums_updated_at", "albums", ["updated_at"])
    op.create_index("idx_albums_created_at", "albums", ["created_at"])
    op.create_index("idx_artists_updated_at", "artists", ["updated_at"])
    op.create_index("idx_artists_created_at", "artists", ["created_at"])
    op.create_index("idx_artists_albums_updated_at", "artists", ["albums_updated_at"])

    pass


def downgrade():
    op.drop_index("idx_tracks_updated_at")
    op.drop_index("idx_tracks_created_at")
    op.drop_index("idx_albums_updated_at")
    op.drop_index("idx_albums_created_at")
    op.drop_index("idx_artists_updated_at")
    op.drop_index("idx_artists_created_at")
    op.drop_index("idx_artists_albums_updated_at")
    pass
