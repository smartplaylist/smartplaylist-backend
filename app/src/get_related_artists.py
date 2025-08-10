import json
import os
import sys
import time

import pika
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

# Add api/src to the path to be able to import from `lib`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api", "src")))

from lib.engine import get_sessionmaker
from models.artist import Artist
from imports.decorators import api_attempts
from imports.logging import get_logger
from imports.spotipy import sp
import imports.broker as broker

CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
CHANNEL_ALBUMS_NAME = "artists"

log = get_logger(os.path.basename(__file__))

@api_attempts
def get_related_artists(artist_id):
    return sp.artist_related_artists(artist_id)

def get_session():
    """Gets a new SQLAlchemy session."""
    engine_sessionmaker = get_sessionmaker()
    return engine_sessionmaker()

def process_message(session, channel_albums, message_body):
    """Processes a single message from the queue."""
    message = json.loads(message_body.decode())
    artist_id = message["spotify_id"]
    artist_name = message["name"]

    related_artists_data = get_related_artists(artist_id)

    if not related_artists_data or not related_artists_data.get("artists"):
        log.warning("🤷🏽 Unable to get artist's related artists", id=artist_id)
        return

    new_artists_to_publish = []

    with session.begin():
        for item in related_artists_data["artists"]:
            insert_stmt = insert(Artist).values(
                spotify_id=item["id"],
                name=item["name"],
                popularity=item["popularity"],
                followers=item["followers"]["total"],
                genres=item["genres"],
                genres_string=" ".join(item["genres"]),
                related_to_spotify_id=artist_id,
                related_to=artist_name,
                has_related=False,
                total_albums=0,
            ).on_conflict_do_nothing(
                index_elements=['spotify_id']
            )
            result = session.execute(insert_stmt)

            if result.rowcount:
                log.info("👨🏽‍🎤 Artist saved", id=item["id"])
                new_artists_to_publish.append({
                    "spotify_id": item["id"],
                    "total_albums": 0,
                    "name": item["name"],
                })
            else:
                log.info("👨🏽‍🎤 Artist exists", id=item["id"])

        # Update the original artist to mark that we have processed its related artists
        session.query(Artist).filter(Artist.spotify_id == artist_id).update({"has_related": True})
        log.info("👨🏽‍🎤 Artist's has_related updated", id=artist_id)

    # Publish messages for newly added artists outside the transaction
    for new_artist in new_artists_to_publish:
        channel_albums.basic_publish(
            exchange="",
            routing_key=CHANNEL_ALBUMS_NAME,
            body=json.dumps(new_artist),
            properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
        )
        log.info("👨🏽‍🎤 Published new artist to albums queue", id=new_artist["spotify_id"])


def main():
    """Main loop for the worker."""
    while True:
        try:
            broker_conn = broker.get_broker_connection()
            consume_channel = broker.create_channel(broker_conn, CHANNEL_RELATED_ARTISTS_NAME)
            channel_albums = broker.create_channel(broker_conn, CHANNEL_ALBUMS_NAME)

            consume_channel.basic_qos(prefetch_count=1)

            db_session = get_session()

            log.info("[*] Waiting for messages. To exit press CTRL+C")

            for method_frame, properties, body in consume_channel.consume(CHANNEL_RELATED_ARTISTS_NAME):
                try:
                    process_message(db_session, channel_albums, body)
                except Exception as e:
                    log.exception("Unhandled exception while processing message", exc_info=e)
                    # Negative acknowledgement to requeue the message or send to dead-letter-queue
                    # For now, we will not requeue to avoid poison pill messages.
                    consume_channel.basic_nack(method_frame.delivery_tag, requeue=False)
                else:
                    # Acknowledge the message
                    consume_channel.basic_ack(method_frame.delivery_tag)

        except pika.exceptions.AMQPConnectionError as e:
            log.error("Connection to RabbitMQ failed. Retrying in 5 seconds...", error=e)
            time.sleep(5)
        except Exception as e:
            log.exception("An unhandled error occurred in the main loop.", exc_info=True)
            # A more robust solution might have more specific error handling
            # or a limited number of retries.
            time.sleep(10)
        finally:
            if 'db_session' in locals() and db_session.is_active:
                db_session.close()
            if 'broker_conn' in locals() and broker_conn.is_open:
                broker_conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
