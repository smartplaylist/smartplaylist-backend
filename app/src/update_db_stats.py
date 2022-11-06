import os
import sys

from imports.logging import get_logger
import imports.db as db

log = get_logger(os.path.basename(__file__))
db_connection, cursor = db.init_connection()


def get_track_count():
    cursor.execute("SELECT count(*) as tracks_count FROM tracks")
    return cursor.fetchone()


def get_tracks_updated_at_minmax():
    cursor.execute("SELECT min(updated_at) as min, max(updated_at) as max FROM tracks")
    return cursor.fetchone()


def get_tracks_created_at_minmax():
    cursor.execute("SELECT min(created_at) as min, max(created_at) as max FROM tracks")
    return cursor.fetchone()


def get_tracks_with_audiofeature_count():
    cursor.execute("SELECT count(*) FROM tracks WHERE energy IS NOT NULL")
    return cursor.fetchone()


def get_album_count():
    cursor.execute("SELECT count(*) FROM albums")
    return cursor.fetchone()


def get_albums_updated_at_minmax():
    cursor.execute("SELECT min(updated_at) as min, max(updated_at) as max FROM albums")
    return cursor.fetchone()


def get_albums_created_at_minmax():
    cursor.execute("SELECT min(created_at) as min, max(created_at) as max FROM albums")
    return cursor.fetchone()


def get_artist_count():
    cursor.execute("SELECT count(*) FROM artists")
    return cursor.fetchone()


def get_artists_updated_at_minmax():
    cursor.execute("SELECT min(updated_at) as min, max(updated_at) as max FROM artists")
    return cursor.fetchone()


def get_artists_created_at_minmax():
    cursor.execute("SELECT min(created_at) as min, max(created_at) as max FROM artists")
    return cursor.fetchone()


def get_artists_album_updated_at_minmax():
    cursor.execute(
        "SELECT min(albums_updated_at) as min, max(albums_updated_at) as max FROM artists"
    )
    return cursor.fetchone()


def get_current_stats():
    cursor.execute(
        """
        SELECT
            total_tracks,
            total_albums,
            total_artists,
            tracks_with_audiofeature,
            artists_with_null_lastfm_tags,
            albums_with_null_lastfm_tags,
            tracks_with_null_lastfm_tags
        FROM db_stats
        ORDER BY created_at DESC
        LIMIT 1
        """
    )
    return cursor.fetchone()


def get_album_release_date_minmax():
    cursor.execute("SELECT min(release_date), max(release_date) FROM albums")
    return cursor.fetchone()


def get_track_release_date_minmax():
    cursor.execute("SELECT min(release_date), max(release_date) FROM tracks")
    return cursor.fetchone()


def get_artists_with_null_lastfm_tags():
    cursor.execute(
        """SELECT count(spotify_id) FROM artists WHERE lastfm_tags IS NULL"""
    )
    return cursor.fetchone()


def get_albums_with_null_lastfm_tags():
    cursor.execute("""SELECT count(spotify_id) FROM albums WHERE lastfm_tags IS NULL""")
    return cursor.fetchone()


def get_tracks_with_null_lastfm_tags():
    cursor.execute("""SELECT count(spotify_id) FROM tracks WHERE lastfm_tags IS NULL""")
    return cursor.fetchone()


def main():
    current_stats = get_current_stats()

    # First run only for an empty stats database, populates 7 fields
    if current_stats == None:
        current_stats = [0] * 7

    track_count = get_track_count()

    tracks_with_audiofeature_count = get_tracks_with_audiofeature_count()
    tracks_updated_at_minmax = get_tracks_updated_at_minmax()
    tracks_created_at_minmax = get_tracks_created_at_minmax()

    album_count = get_album_count()
    albums_updated_at_minmax = get_albums_updated_at_minmax()
    albums_created_at_minmax = get_albums_created_at_minmax()

    artist_count = get_artist_count()
    artists_updated_at_minmax = get_artists_updated_at_minmax()
    artists_created_at_minmax = get_artists_created_at_minmax()
    artists_album_updated_at_minmax = get_artists_album_updated_at_minmax()

    album_release_date_minmax = get_album_release_date_minmax()
    track_release_date_minmax = get_track_release_date_minmax()

    artists_with_null_lastfm_tags = get_artists_with_null_lastfm_tags()
    albums_with_null_lastfm_tags = get_albums_with_null_lastfm_tags()
    tracks_with_null_lastfm_tags = get_tracks_with_null_lastfm_tags()

    try:
        cursor.execute(
            """
            INSERT INTO db_stats (
            total_tracks, total_albums, total_artists, tracks_with_audiofeature,
            track_min_updated_at, track_max_updated_at,
            track_min_created_at, track_max_created_at,
            album_min_updated_at, album_max_updated_at,
            album_min_created_at, album_max_created_at,
            artist_min_updated_at, artist_max_updated_at,
            artist_min_created_at, artist_max_created_at,
            artist_albums_updated_at_min, artist_albums_updated_at_max,
            tracks_added, albums_added, artists_added, tracks_with_audiofeatures_added,
            albums_oldest_release_date, albums_newest_release_date,
            tracks_oldest_release_date, tracks_newest_release_date,
            artists_with_null_lastfm_tags, albums_with_null_lastfm_tags, tracks_with_null_lastfm_tags,
            artists_lastfm_tags_added, albums_lastfm_tags_added, tracks_lastfm_tags_added
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s);
            """,
            (
                track_count[0],
                album_count[0],
                artist_count[0],
                tracks_with_audiofeature_count[0],
                tracks_updated_at_minmax[0],
                tracks_updated_at_minmax[1],
                tracks_created_at_minmax[0],
                tracks_created_at_minmax[1],
                albums_updated_at_minmax[0],
                albums_updated_at_minmax[1],
                albums_created_at_minmax[0],
                albums_created_at_minmax[1],
                artists_updated_at_minmax[0],
                artists_updated_at_minmax[1],
                artists_created_at_minmax[0],
                artists_created_at_minmax[1],
                artists_album_updated_at_minmax[0],
                artists_album_updated_at_minmax[1],
                (track_count[0] - current_stats[0]),
                (album_count[0] - current_stats[1]),
                (artist_count[0] - current_stats[2]),
                (tracks_with_audiofeature_count[0] - current_stats[3]),
                album_release_date_minmax[0],
                album_release_date_minmax[1],
                track_release_date_minmax[0],
                track_release_date_minmax[1],
                artists_with_null_lastfm_tags,
                albums_with_null_lastfm_tags,
                tracks_with_null_lastfm_tags,
                (current_stats[4] - artists_with_null_lastfm_tags[0]),
                (current_stats[5] - albums_with_null_lastfm_tags[0]),
                (current_stats[6] - tracks_with_null_lastfm_tags[0]),
            ),
        )

    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info(
            "📈 Saved stats",
        )

    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ## If file exists, delete it ##
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
