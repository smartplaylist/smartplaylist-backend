import json
import os
import sys

from imports.logging import get_logger
import imports.broker as broker
import imports.db as db
import pika
import spotipy
from psycopg2.extras import execute_values

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
            ),
        )
    )

    results = sp.current_user_followed_artists(limit=50)
    artists = results["artists"]["items"]

    # Iterate over results to get the full list
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        artists.extend(results["artists"]["items"])

    # Prepare data for bulk insert
    artists_to_insert = [
        (
            item["id"],
            item["name"],
            item["popularity"],
            item["followers"]["total"],
            item["genres"],
            " ".join(item["genres"]),
            False,  # has_related
            0,  # total_albums
        )
        for item in artists
    ]

    if not artists_to_insert:
        log.info("No artists found to sync.")
    else:
        try:
            insert_query = '''
                INSERT INTO artists (spotify_id, name, popularity, followers, genres, genres_string, has_related, total_albums)
                VALUES %s
                ON CONFLICT (spotify_id) DO NOTHING
                RETURNING spotify_id, name;
            '''
            # One page keeps it a single statement on the autocommit connection,
            # so a failure leaves no half-inserted batch behind.
            newly_inserted_artists = execute_values(
                cursor,
                insert_query,
                artists_to_insert,
                page_size=len(artists_to_insert),
                fetch=True,
            )
            log.info(
                "Processed %s artists. Found %s new artists. %s already existed.",
                len(artists_to_insert),
                len(newly_inserted_artists),
                len(artists_to_insert) - len(newly_inserted_artists),
            )

            # Publish newly inserted artists to RabbitMQ
            for spotify_id, name in newly_inserted_artists:
                log.info("👨🏽‍🎤 Publishing new artist", id=spotify_id)
                channel_albums.basic_publish(
                    exchange="",
                    routing_key=CHANNEL_ALBUMS_NAME,
                    body=json.dumps(
                        {
                            "spotify_id": spotify_id,
                            "total_albums": 0,
                            "name": name,
                        }
                    ),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                )
                channel_related_artists.basic_publish(
                    exchange="",
                    routing_key=CHANNEL_RELATED_ARTISTS_NAME,
                    body=json.dumps({"spotify_id": spotify_id, "name": name}),
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ),
                )

        except Exception as e:
            log.exception(
                "Unhandled exception during bulk artist insert",
                exception=e,
                exc_info=True,
            )

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
