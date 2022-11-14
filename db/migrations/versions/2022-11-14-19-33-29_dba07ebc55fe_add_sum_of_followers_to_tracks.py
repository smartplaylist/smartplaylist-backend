"""Add sum_of_followers_to_tracks

Revision ID: dba07ebc55fe
Revises: bf1a5843503b
Create Date: 2022-11-14 19:33:29.501866

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "dba07ebc55fe"
down_revision = "bf1a5843503b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tracks",
        sa.Column(
            "sum_of_artists_followers", sa.Integer, nullable=False, server_default="-1"
        ),
    )

    op.alter_column("tracks", "sum_of_artists_followers", server_default=None)

    op.add_column(
        "tracks",
        sa.Column(
            "average_artists_popularity",
            sa.Integer,
            nullable=False,
            server_default="-1",
        ),
    )
    op.alter_column("tracks", "average_artists_popularity", server_default=None)
    pass


def downgrade():
    op.drop_column("tracks", "sum_of_artists_followers")
    op.drop_column("tracks", "average_artists_popularity")
    pass
