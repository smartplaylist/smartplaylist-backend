"""Add more stats to db stats table

Revision ID: 0c41fff3c153
Revises: fc0cc90a7b17
Create Date: 2022-10-30 15:35:26.525613

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0c41fff3c153"
down_revision = "fc0cc90a7b17"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("db_stats", sa.Column("tracks_added", sa.Integer))
    op.add_column("db_stats", sa.Column("albums_added", sa.Integer))
    op.add_column("db_stats", sa.Column("artists_added", sa.Integer))
    op.add_column("db_stats", sa.Column("tracks_with_audiofeatures_added", sa.Integer))
    op.add_column("db_stats", sa.Column("albums_oldest_release_date", sa.Date))
    op.add_column("db_stats", sa.Column("albums_newest_release_date", sa.Date))
    op.add_column("db_stats", sa.Column("tracks_oldest_release_date", sa.Date))
    op.add_column("db_stats", sa.Column("tracks_newest_release_date", sa.Date))

    pass


def downgrade():
    op.drop_column("db_stats", "tracks_added")
    op.drop_column("db_stats", "albums_added")
    op.drop_column("db_stats", "artists_added")
    op.drop_column("db_stats", "albums_oldest_release_date")
    op.drop_column("db_stats", "albums_newest_release_date")
    op.drop_column("db_stats", "tracks_oldest_release_date")
    op.drop_column("db_stats", "tracks_newest_release_date")
    pass
