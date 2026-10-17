import json
import os
import sys

from imports.custom_decorators import handle_exceptions
from imports.logging import get_logger
import imports.broker as broker
import imports.db as db
import pika
import spotipy

CHANNEL_ALBUMS_NAME = "artists"
CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
SPOTIFY_SCOPE = "user-follow-read"
SPOTIPY_AUTH_CACHE_PATH = ".cache-spotipy"

log = get_logger(os.path.basename(__file__))


def main():
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    channel_related_artists = broker.create_channel(CHANNEL_RELATED_ARTISTS_NAME)

    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyPKCE(
            scope=SPOTIFY_SCOPE,
            open_browser=False,
            cache_handler=spotipy.CacheFileHandler(
                cache_path=SPOTIPY_AUTH_CACHE_PATH
            )
        )
    )

    results = sp.current_user_followed_artists(limit=50)
    artists = results["artists"]["items"]

    # Iterate over results to get the full list
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        artists.extend(results["artists"]["items"])

    # Iterate over results, save to Postgres, push to Rabbit
    for i, item in enumerate(artists):
        @handle_exceptions
        def save_artist():
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
            # Only add to queue if it was added to the db
            if cursor.rowcount:
                log.info("👨🏽‍🎤 Artist saved", id=item["id"])

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
                log.info("👨🏽‍🎤 Artist exists", id=item["id"])

        save_artist()

    # Clean up and close connections
    broker.close_connection()
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    # Not using a decorator here because it's a control-flow exception
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
