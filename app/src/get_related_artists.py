import json
import os
import sys

from imports.decorators import api_attempts
from imports.logging import get_logger
from imports.spotipy import sp
import imports.broker as broker
import imports.db as db
import pika

CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
CHANNEL_ALBUMS_NAME = "artists"

log = get_logger(os.path.basename(__file__))


@api_attempts
def get_related_artists(id):
    return sp.artist_related_artists(id)


def main():
    consume_channel = broker.create_channel(CHANNEL_RELATED_ARTISTS_NAME)
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    db_connection, cursor = db.init_connection()

    def update_artist(spotify_id):
        try:
            cursor.execute(
                "UPDATE artists SET has_related=%s WHERE spotify_id=%s;",
                (True, spotify_id),
            )
        except Exception as e:
            log.error("Unhandled exception", exc_info=True)
        else:
            log.info("👨🏽‍🎤 Artist's has_related updated", id=spotify_id)

    def callback(ch, method, _, body):
        message = json.loads(body.decode())
        id = message["spotify_id"]
        name = message["name"]

        result = {}
        result = get_related_artists(id)

        if result == {}:
            log.warning("🤷🏽 Unable to get artist's related artists", id=id)
            ch.basic_ack(method.delivery_tag)
            return

        for _, item in enumerate(result["artists"]):
            try:
                cursor.execute(
                    "INSERT INTO artists (spotify_id, name, popularity, followers, genres, genres_string, related_to_spotify_id, related_to, has_related, total_albums) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0) ON CONFLICT DO NOTHING;",
                    (
                        item["id"],
                        item["name"],
                        item["popularity"],
                        item["followers"]["total"],
                        item["genres"],
                        " ".join(item["genres"]),
                        id,
                        name,
                        False,
                    ),
                )
            except Exception as e:
                log.exception("Unhandled exception", exception=e)
            else:
                log.info(
                    "👨🏽‍🎤 Artist " + ("saved" if cursor.rowcount else "exists"),
                    id=item["id"],
                )

                # Only publish if it was added
                if cursor.rowcount:
                    channel_albums.basic_publish(
                        exchange="",
                        routing_key=CHANNEL_ALBUMS_NAME,
                        body=json.dumps(
                            {
                                "spotify_id": item["id"],
                                "total_albums": 0,
                                "name": item["name"],
                            }
                        ),
                        properties=pika.BasicProperties(
                            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                        ),
                    )

        update_artist(id)
        ch.basic_ack(method.delivery_tag)

    consume_channel.basic_qos(prefetch_count=1)
    consume_channel.basic_consume(
        on_message_callback=callback, queue=CHANNEL_RELATED_ARTISTS_NAME
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
