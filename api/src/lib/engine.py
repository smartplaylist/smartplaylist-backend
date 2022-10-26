import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_sessionmaker():

    # Update connection string information
    host = os.environ["POSTGRES_HOST"]
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    # Construct connection string
    conn_string = "postgresql://{0}:{1}@{2}/{3}".format(
        user, password, host, dbname
    )
    return sessionmaker(bind=create_engine(conn_string))
