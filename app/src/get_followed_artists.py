import os, time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import imports.db as db
import imports.broker as broker

QUEUE_NAME = "followed_artists"


def main():
    broker_connection, channel = broker.create_channel(QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth=os.environ["SPOTIPY_OAUTH_TOKEN"])

    # Iterate over results to get the full list
    results = sp.current_user_followed_artists(limit=50)
    followed_artists = results["artists"]["items"]
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        followed_artists.extend(results["artists"]["items"])

    # Iterate over results, save to Postgres, push to Rabbit
    for i, item in enumerate(followed_artists):
        cursor.execute(
            "INSERT INTO followed_artists (spotify_id, name, popularity, followers, created_at, updated_at) VALUES (%s, %s, %s, %s, now(), now());",
            (item["id"], item["name"], item["popularity"], item["followers"]["total"]),
        )
        channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=item["id"])
        print("Saved ", i, item["name"])

    # Clean up and close connections
    broker.close_connection(broker_connection)
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    main()
