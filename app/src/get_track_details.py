import math
import os
import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import imports.broker as broker
import imports.db as db
from imports.logging import get_logger

READING_QUEUE_NAME = "tracks"
PREFETCH_COUNT = 50

log = get_logger(os.path.basename(__file__))


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(),
        retries=3,
        status_retries=3,
        backoff_factor=0.3,
    )

    messages = {}

    def callback(ch, method, properties, body):

        track_id = body.decode()
        messages[track_id] = method.delivery_tag

        # Process PREFETCH_COUNT messages at once
        if len(messages) >= PREFETCH_COUNT:
            log.info(
                "🔉 Processing %s messages" % PREFETCH_COUNT,
            )

            tracks = {}

            result_audio_features = sp.audio_features(tracks=messages.keys())
            for i, v in enumerate(result_audio_features):
                if not v or v is None:
                    log.info("🔉 No audio feature data", id=track_id)
                    # We are only interested in tracks that have feature analysis
                    # We skip other tracks
                    continue
                tracks[v["id"]] = v

            result_tracks = sp.tracks(tracks=messages.keys(), market=[])
            for i, v in enumerate(result_tracks["tracks"]):
                if not v["id"] in tracks:
                    tracks[v["id"]] = {"id": v["id"]}
                tracks[v["id"]]["popularity"] = v["popularity"]

            for k, v in tracks.items():
                log.info("🔉 Processing", id=k)

                if not "danceability" in v:
                    log.info(
                        "🔉 Skipping due to no audio_feature data",
                        id=k,
                        status="skipped",
                    )
                    ch.basic_ack(messages[v["id"]])
                    continue

                try:
                    cursor.execute(
                        "UPDATE tracks SET popularity=%s, key=%s, loudness=%s, mode_is_major=%s, danceability=%s, energy=%s, speechiness=%s, acousticness=%s, instrumentalness=%s, liveness=%s, valence=%s, tempo=%s, time_signature=%s, danceability_raw=%s, energy_raw=%s, speechiness_raw=%s, acousticness_raw=%s, instrumentalness_raw=%s, liveness_raw=%s, valence_raw=%s, tempo_raw=%s WHERE spotify_id=%s;",
                        (
                            v["popularity"],
                            v["key"],
                            v["loudness"],
                            (v["mode"] == 1),
                            math.ceil(v["danceability"] * 1000),
                            math.ceil(v["energy"] * 1000),
                            math.ceil(v["speechiness"] * 1000),
                            math.ceil(v["acousticness"] * 1000),
                            math.ceil(v["instrumentalness"] * 1000),
                            math.ceil(v["liveness"] * 1000),
                            math.ceil(v["valence"] * 1000),
                            v["tempo"],
                            v["time_signature"],
                            v["danceability"],
                            v["energy"],
                            v["speechiness"],
                            v["acousticness"],
                            v["instrumentalness"],
                            v["liveness"],
                            v["valence"],
                            v["tempo"],
                            v["id"],
                        ),
                    )
                except Exception as e:
                    log.exception("🔉 Unhandled exception", id=v["id"], status="skipped")
                else:
                    if cursor.rowcount:
                        log.info(
                            "🔉 Track updated",
                            id=v["id"],
                            status="updated",
                        )
                    else:
                        log.info(
                            "🔉 Track not updated (probably not in the database)",
                            id=v["id"],
                            status="skipped",
                        )
                ch.basic_ack(messages[v["id"]])
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
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
