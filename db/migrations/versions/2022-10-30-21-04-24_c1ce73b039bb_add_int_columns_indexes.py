"""Add int columns indexes

Revision ID: c1ce73b039bb
Revises: 0c41fff3c153
Create Date: 2022-10-30 21:04:24.815057

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c1ce73b039bb"
down_revision = "0c41fff3c153"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "idx_tracks_int_colums_no_key",
        "tracks",
        [
            "release_date",
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
        ],
    )
    pass

    op.create_index(
        "idx_tracks_int_colums_and_key",
        "tracks",
        [
            "release_date",
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
            "key",
        ],
    )


def downgrade():
    op.drop_index("idx_tracks_int_colums_no_key")
    op.drop_index("idx_tracks_int_colums_and_key")
    pass
