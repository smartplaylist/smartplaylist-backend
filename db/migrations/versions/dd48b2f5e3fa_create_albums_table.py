"""Create albums table

Revision ID: dd48b2f5e3fa
Revises: 9f24a192758c
Create Date: 2022-02-13 12:44:25.528634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dd48b2f5e3fa"
down_revision = "9f24a192758c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "albums",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("spotify_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("artists", sa.Text, nullable=False),
        sa.Column(
            "album_group",
            sa.Enum(
                "album", "single", "compilation", "appears_on", name="album_group_enum"
            ),
            nullable=False,
        ),
        sa.Column(
            "album_type",
            sa.Enum("album", "single", "compilation", name="album_type_enum"),
            nullable=False,
        ),
        sa.Column("release_date", sa.Text, nullable=False),
        sa.Column(
            "release_date_precision",
            sa.Enum("day", "month", "year", name="release_date_precision_enum"),
            nullable=False,
        ),
        sa.Column("total_tracks", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False),
    )
    op.create_unique_constraint("uniq_albums_spotify_id", "albums", ["spotify_id"])


def downgrade():
    op.drop_table("albums")
    op.execute("DROP TYPE album_group_enum")
    op.execute("DROP TYPE album_type_enum")
    op.execute("DROP TYPE release_date_precision_enum")
