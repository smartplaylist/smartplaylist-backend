from datetime import date
import os
import sys
import redis

sys.path.insert(0, "/app/imports/")

from db import init_connection, close_connection
from redis_om import HashModel
from typing import Optional


LOOP_FETCH_COUNT = 10000

r = redis.Redis(host="db_api_redis", port=6379, db=0)


class Track(HashModel):
    """Redis OM Track model"""

    all_artists_string: str
    name: str
    main_artist_popularity: Optional[int]
    main_artist_followers: Optional[int]
    genres_string: str
    popularity: int
    release_date: date
    danceability: int
    energy: int
    speechiness: int
    acousticness: int
    instrumentalness: int
    liveness: int
    valence: int
    track_key: int

    class Meta:
        database = r


def main():
    db_connection, cursor = init_connection()
    cursor.execute(
        """ SELECT
                all_artists_string,
                name,
                main_artist_popularity,
                main_artist_followers,
                genres_string,
                popularity,
                release_date,
                danceability,
                energy,
                speechiness,
                acousticness,
                instrumentalness,
                liveness,
                valence,
                key,
                spotify_id
            FROM tracks
            WHERE energy IS NOT NULL
            ;
        """
    )

    # Iterate over results in packs of LOOP_FETCH_COUNT size
    while True:
        tracks = cursor.fetchmany(LOOP_FETCH_COUNT)
        if not tracks:
            break

        for n, item in enumerate(tracks):
            track = Track(
                all_artists_string=item[0],
                name=item[1],
                main_artist_popularity=item[2],
                main_artist_followers=item[3],
                genres_string=item[4],
                popularity=item[5],
                release_date=item[6],
                danceability=item[7],
                energy=item[8],
                speechiness=item[9],
                acousticness=item[10],
                instrumentalness=item[11],
                liveness=item[12],
                valence=item[13],
                track_key=item[14],
            )
            res = track.save()
            pass

    close_connection(db_connection, cursor)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
