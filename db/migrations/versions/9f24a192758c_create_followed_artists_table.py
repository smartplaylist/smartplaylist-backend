"""create basic structure

Revision ID: 9f24a192758c
Revises:
Create Date: 2022-02-09 22:14:25.019965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f24a192758c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "followed_artists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("spotify_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("popularity", sa.Integer, nullable=False),
        sa.Column("followers", sa.Integer, nullable=False),
        sa.Column("genres", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False),
    )

    op.create_unique_constraint(
        "uniq_followed_artists_spotify_id", "followed_artists", ["spotify_id"]
    )

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

    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("spotify_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("popularity", sa.Integer, nullable=False),
        sa.Column("followers", sa.Integer, nullable=False),
        sa.Column("genres", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False),
    )

    op.create_unique_constraint("uniq_tracks_spotify_id", "tracks", ["spotify_id"])


def downgrade():
    op.drop_table("followed_artists")
    op.drop_table("albums")
    op.execute("DROP TYPE album_group_enum")
    op.execute("DROP TYPE album_type_enum")
    op.execute("DROP TYPE release_date_precision_enum")
