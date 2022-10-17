"""Add columns for Lastfm tags

Revision ID: a6402b301348
Revises: 366afade137c
Create Date: 2022-05-05 21:18:13.570601

"""
from readline import insert_text
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a6402b301348"
down_revision = "366afade137c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "artists",
        sa.Column(
            "lastfm_tags",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )
    op.add_column(
        "artists",
        sa.Column(
            "lastfm_tags_string",
            sa.String(),
            nullable=True,
        ),
    )
    op.add_column(
        "albums",
        sa.Column(
            "lastfm_tags",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )
    op.add_column(
        "albums",
        sa.Column(
            "lastfm_tags_string",
            sa.String(),
            nullable=True,
        ),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "lastfm_tags",
            sa.dialects.postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )
    op.add_column(
        "tracks",
        sa.Column(
            "lastfm_tags_string",
            sa.String(),
            nullable=True,
        ),
    )
    pass


def downgrade():
    op.drop_column("artists", "lastfm_tags")
    op.drop_column("artists", "lastfm_tags_string")
    op.drop_column("albums", "lastfm_tags")
    op.drop_column("albums", "lastfm_tags_string")
    op.drop_column("tracks", "lastfm_tags")
    op.drop_column("tracks", "lastfm_tags_string")
    pass
