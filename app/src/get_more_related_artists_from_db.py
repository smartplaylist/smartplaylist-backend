import json
import os
import sys

import pika
import psycopg2.errors


import imports.broker as broker
import imports.db as db
from imports.logging import get_logger


CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
CHANNEL_ALBUMS_NAME = "artists"

log = get_logger(os.path.basename(__file__))


def main():
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    db_connection, cursor = db.init_connection()

    # TODO: Not to import same artists over and over again, we have to
    # change the WHERE caluse manually (changing the `created_at` date)
    cursor.execute("SELECT spotify_id, name FROM artists WHERE has_related='0'")
    artist_data = cursor.fetchall()

    for item in artist_data:

        log.info(
            "👨🏽‍🎤 Added related artist to Queue",
            id=item[0],
        )

        channel_albums.basic_publish(
            exchange="",
            routing_key=CHANNEL_RELATED_ARTISTS_NAME,
            body=json.dumps({"spotify_id": item[0], "name": item[1]}),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    print("Adding artists to `related_artists` Queue.")

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
