from distutils.log import info
import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import imports.broker as broker
import imports.db as db
import imports.logger as logger


READING_QUEUE_NAME = "tracks"


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = logger.get_logger(os.path.basename(__file__))

    def callback(ch, method, properties, body):
        id = body.decode()
        # Iterate over results to get the full list
        result = sp.track(track_id=id)
        track_popularity = result["popularity"]
        track_name = result["name"]

        result = sp.audio_features(tracks=[id])

        if not result or result[0] is None:
            log.info(f"Track's {id} audio_features() didn't return any results")
            ch.basic_ack(method.delivery_tag)
            return

        for item in result:
            try:
                cursor.execute(
                    "UPDATE tracks SET popularity=%s, updated_at=now() WHERE spotify_id=%s;",
                    (
                        track_popularity,
                        id,
                    ),
                )

            except Exception as e:
                log.error("id: %s (%s)" % (item["id"], str(e).replace("\n", " ")))
            else:
                log.info(f"Updated id: {id}")

        # dorobienie migracji
        # zapisanie informacji pobranych przez audio_features
        # pobranie tablicy genres z artystów
        # lepsze formatowaine artists w albumach i trackach (json? {artists:["faze miyaki", "sudoo"]})

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
