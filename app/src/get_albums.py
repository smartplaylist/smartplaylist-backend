from datetime import date
import json
import os
import sys

import psycopg2.errors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from structlog import get_logger

import imports.broker as broker
import imports.db as db


SPOTIFY_MARKET = os.environ["SPOTIFY_MARKET"]
READING_QUEUE_NAME = "artists"
WRITING_QUEUE_NAME = "albums"


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = get_logger(os.path.basename(__file__))

    def callback(ch, method, properties, body):
        """Handle received artist's id from the queue"""
        message = json.loads(body.decode())
        id = message["spotify_id"]
        total_albums = message["total_albums"]

        results = sp.artist_albums(
            artist_id=id,
            album_type="album,single,appears_on",
            offset=0,
            limit=50,
            country=SPOTIFY_MARKET,
        )

        if total_albums >= results["total"]:
            log.info("No new albums", id=id)
            ch.basic_ack(method.delivery_tag)
            return

        new_albums = results["total"] - total_albums

        log.info("👨🏽‍🎤 New releases", id=id, albums_count=new_albums)

        # We need to do make several requests since data is sorted by albumy type
        # and then by release date
        # An option would be to do separate requestes for `albums` and `singles`
        items = results["items"]
        while results["next"]:
            results = sp.next(results)
            items.extend(results["items"])

        # Update total albums for the current artist
        # Even though we might not store all those albums
        # It is used for determining if there are new releases in Spotify's database
        try:
            cursor.execute(
                "UPDATE artists SET total_albums=%s, last_update=%s WHERE spotify_id=%s;",
                (results["total"], date.today(), id),
            )
        except Exception as e:
            log.exception("Unhandled exception")
        else:
            log.info(
                "👨🏽‍🎤 Updated total albums",
                id=id,
                total_albums=results["total"],
                prev_total_albums=total_albums,
            )

        for i, item in enumerate(items):
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])
            try:
                cursor.execute(
                    "INSERT INTO albums (spotify_id, name, main_artist, all_artists, album_group, album_type, release_date, release_date_precision, total_tracks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        item["id"],
                        item["name"],
                        artists[0],
                        artists,
                        item["album_group"],
                        item["album_type"],
                        item["release_date"],
                        item["release_date_precision"],
                        item["total_tracks"],
                    ),
                )
            except psycopg2.errors.UniqueViolation as e:
                log.info(
                    "💿 Album exists",
                    id=item["id"],
                    name=item["name"],
                    main_artist=artists[0],
                    number=i + 1,
                    status="skipped",
                )
            except Exception as e:
                log.exception("Unhandled exception")
            else:
                log.info(
                    "💿 Album saved",
                    id=item["id"],
                    name=item["name"],
                    main_artist=artists[0],
                    number=i + 1,
                    status="saved",
                )
                # Only get details for albums newer and released in 2020
                # Should this be here? Where should I filter this?
                if item["release_date"] >= "2020":
                    publish_channel.basic_publish(
                        exchange="", routing_key=WRITING_QUEUE_NAME, body=item["id"]
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
