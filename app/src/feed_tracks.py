import datetime
import json
import os
import sys

import pika

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger

WRITING_QUEUE_NAME = "tracks"

log = get_logger(os.path.basename(__file__))


def main():
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    cursor.execute("SELECT spotify_id FROM tracks WHERE energy IS NULL")
    tracks = cursor.fetchall()

    for item in tracks:
        publish_channel.basic_publish(
            exchange="",
            routing_key=WRITING_QUEUE_NAME,
            body=item[0],
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

    print(f"Adding tracks to {WRITING_QUEUE_NAME} Queue.")

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
