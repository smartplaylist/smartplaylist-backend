import os
import sys
import pika
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import imports.broker as broker
import imports.db as db


QUEUE_NAME = "artists"


def main():
    broker_connection, channel = broker.create_channel(QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    def callback(ch, method, properties, body):
        print(method)
        id = body.decode()
        # Iterate over results to get the full list
        results = sp.artist_albums(artist_id=id, limit=50)
        items = results["items"]
        while results["next"]:
            results = sp.next(results)
            items.extend(results["items"])

        for i, item in enumerate(items):
            artists = []
            for artist in item["artists"]:
                artists.append("%s: %s" % (artist["name"], artist["type"]))
            try:
                cursor.execute(
                    "INSERT INTO albums (spotify_id, name, artists, album_group, album_type, release_date, release_date_precision, total_tracks, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now());",
                    (
                        item["id"],
                        item["name"],
                        ", ".join(artists),
                        item["album_group"],
                        item["album_type"],
                        item["release_date"],
                        item["release_date_precision"],
                        item["total_tracks"],
                    ),
                )
                # print("Saved ", i, item["name"], artists)
            except Exception as e:
                print("💽 skipped ", i, item["name"], artists, e)

        ch.basic_ack(method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_message_callback=callback, queue=QUEUE_NAME)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

    # Clean up and close connections
    broker.close_connection(broker_connection)
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
