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
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("main_artist", sa.Text, nullable=False),
        sa.Column(
            "all_artists",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=False,
        ),
        sa.Column("from_discography_of", sa.Text, nullable=False),
        sa.Column("release_date", sa.Date, nullable=False),
        sa.Column("total_tracks", sa.SmallInteger, nullable=False),
        sa.Column("popularity", sa.SmallInteger, nullable=True),
        sa.Column("label", sa.Text, nullable=True),
        sa.Column(
            "copyrights",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
        sa.Column(
            "album_group",
            sa.Enum(
                "album",
                "single",
                "compilation",
                "appears_on",
                name="album_group_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "album_type",
            sa.Enum("album", "single", "compilation", name="album_type_enum"),
            nullable=False,
        ),
        sa.Column("spotify_id", sa.Text, primary_key=True),
        sa.Column("main_artist_spotify_id", sa.Text, nullable=False),
        sa.Column("from_discography_of_spotify_id", sa.Text, nullable=False),
        sa.Column(
            "release_date_precision",
            sa.Enum("day", "month", "year", name="release_date_precision_enum"),
            nullable=False,
        ),
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
        "unique_albums_main_artist_name_total_tracks",
        "albums",
        ["main_artist", "name", "total_tracks"],
    )


def downgrade():
    op.drop_table("albums")
    op.execute("DROP TYPE album_group_enum")
    op.execute("DROP TYPE album_type_enum")
    op.execute("DROP TYPE release_date_precision_enum")
