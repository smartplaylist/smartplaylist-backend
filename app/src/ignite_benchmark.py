import imports.db as db
from pyignite import Client

BENCHMARK_QUERY = """
SELECT
    spotify_id,
    all_artists,
    name,
    genres,
    release_date,
    tempo,
    popularity,
    danceability,
    energy,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    main_artist_popularity,
    main_artist_followers,
    key,
    preview_url
FROM
    tracks
WHERE
    (
    name LIKE '%a%'
    OR all_artists LIKE '%c%'
    )
    AND (genres LIKE '%o%')
    AND tempo >= '80'
    AND tempo <= '210'
    AND popularity >= '0'
    AND popularity <= '100'
    AND main_artist_popularity >= '1'
    AND main_artist_popularity <= '100'
    AND main_artist_followers >= '1'
    AND main_artist_followers <= '50000000'
    AND danceability >= '0'
    AND danceability <= '100'
    AND energy >= '0'
    AND energy <= '100'
    AND speechiness >= '0'
    AND speechiness <= '100'
    AND acousticness >= '0'
    AND acousticness <= '100'
    AND instrumentalness >= '0'
    AND instrumentalness <= '100'
    AND liveness >= '0'
    AND liveness <= '100'
    AND valence >= '0'
    AND valence <= '100'
    AND release_date >= '2021-03-04'
    AND key = '10'
ORDER BY
    release_date DESC,
    popularity DESC,
    spotify_id ASC
LIMIT 10 OFFSET 0;
"""


def main():

    with client.connect("ignite", 10800):
        result = client.sql(BENCHMARK_QUERY)
        for row in result:
            print(row)


if __name__ == "__main__":
    try:
        # db_connection, cursor = db.init_connection()
        client = Client()
        main()
        # db.close_connection(db_connection, cursor)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
