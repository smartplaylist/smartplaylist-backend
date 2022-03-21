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
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("main_artist", sa.Text, nullable=False),
        sa.Column("from_album", sa.Text, nullable=False),
        sa.Column("album_artist", sa.Text, nullable=False),
        sa.Column("main_artist_popularity", sa.Integer, nullable=True),
        sa.Column("main_artist_followers", sa.Integer, nullable=True),
        sa.Column(
            "all_artists", sa.dialects.postgresql.ARRAY(sa.String()), nullable=False
        ),
        sa.Column("release_date", sa.Text, nullable=False),
        sa.Column("genres", sa.dialects.postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("popularity", sa.Integer, nullable=True),
        sa.Column("track_number", sa.Integer, nullable=False),
        sa.Column("disc_number", sa.Integer, nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("explicit", sa.Boolean, nullable=False),
        sa.Column("danceability", sa.Float(precision=5), nullable=True),
        sa.Column("energy", sa.Float(precision=5), nullable=True),
        sa.Column("key", sa.Integer, nullable=True),
        sa.Column("mode", sa.Integer, nullable=True),
        sa.Column("speechiness", sa.Float(precision=5), nullable=True),
        sa.Column("acousticness", sa.Float(precision=5), nullable=True),
        sa.Column("instrumentalness", sa.Float(precision=5), nullable=True),
        sa.Column("liveness", sa.Float(precision=5), nullable=True),
        sa.Column("valence", sa.Float(precision=5), nullable=True),
        sa.Column("tempo", sa.Float(precision=5), nullable=True),
        sa.Column("time_signature", sa.Integer, nullable=True),
        sa.Column("loudness", sa.Float(precision=5), nullable=True),
        sa.Column("preview_url", sa.Text, nullable=True),
        sa.Column("spotify_id", sa.Text, nullable=False),
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

    op.create_unique_constraint("unique_tracks_spotify_id", "tracks", ["spotify_id"])
    op.create_unique_constraint(
        "unique_tracks_main_artist_name_duration",
        "tracks",
        ["main_artist", "name", "duration_ms"],
    )


def downgrade():
    op.drop_table("tracks")
