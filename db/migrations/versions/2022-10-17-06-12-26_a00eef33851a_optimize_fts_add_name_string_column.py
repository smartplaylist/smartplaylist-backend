"""Optimize fts, add name_string column

Revision ID: a00eef33851a
Revises: 58ec6b4f51f6
Create Date: 2022-10-17 06:12:26.096891

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a00eef33851a"
down_revision = "58ec6b4f51f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tracks",
        sa.Column(
            "name_fts_string",
            sa.String(),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE tracks AS target set name_fts_string = (
            SELECT lower(name)
            FROM tracks AS source
            WHERE source.spotify_id = target.spotify_id
            );
        """
    )
    op.execute(
        """
        UPDATE tracks SET genres_string = LOWER(genres_string)
        """
    )
    op.execute(
        """
        UPDATE tracks SET all_artists_string = LOWER(all_artists_string)
        """
    )
    op.execute(
        """
        CREATE EXTENSION pg_trgm;
        """
    )
    op.create_index(
        "idx_gin_tracks_all_artists_string",
        "tracks",
        ["all_artists_string"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "all_artists_string": "gin_trgm_ops",
        },
    )
    op.create_index(
        "idx_gin_tracks_genres_string",
        "tracks",
        ["genres_string"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "genres_string": "gin_trgm_ops",
        },
    )
    op.create_index(
        "idx_gin_tracks_name_fts_string",
        "tracks",
        ["name_fts_string"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={
            "name_fts_string": "gin_trgm_ops",
        },
    )
    pass


def downgrade():
    op.drop_index("idx_gin_tracks_all_artists_string", table_name="tracks")
    op.drop_index("idx_gin_tracks_genres_string", table_name="tracks")
    op.drop_index("idx_gin_tracks_name_fts_string", table_name="tracks")
    op.drop_column("tracks", "name_fts_string")
    op.execute("DROP EXTENSION pg_trgm;")
    pass
