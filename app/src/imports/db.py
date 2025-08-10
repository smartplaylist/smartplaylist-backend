import os

import psycopg2


def get_db_connection():
    """
    Establishes and returns a new connection to the PostgreSQL database.

    The caller is responsible for managing the connection lifecycle,
    preferably using a 'with' statement.
    """
    host = os.environ["POSTGRES_HOST"]
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    # Construct connection string using an f-string for better readability
    conn_string = f"host={host} user={user} password={password} dbname={dbname}"

    return psycopg2.connect(conn_string)
