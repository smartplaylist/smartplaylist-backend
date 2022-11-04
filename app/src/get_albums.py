import json
import os
import sys
from datetime import datetime, timezone

import imports.broker as broker
import imports.db as db
import pika
from imports.decorators import api_attempts
from imports.logging import get_logger
from imports.spotipy import sp

SPOTIFY_MARKET = os.environ["SPOTIFY_MARKET"]
READING_QUEUE_NAME = "artists"
WRITING_QUEUE_NAME = "albums"


log = get_logger(os.path.basename(__file__))


def filter_album(album):
    return (
        # album["release_date"] >= "1990" and
        album["album_type"] != "compilation"
        and album["artists"][0]["name"] != "Various Artists"
    )


def update_total_albums(artist_id, result, cursor):
    """Update total albums for the current artist
    Even though we might not store all those albums
    It is used for determining if there are new releases in Spotify's database"""

    try:
        cursor.execute(
            "UPDATE artists SET total_albums=%s, albums_updated_at=%s WHERE spotify_id=%s;",
            (result["total"], datetime.now(timezone.utc), artist_id),
        )
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info(
            "👨🏽‍🎤 Updated total albums",
            id=artist_id,
            total_albums=result["total"],
        )


@api_attempts
def get_artist_albums(id):
    return sp.artist_albums(
        artist_id=id,
        album_type="album,single,appears_on",
        offset=0,
        limit=50,
        country=SPOTIFY_MARKET,
    )


@api_attempts
def get_next(next):
    return sp.next(next)


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    def callback(ch, method, properties, body):
        """Handle received artist's data from the queue"""

        message = json.loads(body.decode())
        artist_id = message["spotify_id"]
        total_albums = message["total_albums"]
        artist_name = message["name"]

        log.info("👨🏽‍🎤 Processing artist", id=message["spotify_id"])

        result = get_artist_albums(artist_id)

        if result == {}:
            log.warning("🤷🏽 Unable to get artist's albums", id=artist_id)
            ch.basic_ack(method.delivery_tag)
            return

        # Update `albums_updated_at` even if no new albums where added
        update_total_albums(artist_id, result, cursor)

        # To grab more (older) albums, we should get rid of that condition
        if total_albums >= result["total"]:
            log.info("👨🏽‍🎤 No new albums", id=artist_id)
            ch.basic_ack(method.delivery_tag)
            return

        new_albums = result["total"] - total_albums
        log.info("👨🏽‍🎤 New releases", id=artist_id, new_albums=new_albums)

        # We need to do make several requests since data is sorted by albumy type
        # and then by the release date
        # An option would be to do separate requestes for `albums` and `singles`
        items = result["items"]
        while result["next"]:
            result = get_next(result)
            items.extend(result["items"])

        # TODO: Why not sort result by release date and only add those newest
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
                log.exception(
                    "Unhandled exception", exception=e, exc_info=True
                )
            else:
                log.info(
                    "💿 Album " + ("saved" if cursor.rowcount else "exists"),
                    id=item["id"],
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
                                    "album_artist_spotify_id": item["artists"][
                                        0
                                    ]["id"],
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
        ## If file exists, delete it ##
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
