"""
after: dba07ebc55fe
after_name: (Add sum_of_followers_to_tracks)
Updates 'tracks.sum_of_artists_followers' column with proper sum
"""

from math import ceil
import os
import sys

from imports.custom_decorators import handle_exceptions
from imports.logging import get_logger
import imports.db as db

WRITING_QUEUE_NAME = "tracks"
ITERATION_SIZE = int(os.environ.get("TRACKS_UPDATE_ITERATION_SIZE", 10_000))

log = get_logger(os.path.basename(__file__))


def main():
    db_connection, cursor = db.init_connection()

    def get_artist_data():
        # Build artist data array to add it to the tracks
        cursor.execute("SELECT name, popularity, followers FROM artists")
        return {
            artist_data[0]: {"popularity": artist_data[1], "followers": artist_data[2]}
            for artist_data in cursor.fetchall()
        }

    # Get total number of tracks to be processed
    cursor.execute("SELECT count(*) FROM tracks WHERE sum_of_artists_followers=-1")
    count = cursor.fetchone()
    count = count[0]

    artist_data = get_artist_data()
    max = ceil(count / ITERATION_SIZE)

    for i in range(max):
        print("Progress:", i + 1, "/", max)
        cursor.execute(
            f"SELECT spotify_id, all_artists FROM tracks WHERE sum_of_artists_followers=-1 LIMIT {ITERATION_SIZE}"
        )
        tracks = cursor.fetchall()

        for track in tracks:
            sum_of_artists_followers = 0
            sum_of_artists_popularity = 0
            artists = track[1]

            for artist in artists:
                if artist in artist_data:
                    sum_of_artists_followers += artist_data[artist]["followers"]
                    sum_of_artists_popularity += artist_data[artist]["popularity"]

            average_artists_popularity = ceil(sum_of_artists_popularity / len(artists))

            @handle_exceptions
            def update_track_stats():
                cursor.execute(
                    f"""
                    UPDATE
                        tracks
                    SET
                        sum_of_artists_followers={sum_of_artists_followers},
                        average_artists_popularity={average_artists_popularity}
                    WHERE
                        spotify_id='{track[0]}'
                    """
                )

            update_track_stats()

    # Clean up and close connections
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
