import json
from math import ceil
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
PREFETCH_COUNT = 20

log = get_logger(os.path.basename(__file__))


@api_attempts
def get_albums_details(ids):
    return sp.albums(ids)


def normalize_release_date(date):
    if len(date) == 4:
        if "0000" == date:
            date = "0001"
        date += "-01-01"
    elif 7 == len(date):
        date += "-01"
    return date


# def get_track_genres(track, artists):
#     genres = []
#     for artist in track["artists"]:
#         if artist["name"] in artists:
#             genres.extend(artists[artist["name"]][0])

#     return genres


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    def get_artist_data():
        # Build artist data array to add it to the tracks
        cursor.execute("SELECT name, genres, popularity, followers FROM artists")
        return {
            artist_data[0]: [artist_data[1], artist_data[2], artist_data[3]]
            for artist_data in cursor.fetchall()
        }

    def publish_to_broker(data):
        publish_channel.basic_publish(
            exchange="",
            routing_key=WRITING_QUEUE_NAME,
            body=data,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    def update_album(data):
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

    artist_data = get_artist_data()
    messages = []

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        message["delivery_tag"] = method.delivery_tag

        messages.append(message)

        if len(messages) >= PREFETCH_COUNT:
            log.info(f"💿 Processing {PREFETCH_COUNT} messages")

            ids = [i["spotify_id"] for i in messages]

            result = get_albums_details(ids)
            albums = result["albums"]

            for i in range(len(messages)):
                album = albums[i]
                message = messages[i]

                log.info("💿 Processing album", id=album["id"])

                if album == {}:
                    log.warning("🤷🏽 Unable to get album details", id=album["id"])
                    ch.basic_ack(message["delivery_tag"])
                    return

                update_album(album)

                release_date = normalize_release_date(album["release_date"])
                tracks = album["tracks"]["items"]

                for track in tracks:
                    artists = [artist["name"] for artist in track["artists"]]
                    # genres = get_track_genres(track, artists)
                    genres = []
                    main_artist_popularity = None
                    main_artist_followers = None
                    sum_of_artists_followers = 0
                    sum_of_artists_popularity = 0
                    average_artists_popularity = 0

                    for artist in track["artists"]:
                        # TODO: or take the maximum from artists we have (the most popular is the most importatnt)
                        if artist["name"] in artist_data:
                            genres.extend(artist_data[artist["name"]][0])
                            # Set popularity of the first available artist
                            if main_artist_popularity == None:
                                main_artist_popularity = artist_data[artist["name"]][1]
                            # Set followers of the first available artist
                            if main_artist_followers == None:
                                main_artist_followers = artist_data[artist["name"]][2]

                            sum_of_artists_popularity += artist_data[artist["name"]][1]
                            sum_of_artists_followers += artist_data[artist["name"]][2]

                    average_artists_popularity = ceil(
                        sum_of_artists_popularity / len(track["artists"])
                    )

                    genres = list(set(genres))

                    try:
                        cursor.execute(
                            """
                            INSERT INTO tracks
                                (spotify_id, name, name_fts_string, main_artist, main_artist_popularity, main_artist_followers, all_artists, all_artists_string, release_date, genres, genres_string, track_number, disc_number, duration_ms, explicit, preview_url, from_album, from_album_spotify_id, album_artist, album_artist_spotify_id, sum_of_artists_followers, average_artists_popularity)
                            VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING;""",
                            (
                                track["id"],
                                track["name"],
                                track["name"].lower(),
                                artists[0],
                                main_artist_popularity,
                                main_artist_followers,
                                artists,
                                " ".join(artists).lower(),
                                release_date,
                                genres,
                                " ".join(genres).lower(),
                                track["track_number"],
                                track["disc_number"],
                                track["duration_ms"],
                                track["explicit"],
                                track["preview_url"],
                                album["name"],
                                album["id"],
                                album["artists"][0]["name"],
                                album["artists"][0]["id"],
                                sum_of_artists_followers,
                                average_artists_popularity,
                            ),
                        )
                    except Exception as e:
                        log.exception("Unhandled exception", exception=e, exc_info=True)
                    else:
                        log.info(
                            "🎧 Track " + ("saved" if cursor.rowcount else "exists"),
                            id=track["id"],
                        )

                        # Publish to queue only if it was added (which means it was not in the db yet)
                        if cursor.rowcount:
                            publish_to_broker(track["id"])

                ch.basic_ack(message["delivery_tag"])

            messages.clear()

    consume_channel.basic_qos(prefetch_count=PREFETCH_COUNT)
    consume_channel.basic_consume(
        on_message_callback=callback, queue=READING_QUEUE_NAME
    )

    print(
        f' [*] Waiting for messages in "{READING_QUEUE_NAME}" queue. To exit press CTRL+C'
    )
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
