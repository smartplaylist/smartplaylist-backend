import os
import sys

import psycopg2.errors
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from structlog import get_logger

import imports.broker as broker
import imports.db as db

READING_QUEUE_NAME = "albums"
WRITING_QUEUE_NAME = "tracks"


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
                    # TODO: Save copyrights as an array (change database structure)
                    ", ".join(copyrights),
                    data["id"],
                ),
            )
        except Exception as e:
            log.error("Unhandled exception", exc_info=True)
        else:
            log.info(
                "💿 Album's details updated",
                id=data["id"],
            )

    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = get_logger(os.path.basename(__file__))

    # Build artist data array to add it to the tracks
    cursor.execute("SELECT name, genres, popularity, followers FROM artists")
    artist_data = {
        artist_data[0]: [artist_data[1], artist_data[2], artist_data[3]]
        for artist_data in cursor.fetchall()
    }

    def callback(ch, method, properties, body):

        album_id = body.decode()
        result = sp.album(album_id=album_id)
        update_album(cursor, result)

        tracks = result["tracks"]["items"]
        album_release_date = result["release_date"]

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
                    "INSERT INTO tracks (spotify_id, name, main_artist, main_artist_popularity, main_artist_followers, all_artists, all_artists_string, release_date, genres, genres_string, track_number, disc_number, duration_ms, explicit, preview_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        item["id"],
                        item["name"],
                        artists[0],
                        main_artist_popularity,
                        main_artist_followers,
                        artists,
                        " ".join(artists),
                        album_release_date,
                        genres,
                        " ".join(genres),
                        item["track_number"],
                        item["disc_number"],
                        item["duration_ms"],
                        item["explicit"],
                        item["preview_url"],
                    ),
                )
            except psycopg2.errors.UniqueViolation as e:
                log.info(
                    "🎧 Track exists",
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
                    "🎧 Track saved",
                    id=item["id"],
                    name=item["name"],
                    main_artist=artists[0],
                    number=i + 1,
                    status="saved",
                )
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
