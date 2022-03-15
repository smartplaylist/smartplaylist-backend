from distutils.log import info
import os
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from structlog import get_logger

import imports.broker as broker
import imports.db as db


READING_QUEUE_NAME = "tracks"


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = get_logger(os.path.basename(__file__))

    def callback(ch, method, properties, body):

        track_id = body.decode()

        log.info(
            "🔉 Processing",
            id=track_id,
            status="updated",
        )

        # Iterate over results to get the full list
        result = sp.track(track_id=track_id)
        track_popularity = result["popularity"]

        result_features = sp.audio_features(tracks=[track_id])

        if not result_features or result_features[0] is None:
            log.info("🔉 No data", id=track_id)
            ch.basic_ack(method.delivery_tag)
            return

        for item in result_features:
            try:
                cursor.execute(
                    "UPDATE tracks SET popularity=%s, danceability=%s, energy=%s, key=%s, loudness=%s, mode=%s, speechiness=%s, acousticness=%s, instrumentalness=%s, liveness=%s, valence=%s, tempo=%s, time_signature=%s WHERE spotify_id=%s",
                    (
                        track_popularity,
                        item["danceability"],
                        item["energy"],
                        item["key"],
                        item["loudness"],
                        item["mode"],
                        item["speechiness"],
                        item["acousticness"],
                        item["instrumentalness"],
                        item["liveness"],
                        item["valence"],
                        item["tempo"],
                        item["time_signature"],
                        track_id,
                    ),
                )
            except Exception as e:
                log.exception("Unhandled exception")
            else:
                if cursor.rowcount:
                    log.info(
                        "🔉 Track updated",
                        id=track_id,
                        status="updated",
                    )
                else:
                    log.info(
                        "🔉 Track not updated (probably not in the database)",
                        id=track_id,
                        status="skipped",
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
