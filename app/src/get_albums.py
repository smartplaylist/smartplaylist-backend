from datetime import datetime, timezone
import json
import os
import sys

import pika

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger

# import imports.requests

SPOTIFY_MARKET = os.environ["SPOTIFY_MARKET"]
READING_QUEUE_NAME = "artists"
WRITING_QUEUE_NAME = "albums"
MAX_RETRY_ATTEMPTS = 10

log = get_logger(os.path.basename(__file__))


def filter_album(album):
    return (
        album["release_date"] >= "2021"
        and album["album_type"] != "compilation"
        and album["artists"][0]["name"] != "Various Artists"
    )


def update_total_albums(artist_id, results, cursor):
    """Update total albums for the current artist
    Even though we might not store all those albums
    It is used for determining if there are new releases in Spotify's database"""

    try:
        cursor.execute(
            "UPDATE artists SET total_albums=%s, albums_updated_at=%s WHERE spotify_id=%s;",
            (results["total"], datetime.now(timezone.utc), artist_id),
        )
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info(
            "👨🏽‍🎤 Updated total albums",
            spotify_id=artist_id,
            total_albums=results["total"],
            object="artist",
        )


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    def callback(ch, method, properties, body):
        """Handle received artist's data from the queue"""

        message = json.loads(body.decode())
        artist_id = message["spotify_id"]
        total_albums = message["total_albums"]
        artist_name = message["name"]

        log.info(
            "👨🏽‍🎤 Processing",
            name=artist_name,
            spotify_id=message["spotify_id"],
            object="artist",
        )

        attempts = 0
        while attempts < MAX_RETRY_ATTEMPTS:
            try:
                results = sp.artist_albums(
                    artist_id=artist_id,
                    album_type="album,single,appears_on",
                    offset=0,
                    limit=50,
                    country=SPOTIFY_MARKET,
                )
                log.info("⚡️ Trying API request", attempt=attempts)
                break
            except Exception as e:
                attempts += 1
                log.exception(
                    "Unhandled exception", exception=e, attempt=attempts, exc_info=True
                )

        # Update `albums_updated_at` even if no new albums where added
        update_total_albums(artist_id, results, cursor)

        if total_albums >= results["total"]:
            log.info("👨🏽‍🎤 No new albums", spotify_id=artist_id, object="artist")
            ch.basic_ack(method.delivery_tag)
            return

        new_albums = results["total"] - total_albums

        log.info(
            "👨🏽‍🎤 New releases",
            spotify_id=artist_id,
            albums_count=new_albums,
            object="artist",
        )

        # We need to do make several requests since data is sorted by albumy type
        # and then by the release date
        # An option would be to do separate requestes for `albums` and `singles`
        items = results["items"]
        while results["next"]:

            attempts = 0
            # attemps hack because API is returning random 404 errors
            while attempts < MAX_RETRY_ATTEMPTS:
                try:
                    results = sp.next(results)
                    log.info("Trying API request", attempt=attempts)
                    break
                except Exception as e:
                    attempts += 1
                    log.exception(
                        "Unhandled exception",
                        exception=e,
                        attempt=attempts,
                        exc_info=True,
                    )

            items.extend(results["items"])

        # TODO: Why not sort results by release date and only add those newest
        # This will not add older realeases that were added by Spotify between 2021
        # checking new releases
        for i, item in enumerate(items):
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])
            release_date = item["release_date"]
            if "0000" == release_date:
                release_date = "0001"

            if item["release_date_precision"] == "year":
                release_date += "-01-01"
            elif item["release_date_precision"] == "month":
                release_date += "-01"

            try:
                cursor.execute(
                    "INSERT INTO albums (spotify_id, name, main_artist, all_artists, from_discography_of, album_group, album_type, release_date, release_date_precision, total_tracks, from_discography_of_spotify_id, main_artist_spotify_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                    (
                        item["id"],
                        item["name"],
                        artists[0],
                        artists,
                        artist_name,
                        item["album_group"],
                        item["album_type"],
                        release_date,
                        item["release_date_precision"],
                        item["total_tracks"],
                        artist_id,
                        item["artists"][0]["id"],
                    ),
                )
            except Exception as e:
                log.exception("Unhandled exception", exception=e, exc_info=True)
            else:
                log.info(
                    "💿 Album " + ("saved" if cursor.rowcount else "exists"),
                    spotify_id=item["id"],
                    name=item["name"],
                    main_artist=artists[0],
                    object="album",
                )

                # Publish to queue only if it was added (which means it was not in the db yet)
                if cursor.rowcount:
                    # Only publish (to get details) for albums that pass the test
                    # Should this be here? Where should I filter this?
                    if filter_album(item):
                        publish_channel.basic_publish(
                            exchange="",
                            routing_key=WRITING_QUEUE_NAME,
                            body=json.dumps(
                                {
                                    "spotify_id": item["id"],
                                    "album_name": item["name"],
                                    "album_artist": artists[0],
                                    "album_artist_spotify_id": item["artists"][0]["id"],
                                }
                            ),
                            properties=pika.BasicProperties(
                                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                            ),
                        )

        ch.basic_ack(method.delivery_tag)

    consume_channel.basic_qos(prefetch_count=1)
    consume_channel.basic_consume(
        on_message_callback=callback, queue=READING_QUEUE_NAME
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    consume_channel.start_consuming()

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
