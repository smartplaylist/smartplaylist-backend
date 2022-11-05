"""Create tracks table

Revision ID: be6a440b9533
Revises: dd48b2f5e3fa
Create Date: 2022-02-13 12:46:11.545396

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "be6a440b9533"
down_revision = "dd48b2f5e3fa"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tracks",
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("main_artist", sa.Text, nullable=False),
        sa.Column("from_album", sa.Text, nullable=False),
        sa.Column("album_artist", sa.Text, nullable=False),
        sa.Column("main_artist_popularity", sa.SmallInteger, nullable=True),
        sa.Column("main_artist_followers", sa.Integer, nullable=True),
        sa.Column(
            "all_artists",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=False,
        ),
        sa.Column("release_date", sa.Date, nullable=False),
        sa.Column("genres", sa.dialects.postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("popularity", sa.SmallInteger, nullable=True),
        sa.Column("track_number", sa.SmallInteger, nullable=False),
        sa.Column("disc_number", sa.SmallInteger, nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("explicit", sa.Boolean, nullable=False),
        sa.Column("key", sa.SmallInteger, nullable=True),
        sa.Column("mode_is_major", sa.Boolean, nullable=True),
        sa.Column("time_signature", sa.SmallInteger, nullable=True),
        sa.Column("danceability", sa.SmallInteger, nullable=True),
        sa.Column("energy", sa.SmallInteger, nullable=True),
        sa.Column("speechiness", sa.SmallInteger, nullable=True),
        sa.Column("acousticness", sa.SmallInteger, nullable=True),
        sa.Column("instrumentalness", sa.SmallInteger, nullable=True),
        sa.Column("liveness", sa.SmallInteger, nullable=True),
        sa.Column("valence", sa.SmallInteger, nullable=True),
        sa.Column("tempo", sa.SmallInteger, nullable=True),
        sa.Column("loudness", sa.SmallInteger, nullable=True),
        sa.Column("danceability_raw", sa.Float(precision=5), nullable=True),
        sa.Column("energy_raw", sa.Float(precision=5), nullable=True),
        sa.Column("speechiness_raw", sa.Float(precision=5), nullable=True),
        sa.Column("acousticness_raw", sa.Float(precision=5), nullable=True),
        sa.Column("instrumentalness_raw", sa.Float(precision=5), nullable=True),
        sa.Column("liveness_raw", sa.Float(precision=5), nullable=True),
        sa.Column("valence_raw", sa.Float(precision=5), nullable=True),
        sa.Column("tempo_raw", sa.Float(precision=5), nullable=True),
        sa.Column("preview_url", sa.Text, nullable=True),
        sa.Column("spotify_id", sa.Text, primary_key=True),
        sa.Column("from_album_spotify_id", sa.Text, nullable=False),
        sa.Column("album_artist_spotify_id", sa.Text, nullable=False),
        sa.Column("all_artists_string", sa.Text, nullable=True),
        sa.Column("genres_string", sa.Text, nullable=True),
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

    op.create_unique_constraint(
        "unique_tracks_main_artist_name_duration",
        "tracks",
        ["main_artist", "name", "duration_ms"],
    )


def downgrade():
    op.drop_table("tracks")
