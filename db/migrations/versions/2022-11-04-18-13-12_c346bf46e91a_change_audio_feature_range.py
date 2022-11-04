"""Change audio feature range

Revision ID: c346bf46e91a
Revises: c1ce73b039bb
Create Date: 2022-11-04 18:13:12.003440

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c346bf46e91a"
down_revision = "c1ce73b039bb"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE tracks
        SET
            danceability=danceability_raw*100,
            energy=energy_raw*100,
            speechiness=speechiness_raw*100,
            acousticness=acousticness_raw*100,
            instrumentalness=instrumentalness_raw*100,
            liveness=liveness_raw*100,
            valence=valence_raw*100
        WHERE energy IS NOT NULL
        """
    )
    pass


def downgrade():
    op.execute(
        """
        UPDATE tracks
        SET
            danceability=danceability_raw*1000,
            energy=energy_raw*1000,
            speechiness=speechiness_raw*1000,
            acousticness=acousticness_raw*1000,
            instrumentalness=instrumentalness_raw*1000,
            liveness=liveness_raw*1000,
            valence=valence_raw*1000
        WHERE energy IS NOT NULL
        """
    )
    pass
