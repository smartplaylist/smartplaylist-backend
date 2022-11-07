import json
import os
import sys

from imports.logging import get_logger
import imports.broker as broker
import imports.db as db
import pika

WRITING_QUEUE_NAME = "tracks_to_have_tags_updated"
COMPUTE_TAGS_DAILY = os.getenv("COMPUTE_TAGS_DAILY", 100_000)

log = get_logger(os.path.basename(__file__))


def main():
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    print(f"Adding tracks to {WRITING_QUEUE_NAME} Queue.")

    cursor.execute(
        """
        SELECT spotify_id
        FROM tracks
        WHERE lastfm_tags_string != ''
        ORDER BY computed_genres_updated_at ASC NULLS FIRST, created_at DESC
        LIMIT %s;
        """,
        (COMPUTE_TAGS_DAILY,),
    )
    tracks = cursor.fetchall()

    for item in tracks:
        log.info("💿 Track added to the queue", id=item[0])

        publish_channel.basic_publish(
            exchange="",
            routing_key=WRITING_QUEUE_NAME,
            body=json.dumps({"spotify_id": item[0]}),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )

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
