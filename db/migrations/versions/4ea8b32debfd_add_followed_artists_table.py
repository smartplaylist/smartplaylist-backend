"""Add followed artists table

Revision ID: 4ea8b32debfd
Revises: eede0f0f90b5
Create Date: 2022-08-14 20:06:00.052747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4ea8b32debfd"
down_revision = "eede0f0f90b5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_followed_artist",
        sa.Column(
            "artist_spotify_id",
            sa.Text,
            sa.ForeignKey("tracks.album_artist_spotify_id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Text, nullable=False),
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

    create_trigger = """
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON user_followed_artist
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_set_timestamp();
    """
    op.execute(create_trigger)

    pass


def downgrade():
    op.execute("DROP TRIGGER set_timestamp ON user_followed_artist")
    op.drop_table("user_followed_artist")
    pass
