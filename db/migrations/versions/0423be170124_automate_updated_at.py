"""Automate updated_at

Revision ID: 0423be170124
Revises: be6a440b9533
Create Date: 2022-03-11 21:46:20.318123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0423be170124"
down_revision = "be6a440b9533"
branch_labels = None
depends_on = None


def upgrade():
    # Create the function to be triggered to automatically set updated_at with now() on every UPDATE
    create_function = """
        CREATE OR REPLACE FUNCTION trigger_set_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    op.execute(create_function)

    create_trigger = """
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON artists
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_set_timestamp();
    """
    op.execute(create_trigger)

    create_trigger = """
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON tracks
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_set_timestamp();
    """
    op.execute(create_trigger)

    create_trigger = """
        CREATE TRIGGER set_timestamp
        BEFORE UPDATE ON albums
        FOR EACH ROW
        EXECUTE PROCEDURE trigger_set_timestamp();
    """
    op.execute(create_trigger)


def downgrade():
    op.execute("DROP TRIGGER set_timestamp ON artists")
    op.execute("DROP TRIGGER set_timestamp ON tracks")
    op.execute("DROP TRIGGER set_timestamp ON albums")
    op.execute("DROP FUNCTION trigger_set_timestamp")
