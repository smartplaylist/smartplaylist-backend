"""create followed_artists table

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
        sa.Column("spotify_id", sa.String(50), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("popularity", sa.Integer, nullable=False),
        sa.Column("followers", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False),
    )


def downgrade():
    op.drop_table("followed_artists")
