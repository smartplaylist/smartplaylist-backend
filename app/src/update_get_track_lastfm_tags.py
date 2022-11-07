"""Reads Last.fm tags for given track
and saves it to `lastfm_tags` and `lastfm_tags_string` columns.
Can be run for all tracks or tracks with NULL in `lastfm_tags`
"""
import os
from pprint import pprint
import sys

from imports.lastfm import get_lastfm_network
from imports.logging import get_logger
import imports.db as db
import pylast

LASTFM_DAILY_TRACKS_UPDATE = os.getenv("LASTFM_DAILY_TRACKS_UPDATE", 100_000)
LASTFM_API_CACHE_FILENAME = ".cache-lastfm-api-tracks"
STATUS_INVALID_PARAMS = "6"  # as pylast.STATUS_INVALID_PARAMS

log = get_logger(os.path.basename(__file__))


def get_lastfm_track_tags(artist, name, lastfm):
    """Get tags for a track from Last.fm API

    Returns
    -------
    a list of lowercased tags
    """
    tags = []
    lastfm_track = pylast.Track(artist, name, lastfm)
    try:
        tags = lastfm_track.get_top_tags()
    except pylast.WSError as e:
        if STATUS_INVALID_PARAMS == e.status:
            log.info("💿 Track not found on Last.fm", track=artist + " - " + name)
        else:
            log.exception("Pylast WSError exception", exception=e, exc_info=True)
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)

    tags = [s.item.get_name().lower() for s in tags]
    return tags


def save_lastfm_track_tags(spotify_id, tags, cursor):
    try:
        cursor.execute(
            "UPDATE tracks SET lastfm_tags=%s, lastfm_tags_string=%s WHERE spotify_id=%s;",
            (tags, " ".join(tags), spotify_id),
        )
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info("💿 Added Last.fm tags to track", id=spotify_id, tags=" ".join(tags))


def main():
    db_connection, cursor = db.init_connection()
    lastfm = get_lastfm_network(cache_file=LASTFM_API_CACHE_FILENAME)

    cursor.execute(
        f"""
        SELECT main_artist, name, spotify_id
        FROM tracks
        WHERE lastfm_tags IS NULL
        ORDER BY created_at ASC
        LIMIT {LASTFM_DAILY_TRACKS_UPDATE}
        """
    )
    items = cursor.fetchall()

    for item in items:
        tags = get_lastfm_track_tags(item[0], item[1], lastfm)
        save_lastfm_track_tags(item[2], tags, cursor)
        if not tags:
            log.info(
                "🔉 No Last.fm tags for track",
                id=item[2],
                artist=item[0] + " - " + item[1],
            )

    # Clean up and close connections
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
