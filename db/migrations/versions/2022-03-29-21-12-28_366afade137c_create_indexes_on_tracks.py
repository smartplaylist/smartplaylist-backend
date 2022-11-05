"""Create indexes on tracks

Revision ID: 366afade137c
Revises: 0423be170124
Create Date: 2022-03-29 21:12:28.698388

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "366afade137c"
down_revision = "0423be170124"
branch_labels = None
depends_on = None

MULTI_COLUMN = False


def upgrade():
    def single_columns():
        op.create_index("idx_tracks_name", "tracks", ["name"])
        op.create_index(
            "idx_tracks_all_artists_string", "tracks", ["all_artists_string"]
        )
        op.create_index("idx_tracks_genres_string", "tracks", ["genres_string"])
        op.create_index("idx_tracks_tempo", "tracks", ["tempo"])
        op.create_index("idx_tracks_popularity", "tracks", ["popularity"])
        op.create_index(
            "idx_tracks_main_artist_popularity",
            "tracks",
            ["main_artist_popularity"],
        )
        op.create_index(
            "idx_tracks_main_artist_followers",
            "tracks",
            ["main_artist_followers"],
        )
        op.create_index("idx_tracks_danceability", "tracks", ["danceability"])
        op.create_index("idx_tracks_energy", "tracks", ["energy"])
        op.create_index("idx_tracks_speechiness", "tracks", ["speechiness"])
        op.create_index("idx_tracks_acousticness", "tracks", ["acousticness"])
        op.create_index("idx_tracks_instrumentalness", "tracks", ["instrumentalness"])
        op.create_index("idx_tracks_liveness", "tracks", ["liveness"])
        op.create_index("idx_tracks_valence", "tracks", ["valence"])
        op.create_index("idx_tracks_release_date", "tracks", ["release_date"])

    def multi_column():
        op.create_index(
            "idx_tracks_all_colums",
            "tracks",
            [
                "name",
                "all_artists_string",
                "genres_string",
                "tempo",
                "popularity",
                "main_artist_popularity",
                "main_artist_followers",
                "danceability",
                "energy",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "release_date",
            ],
        )

    if MULTI_COLUMN:
        multi_column()
    else:
        single_columns()


def downgrade():
    def single_columns():
        op.drop_index("idx_tracks_name")
        op.drop_index("idx_tracks_all_artists_string")
        op.drop_index("idx_tracks_genres_string")
        op.drop_index("idx_tracks_tempo")
        op.drop_index("idx_tracks_popularity")
        op.drop_index("idx_tracks_main_artist_popularity")
        op.drop_index("idx_tracks_main_artist_followers")
        op.drop_index("idx_tracks_danceability")
        op.drop_index("idx_tracks_energy")
        op.drop_index("idx_tracks_speechiness")
        op.drop_index("idx_tracks_acousticness")
        op.drop_index("idx_tracks_instrumentalness")
        op.drop_index("idx_tracks_liveness")
        op.drop_index("idx_tracks_valence")
        op.drop_index("idx_tracks_release_date")

    def multi_column():
        op.drop_index("idx_tracks_all_colums")

    if MULTI_COLUMN:
        multi_column()
    else:
        single_columns()
