import json
import os
import sys

from imports.decorators import api_attempts
from imports.logging import get_logger
from imports.spotipy import sp
import imports.broker as broker
import imports.db as db
import pika

READING_QUEUE_NAME = "albums"
WRITING_QUEUE_NAME = "tracks"

log = get_logger(os.path.basename(__file__))


@api_attempts
def get_albums_details(id):
    return sp.album(id)


def main():
    def update_album(cursor, data):
        copyrights = []

        for copyright in data["copyrights"]:
            copyrights.append(copyright["text"])
        try:
            cursor.execute(
                "UPDATE albums SET popularity=%s, label=%s, copyrights=%s WHERE spotify_id=%s;",
                (
                    data["popularity"],
                    data["label"],
                    copyrights,
                    data["id"],
                ),
            )
        except Exception as e:
            log.error("Unhandled exception", exception=e, exc_info=True)
        else:
            log.info("💿 Album's details updated", id=data["id"])

    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    # Build artist data array to add it to the tracks
    cursor.execute("SELECT name, genres, popularity, followers FROM artists")
    artist_data = {
        artist_data[0]: [artist_data[1], artist_data[2], artist_data[3]]
        for artist_data in cursor.fetchall()
    }

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        album_id = message["spotify_id"]
        album_name = message["album_name"]
        album_artist = message["album_artist"]
        album_artist_spotify_id = message["album_artist_spotify_id"]

        log.info("💿 Processing album", id=album_id)

        result = {}
        result = get_albums_details(album_id)

        if result == {}:
            log.warning("🤷🏽 Unable to get album details", id=album_id)
            ch.basic_ack(method.delivery_tag)
            return

        update_album(cursor, result)

        tracks = result["tracks"]["items"]
        album_release_date = result["release_date"]
        if len(album_release_date) == 4:
            if "0000" == album_release_date:
                album_release_date = "0001"
            album_release_date += "-01-01"
        elif len(album_release_date) == 7:
            album_release_date += "-01"

        for i, item in enumerate(tracks):
            artists = []
            genres = []
            main_artist_popularity = None
            main_artist_followers = None

            for artist in item["artists"]:
                artists.append(artist["name"])

                # We use data of the last artist from the track, that exists in `artists` table
                # We should either grab that data from Spotify
                # TODO: or take the maximum from artists we have (the most popular is the most importatnt)
                if artist["name"] in artist_data:
                    genres.extend(artist_data[artist["name"]][0])
                    main_artist_popularity = artist_data[artist["name"]][1]
                    main_artist_followers = artist_data[artist["name"]][2]

            genres = list(set(genres))

            try:
                cursor.execute(
                    "INSERT INTO tracks (spotify_id, name, name_fts_string, main_artist, main_artist_popularity, main_artist_followers, all_artists, all_artists_string, release_date, genres, genres_string, track_number, disc_number, duration_ms, explicit, preview_url, from_album, from_album_spotify_id, album_artist, album_artist_spotify_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                    (
                        item["id"],
                        item["name"],
                        item["name"].lower(),
                        artists[0],
                        main_artist_popularity,
                        main_artist_followers,
                        artists,
                        " ".join(artists).lower(),
                        album_release_date,
                        genres,
                        " ".join(genres).lower(),
                        item["track_number"],
                        item["disc_number"],
                        item["duration_ms"],
                        item["explicit"],
                        item["preview_url"],
                        album_name,
                        album_id,
                        album_artist,
                        album_artist_spotify_id,
                    ),
                )
            except Exception as e:
                log.exception("Unhandled exception", exception=e, exc_info=True)
            else:
                log.info(
                    "🎧 Track " + ("saved" if cursor.rowcount else "exists"),
                    id=item["id"],
                )
                # Publish to queue only if it was added (which means it was not in the db yet)
                if cursor.rowcount:
                    publish_channel.basic_publish(
                        exchange="",
                        routing_key=WRITING_QUEUE_NAME,
                        body=item["id"],
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
