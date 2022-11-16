import imports.db as db
from pyignite import Client

TRACK_INSERT = """
    INSERT INTO tracks (
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
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


def create_table():
    CREATE_TRACKS_TABLE = """
        CREATE TABLE IF NOT EXISTS tracks (
            spotify_id VARCHAR PRIMARY KEY,
            all_artists VARCHAR,
            name VARCHAR,
            genres VARCHAR,
            release_date TIMESTAMP,
            tempo SMALLINT,
            popularity TINYINT,
            danceability TINYINT,
            energy TINYINT,
            speechiness TINYINT,
            acousticness TINYINT,
            instrumentalness TINYINT,
            liveness TINYINT,
            valence TINYINT,
            main_artist_popularity TINYINT,
            main_artist_followers INT,
            key TINYINT,
            preview_url VARCHAR
        )
        """
    result = client.sql(CREATE_TRACKS_TABLE)
    return True


def get_tracks():
    cursor.execute(
        """
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
        FROM tracks
        LIMIT 1000000
        """
    )
    return [list(r) for r in cursor.fetchall()]


def main():
    tracks = get_tracks()
    for track in tracks:
        track[3] = " ".join(track[3])

    with client.connect("ignite", 10800):
        client.sql("DROP TABLE IF EXISTS tracks")
        create_table()

        for track in tracks:
            try:
                client.sql(TRACK_INSERT, query_args=track)
            except Exception as e:
                print(track)
                print(e)
                exit(1)


if __name__ == "__main__":
    try:
        db_connection, cursor = db.init_connection()
        client = Client()
        main()
        db.close_connection(db_connection, cursor)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
