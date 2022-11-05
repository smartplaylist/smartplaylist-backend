import os

import psycopg2


def init_connection():
    """Init connection the database"""
    # Update connection string information
    host = os.environ["POSTGRES_HOST"]
    dbname = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    # Construct connection string
    conn_string = "host={0} user={1} password={2} dbname={3}".format(
        host, user, password, dbname
    )
    connection = psycopg2.connect(conn_string)
    connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    return connection, cursor


# Czy to tworzy kopię obiektu connection, czy przekazuje wskaźnik?
def close_connection(connection, cursor):
    """Close connection with the database and clean up"""
    connection.commit()
    cursor.close()
    connection.close()
    return True
