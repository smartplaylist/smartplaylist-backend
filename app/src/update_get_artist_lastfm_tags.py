"""Reads Last.fm tags for given artist name
and saves it to `lastfm_tags` and `lastfm_tags_string` columns.
Can be run for all artists or artists with NULL in `lastfm_tags`
"""
import os
from pprint import pprint
import sys

from imports.custom_decorators import handle_exceptions
from imports.lastfm import get_lastfm_network
from imports.logging import get_logger
import imports.db as db
import pylast

LASTFM_DAILY_ARTISTS_UPDATE = os.getenv("LASTFM_DAILY_ARTISTS_UPDATE", 100_000)
LASTFM_API_CACHE_FILENAME = ".cache-lastfm-api-artists"
STATUS_INVALID_PARAMS = "6"  # as pylast.STATUS_INVALID_PARAMS

log = get_logger(os.path.basename(__file__))


@handle_exceptions
def get_lastfm_artist_tags(artist, lastfm):
    """Get tags for an artist from Last.fm API

    Returns
    -------
    a list of lowercased tags
    """
    tags = []
    lastfm_artist = pylast.Artist(artist + "sd", lastfm)
    try:
        tags = lastfm_artist.get_top_tags(limit=25)
    except pylast.WSError as e:
        if STATUS_INVALID_PARAMS == e.status:
            log.info("👨🏽‍🎤 Artist not found on Last.fm", artist=artist)
        else:
            log.exception("Pylast WSError exception", exception=e, exc_info=True)
        return []

    tags = [s.item.get_name().lower() for s in tags]
    return tags


@handle_exceptions
def save_lastfm_artist_tags(artist_id, tags, cursor):
    cursor.execute(
        "UPDATE artists SET lastfm_tags=%s, lastfm_tags_string=%s WHERE spotify_id=%s;",
        (tags, " ".join(tags), artist_id),
    )
    log.info("👨🏽‍🎤 Added Last.fm tags to artist", id=artist_id, tags=" ".join(tags))


def main():
    db_connection, cursor = db.init_connection()
    lastfm = get_lastfm_network(cache_file=LASTFM_API_CACHE_FILENAME)

    cursor.execute(
        f"""
        SELECT name, spotify_id
        FROM artists
        WHERE lastfm_tags_string = ''
        ORDER BY created_at ASC
        LIMIT {LASTFM_DAILY_ARTISTS_UPDATE}
        """
    )

    artists = cursor.fetchall()

    for artist in artists:
        tags = get_lastfm_artist_tags(artist[0], lastfm)
        save_lastfm_artist_tags(artist[1], tags, cursor)
        if not tags:
            log.info("👨🏽‍🎤 No Last.fm tags for artist", id=artist[1])

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
