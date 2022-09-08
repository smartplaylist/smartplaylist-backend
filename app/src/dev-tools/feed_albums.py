import datetime
import json
import os
import sys

import pika

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger

WRITING_QUEUE_NAME = "albums_feed_test"

log = get_logger(os.path.basename(__file__))


def filter_album(album):
    return (
        album[4] >= datetime.date(2021, 1, 1)
        and album[5] != "compilation"
        and album[6] != "Various Artists"
    )


def main():
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    cursor.execute(
        "SELECT spotify_id, name, main_artist, main_artist_spotify_id, release_date, album_type, main_artist FROM albums"
    )
    albums = cursor.fetchall()

    for item in albums:
        # log.info("💿 Album added to the queue", spotify_id=item[0], album_name=item[1])

        if filter_album(item):
            publish_channel.basic_publish(
                exchange="",
                routing_key=WRITING_QUEUE_NAME,
                body=json.dumps(
                    {
                        "spotify_id": item[0],
                        "album_name": item[1],
                        "album_artist": item[2],
                        "album_artist_spotify_id": item[3],
                    }
                ),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

    print(f"Adding albums to {WRITING_QUEUE_NAME} Queue.")

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
