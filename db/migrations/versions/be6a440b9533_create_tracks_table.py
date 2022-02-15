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
        sa.Column("spotify_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("artists", sa.Text, nullable=False),
        sa.Column("popularity", sa.Integer, nullable=True),
        sa.Column("track_number", sa.Integer, nullable=False),
        sa.Column("disc_number", sa.Integer, nullable=False),
        sa.Column("duration_ms", sa.Integer, nullable=False),
        sa.Column("explicit", sa.Boolean, nullable=False),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False),
    )

    op.create_unique_constraint("uniq_tracks_spotify_id", "tracks", ["spotify_id"])


def downgrade():
    op.drop_table("tracks")
