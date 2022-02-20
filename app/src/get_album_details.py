import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import imports.broker as broker
import imports.db as db
import imports.logger as logger

READING_QUEUE_NAME = "albums"
WRITING_QUEUE_NAME = "tracks"


def update_album(cursor, data):
    copyrights = []
    for copyright in data["copyrights"]:
        copyrights.append("%s" % (copyright["text"]))
    cursor.execute(
        "UPDATE albums SET genres=%s, popularity=%s, label=%s, copyrights=%s, updated_at=now() WHERE spotify_id=%s;",
        (
            ", ".join(data["genres"]),
            data["popularity"],
            data["label"],
            ", ".join(copyrights),
            data["id"],
        ),
    )


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = logger.get_logger(os.path.basename(__file__))

    cursor.execute("SELECT spotify_id, genres FROM followed_artists")
    artist_genres = {
        artist_genre[0]: artist_genre[1] for artist_genre in cursor.fetchall()
    }

    def callback(ch, method, properties, body):

        id = body.decode()
        # Iterate over results to get the full list
        result = sp.album(album_id=id)
        update_album(cursor, result)

        tracks = result["tracks"]["items"]
        album_release_date = result["release_date"]

        for i, item in enumerate(tracks):
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])

            genres = []
            if item["artists"] and item["artists"][0]["id"] in artist_genres:
                genres = artist_genres[item["artists"][0]["id"]]

            try:
                cursor.execute(
                    "INSERT INTO tracks (spotify_id, name, main_artist, all_artists, release_date, genres, track_number, disc_number, duration_ms, explicit, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now());",
                    (
                        item["id"],
                        item["name"],
                        artists[0],
                        artists,
                        album_release_date,
                        genres,
                        item["track_number"],
                        item["disc_number"],
                        item["duration_ms"],
                        item["explicit"],
                    ),
                )
            except Exception as e:
                log.error("id: %s (%s)" % (item["id"], str(e).replace("\n", " ")))
            else:
                log.info(f"Saved id: {item['id']}")
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
