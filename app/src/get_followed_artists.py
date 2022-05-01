import json
import os
import sys

import pika
import psycopg2.errors
import spotipy
from spotipy.oauth2 import SpotifyPKCE

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger
import imports.requests

CHANNEL_ALBUMS_NAME = "artists"
CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
SPOTIFY_SCOPE = "user-follow-read"

log = get_logger(os.path.basename(__file__))


def main():
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    channel_related_artists = broker.create_channel(CHANNEL_RELATED_ARTISTS_NAME)

    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(
        auth_manager=SpotifyPKCE(scope=SPOTIFY_SCOPE, open_browser=False)
    )

    results = sp.current_user_followed_artists(limit=50)

    artists = results["artists"]["items"]

    # Iterate over results to get the full list
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        artists.extend(results["artists"]["items"])

    # Iterate over results, save to Postgres, push to Rabbit
    for i, item in enumerate(artists):
        try:
            cursor.execute(
                "INSERT INTO artists (spotify_id, name, popularity, followers, genres, genres_string, has_related, total_albums) VALUES (%s, %s, %s, %s, %s, %s, %s, 0) ON CONFLICT DO NOTHING;",
                (
                    item["id"],
                    item["name"],
                    item["popularity"],
                    item["followers"]["total"],
                    item["genres"],
                    " ".join(item["genres"]),
                    False,
                ),
            )
        except Exception as e:
            log.exception("Unhandled exception")
        else:
            # Only add to queue if it was added to the db
            if cursor.rowcount:
                log.info(
                    "👨🏽‍🎤 Artist saved",
                    id=item["id"],
                    name=item["name"],
                    status="saved",
                )
                channel_albums.basic_publish(
                    exchange="",
                    routing_key=CHANNEL_ALBUMS_NAME,
                    body=json.dumps(
                        {
                            "spotify_id": item["id"],
                            "total_albums": 0,
                            "name": item["name"],
                        }
                    ),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                )
                channel_related_artists.basic_publish(
                    exchange="",
                    routing_key=CHANNEL_RELATED_ARTISTS_NAME,
                    body=json.dumps({"spotify_id": item["id"], "name": item["name"]}),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                )
            else:
                log.info(
                    "👨🏽‍🎤 Artist exists",
                    id=item["id"],
                    name=item["name"],
                    status="skipped",
                )

    # Clean up and close connections
    broker.close_connection()
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
