import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Update connection string information
host = os.environ["POSTGRES_HOST"]
dbname = os.environ["POSTGRES_DB"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]

# Uses SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET env vars
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

# Construct connection string
conn_string = "host={0} user={1} password={2} dbname={3}".format(
    host, user, password, dbname
)
conn = psycopg2.connect(conn_string)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS tracks;")
# Create a table
cursor.execute(
    "CREATE TABLE tracks (id serial PRIMARY KEY, title VARCHAR(150), quantity INTEGER);"
)

results = sp.search(q="Beastie Boys", limit=50)

for idx, track in enumerate(results["tracks"]["items"]):
    cursor.execute(
        "INSERT INTO tracks (title, quantity) VALUES (%s, %s);", (track["name"], idx)
    )
    print(idx, track["name"])

# Clean up
conn.commit()
cursor.close()
conn.close()
