import math
import os
import sys

from imports.custom_decorators import handle_exceptions
from imports.decorators import api_attempts
from imports.logging import get_logger
from imports.spotipy import sp
import imports.broker as broker
import imports.db as db

READING_QUEUE_NAME = "tracks"
PREFETCH_COUNT = 50
AUDIO_FEATURE_MULTIPLIER = 100

log = get_logger(os.path.basename(__file__))


@api_attempts
def get_audio_features(ids):
    return sp.audio_features(tracks=ids)


@api_attempts
def get_tracks(ids):
    result = sp.tracks(tracks=ids, market=[])
    return result["tracks"]


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    messages = {}

    def callback(ch, method, properties, body):
        track_id = body.decode()
        messages[track_id] = method.delivery_tag

        if len(messages) >= PREFETCH_COUNT:
            log.info(f"🔉 Processing {PREFETCH_COUNT} messages")

            tracks = {}
            ids = list(messages.keys())

            result_audio_features = get_audio_features(ids)

            for i, item in enumerate(result_audio_features):
                # Skip tracks with no audio_feature
                if not item or item is None:
                    log.info("🔉 No audio feature data", id=ids[i])
                    ch.basic_ack(messages[ids[i]])
                    continue
                tracks[item["id"]] = item

            if len(tracks) <= 0:
                messages.clear()
                return

            result_tracks = get_tracks(list(tracks.keys()))

            # Combine tracks data with audio_features data
            for i, item in enumerate(result_tracks):
                tracks[item["id"]]["popularity"] = item["popularity"]

            for i, item in tracks.items():
                log.info("🔉 Processing", id=i)

                @handle_exceptions
                def update_track():
                    cursor.execute(
                        "UPDATE tracks SET popularity=%s, key=%s, loudness=%s, mode_is_major=%s, danceability=%s, energy=%s, speechiness=%s, acousticness=%s, instrumentalness=%s, liveness=%s, valence=%s, tempo=%s, time_signature=%s, danceability_raw=%s, energy_raw=%s, speechiness_raw=%s, acousticness_raw=%s, instrumentalness_raw=%s, liveness_raw=%s, valence_raw=%s, tempo_raw=%s WHERE spotify_id=%s;",
                        (
                            item["popularity"],
                            item["key"],
                            item["loudness"],
                            (item["mode"] == 1),
                            math.ceil(item["danceability"] * AUDIO_FEATURE_MULTIPLIER),
                            math.ceil(item["energy"] * AUDIO_FEATURE_MULTIPLIER),
                            math.ceil(item["speechiness"] * AUDIO_FEATURE_MULTIPLIER),
                            math.ceil(item["acousticness"] * AUDIO_FEATURE_MULTIPLIER),
                            math.ceil(
                                item["instrumentalness"] * AUDIO_FEATURE_MULTIPLIER
                            ),
                            math.ceil(item["liveness"] * AUDIO_FEATURE_MULTIPLIER),
                            math.ceil(item["valence"] * AUDIO_FEATURE_MULTIPLIER),
                            item["tempo"],
                            item["time_signature"],
                            item["danceability"],
                            item["energy"],
                            item["speechiness"],
                            item["acousticness"],
                            item["instrumentalness"],
                            item["liveness"],
                            item["valence"],
                            item["tempo"],
                            item["id"],
                        ),
                    )
                    if cursor.rowcount:
                        log.info("🔉 Track updated", id=item["id"])
                    else:
                        log.info(
                            "🔉 Track not updated (probably not in the database)",
                            id=item["id"],
                        )

                update_track()
                ch.basic_ack(messages[item["id"]])
            messages.clear()

    consume_channel.basic_qos(prefetch_count=PREFETCH_COUNT)
    consume_channel.basic_consume(
        on_message_callback=callback, queue=READING_QUEUE_NAME
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    consume_channel.start_consuming()

    # Clean up and close connections
    broker.close_connection()
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    # Not using a decorator here because it's a control-flow exception
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
