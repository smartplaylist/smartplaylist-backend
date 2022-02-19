import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import imports.broker as broker
import imports.db as db
import imports.logger as logger

SPOTIFY_MARKET = os.environ["SPOTIFY_MARKET"]

READING_QUEUE_NAME = "artists"
WRITING_QUEUE_NAME = "albums"


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = logger.get_logger(os.path.basename(__file__))

    def callback(ch, method, properties, body):
        id = body.decode()
        # Iterate over results to get the full list
        results = sp.artist_albums(artist_id=id, limit=50, country=SPOTIFY_MARKET)
        items = results["items"]
        while results["next"]:
            results = sp.next(results)
            items.extend(results["items"])

        # Remove albums that were released before 2021
        items = filter(
            lambda x: x["release_date"] >= "2021" and x["album_type"] != "compilation",
            items,
        )

        for i, item in enumerate(items):
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])
            try:
                cursor.execute(
                    "INSERT INTO albums (spotify_id, name, main_artist, all_artists, album_group, album_type, release_date, release_date_precision, total_tracks, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now());",
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
