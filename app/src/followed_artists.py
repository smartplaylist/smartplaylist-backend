import os, time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Update connection string information
host = os.environ["POSTGRES_HOST"]
dbname = os.environ["POSTGRES_DB"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]

# Get your token at: <https://developer.spotify.com/console/get-current-user-top-artists-and-tracks/?type=&time_range=&limit=&offset=>
oauth_token = os.environ["SPOTIPY_OAUTH_TOKEN"]
sp = spotipy.Spotify(auth=oauth_token)

# Construct connection string
conn_string = "host={0} user={1} password={2} dbname={3}".format(
    host, user, password, dbname
)
conn = psycopg2.connect(conn_string)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Iterate over results to get the full list
results = sp.current_user_followed_artists(limit=50)
followed_artists = results["artists"]["items"]
while results["artists"]["next"]:
    results = sp.next(results["artists"])
    followed_artists.extend(results["artists"]["items"])

# Save to db
for i, item in enumerate(followed_artists):
    cursor.execute(
        "INSERT INTO followed_artists (spotify_id, name, popularity, followers, created_at, updated_at) VALUES (%s, %s, %s, %s, now(), now());",
        (item["id"], item["name"], item["popularity"], item["followers"]["total"]),
    )
    print("Saved ", i, item["name"])

# Clean up
conn.commit()
cursor.close()
conn.close()
