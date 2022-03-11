from datetime import date
import json
import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import imports.broker as broker
import imports.db as db
import imports.logger as logger


SPOTIFY_MARKET = os.environ["SPOTIFY_MARKET"]
READING_QUEUE_NAME = "artists"
WRITING_QUEUE_NAME = "albums"


def main():
    consume_channel = broker.create_channel(READING_QUEUE_NAME)
    publish_channel = broker.create_channel(WRITING_QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
    log = logger.get_logger(os.path.basename(__file__))

    def callback(ch, method, properties, body):
        """Handle received artist's id from the queue"""
        message = json.loads(body.decode())
        id = message["spotify_id"]
        total_albums = message["total_albums"]

        results = sp.artist_albums(
            artist_id=id,
            album_type="album,single,appears_on",
            offset=0,
            limit=50,
            country=SPOTIFY_MARKET,
        )

        if total_albums >= results["total"]:
            log.info(f"No new albums for artist: {id}")
            ch.basic_ack(method.delivery_tag)
            return

        log.info(
            "{} new albums for artist: {}".format(results["total"] - total_albums, id)
        )

        # We need to do make several requests since data is sorted by albumy type
        # and then by release date
        # An option would be to do separate requestes for `albums` and `singles`
        items = results["items"]
        while results["next"]:
            results = sp.next(results)
            items.extend(results["items"])

        # Don't filter albums here, since we already requested them
        # Save to DB, and we will filter it later when getting tracks
        # Or filter it before putting it into Rabbit (so get_track_details.py doesn't get that logic)
        # items = filter(
        #     lambda x: x["release_date"] >= "2020",
        #     items,
        # )

        """
        Update total_albums for the artist here?
        What if it breaks while adding albums, and not all are saved, and the next run
        """

        # Update total albums for the current artist
        cursor.execute(
            "UPDATE artists SET total_albums=%s, last_update=%s WHERE spotify_id=%s;",
            (results["total"], date.today(), id),
        )

        for i, item in enumerate(items):
            artists = []
            for artist in item["artists"]:
                artists.append(artist["name"])
            try:
                cursor.execute(
                    "INSERT INTO albums (spotify_id, name, main_artist, all_artists, album_group, album_type, release_date, release_date_precision, total_tracks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        item["id"],
                        item["name"],
                        artists[0],
                        artists,
                        item["album_group"],
                        item["album_type"],
                        item["release_date"],
                        item["release_date_precision"],
                        item["total_tracks"],
                    ),
                )
            except Exception as e:
                # Not error here, but info that the album already exists.
                log.error("id: %s (%s)" % (item["id"], str(e).replace("\n", " ")))
            else:
                log.info(f"Saved id: {item['id']}")
                # Only get details for albums newer and released in 2020
                # Should this be here? Where should I filter this?
                if item["release_date"] >= "2020":
                    publish_channel.basic_publish(
                        exchange="", routing_key=WRITING_QUEUE_NAME, body=item["id"]
                    )

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
