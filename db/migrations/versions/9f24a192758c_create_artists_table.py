"""Create artists table

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
        "artists",
        sa.Column("spotify_id", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("popularity", sa.SmallInteger, nullable=False),
        sa.Column("followers", sa.Integer, nullable=False),
        sa.Column("genres", sa.dialects.postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("genres_string", sa.Text, nullable=False),
        sa.Column("total_albums", sa.SmallInteger, nullable=False),
        sa.Column("last_update", sa.Date, nullable=True),
        sa.Column("related_to", sa.Text, nullable=True),
        sa.Column("related_to_spotify_id", sa.Text, nullable=True),
        sa.Column("has_related", sa.Boolean, nullable=False),
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


def downgrade():
    op.drop_table("artists")
