import json
import os
import sys

import pika
import psycopg2.errors
import requests_cache
from requests_cache import RedisCache
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger


CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
CHANNEL_ALBUMS_NAME = "artists"

log = get_logger(os.path.basename(__file__))
requests_cache.install_cache(
    "grabtrack_redis_cache", RedisCache(host="redis", port=6379)
)


def main():
    def update_artist(spotify_id):
        try:
            cursor.execute(
                "UPDATE artists SET has_related=%s WHERE spotify_id=%s;",
                (
                    True,
                    spotify_id,
                ),
            )
        except Exception as e:
            log.error("Unhandled exception", exc_info=True)
        else:
            log.info(
                "👨🏽‍🎤 Artist's has_related updated",
                spotify_id=spotify_id,
            )

    consume_channel = broker.create_channel(CHANNEL_RELATED_ARTISTS_NAME)
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())

        related_artists = sp.artist_related_artists(message["spotify_id"])

        for i, item in enumerate(related_artists["artists"]):
            try:
                cursor.execute(
                    "INSERT INTO artists (spotify_id, name, popularity, followers, genres, genres_string, related_to_spotify_id, related_to, has_related, total_albums) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0);",
                    (
                        item["id"],
                        item["name"],
                        item["popularity"],
                        item["followers"]["total"],
                        item["genres"],
                        " ".join(item["genres"]),
                        message["spotify_id"],
                        message["name"],
                        False,
                    ),
                )
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

            except psycopg2.errors.UniqueViolation as e:
                log.info(
                    "👨🏽‍🎤 Artist exists",
                    id=item["id"],
                    name=item["name"],
                    status="skipped",
                )
            except Exception as e:
                log.exception("Unhandled exception")
            else:
                log.info(
                    "👨🏽‍🎤 Artist saved",
                    id=item["id"],
                    name=item["name"],
                    status="saved",
                )
        update_artist(message["spotify_id"])
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
