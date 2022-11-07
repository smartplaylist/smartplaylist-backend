from datetime import datetime
from datetime import timezone
import json
import os
import sys

from imports.logging import get_logger
import imports.broker as broker
import imports.db as db

READING_QUEUE_NAME = "tracks_to_have_tags_updated"

log = get_logger(os.path.basename(__file__))


def compute_tags(data):
    tags = (
        data["artist_genres"]
        + data["artist_lastfm_tags"]
        + data["album_lastfm_tags"]
        + data["track_genres"]
        + data["track_lastfm_tags"]
    )
    result = list(set(tags))
    result.sort(key=str.lower)
    return result


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()

    def get_artist_tags_for_track(id):
        cursor.execute(
            """
            SELECT a.genres, a.lastfm_tags
            FROM tracks AS t, artists AS a
            WHERE t.album_artist_spotify_id=a.spotify_id AND t.spotify_id=%s
            """,
            (id,),
        )
        result = cursor.fetchone()

        if result == None:
            # This artist is not in the database
            return [[], []]

        genres = result[0] if result[0] != None else []
        lastfm_tags = result[1] if result[1] != None else []
        return [genres, lastfm_tags]

    def get_album_tags_for_track(id):
        cursor.execute(
            """
            SELECT a.lastfm_tags FROM tracks AS t, albums AS a
            WHERE t.from_album_spotify_id=a.spotify_id AND t.spotify_id=%s
            """,
            (id,),
        )
        result = cursor.fetchone()

        if result == None:
            # This album is not in the database
            return [[]]

        lastfm_tags = result[0] if result[0] != None else []
        return [lastfm_tags]

    def get_track_tags(id):
        cursor.execute(
            """
            SELECT t.genres, t.lastfm_tags
            FROM tracks AS t
            WHERE t.spotify_id=%s
            """,
            (id,),
        )
        result = cursor.fetchone()

        if result == None:
            # This track is not in the database 🤔
            return [[], []]

        genres = result[0] if result[0] != None else []
        lastfm_tags = result[1] if result[1] != None else []
        return [genres, lastfm_tags]

    def get_relevant_tags(id):
        tags = {}
        artist_tags = get_artist_tags_for_track(id)
        album_tags = get_album_tags_for_track(id)
        track_tags = get_track_tags(id)

        tags = {
            "artist_genres": artist_tags[0],
            "artist_lastfm_tags": artist_tags[1],
            "album_lastfm_tags": album_tags[0],
            "track_genres": track_tags[0],
            "track_lastfm_tags": track_tags[1],
        }
        return tags

    def process_track(id):
        relevant_tags = get_relevant_tags(id)
        tags = compute_tags(relevant_tags)

        try:
            cursor.execute(
                """
                UPDATE tracks
                SET
                    computed_genres=%s,
                    computed_genres_string=%s,
                    computed_genres_updated_at=%s
                WHERE spotify_id=%s;
                """,
                (tags, " ".join(tags), datetime.now(timezone.utc), id),
            )
        except Exception as e:
            log.error("Unhandled exception", exc_info=True)
        else:
            log.info("🎧 Updated track's tags", id=id)

    def callback(ch, method, _, body):
        message = json.loads(body.decode())
        id = message["spotify_id"]
        log.info("👨🏽‍🎤 Processing track", id=id)

        process_track(id)

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
