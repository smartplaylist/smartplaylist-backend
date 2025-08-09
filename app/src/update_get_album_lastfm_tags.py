"""Reads Last.fm tags for given album
and saves it to `lastfm_tags` and `lastfm_tags_string` columns.
Can be run for all albums or albums with NULL in `lastfm_tags`
"""
import os
import sys

from imports.custom_decorators import handle_exceptions
from imports.lastfm import get_lastfm_network
from imports.logging import get_logger
import imports.db as db
import pylast

LASTFM_DAILY_ALBUMS_UPDATE = os.getenv("LASTFM_DAILY_ALBUMS_UPDATE", 100_000)
LASTFM_API_CACHE_FILENAME = ".cache-lastfm-api-albums"
STATUS_INVALID_PARAMS = "6"  # as pylast.STATUS_INVALID_PARAMS

log = get_logger(os.path.basename(__file__))


@handle_exceptions
def get_lastfm_album_tags(artist, album, lastfm):
    """Get tags for an album from Last.fm API

    Returns
    -------
    a list of lowercased tags
    """
    tags = []
    lastfm_album = pylast.Album(artist, album, lastfm)
    try:
        tags = lastfm_album.get_top_tags()
    except pylast.WSError as e:
        if STATUS_INVALID_PARAMS == e.status:
            log.info("Album not found on Last.fm", album=artist + " - " + album)
        else:
            log.exception("Pylast WSError exception", exception=e, exc_info=True)
        return []

    tags = [s.item.get_name().lower() for s in tags]
    return tags


@handle_exceptions
def save_lastfm_album_tags(spotify_id, tags, cursor):
    cursor.execute(
        "UPDATE albums SET lastfm_tags=%s, lastfm_tags_string=%s WHERE spotify_id=%s;",
        (tags, " ".join(tags), spotify_id),
    )
    log.info("💿 Added Last.fm tags to album", id=spotify_id, tags=" ".join(tags))


def main():
    db_connection, cursor = db.init_connection()
    lastfm = get_lastfm_network(cache_file=LASTFM_API_CACHE_FILENAME)
    # TODO: https://dellsystem.me/posts/psycopg2-offset-performance
    # Use server-side cursors to select partial results from db
    cursor.execute(
        f"""
        SELECT main_artist, name, spotify_id
        FROM albums
        WHERE lastfm_tags IS NULL
        ORDER BY created_at ASC
        LIMIT {LASTFM_DAILY_ALBUMS_UPDATE}
        """
    )

    items = cursor.fetchall()

    for item in items:
        tags = get_lastfm_album_tags(item[0], item[1], lastfm)
        save_lastfm_album_tags(item[2], tags, cursor)
        if not tags:
            log.info("💿 No Last.fm tags for album", id=item[2])

    # Clean up and close connections
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    # Not using a decorator here because it's a control-flow exception
    try:
        print("Getting albums tags from Last.fm")
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
