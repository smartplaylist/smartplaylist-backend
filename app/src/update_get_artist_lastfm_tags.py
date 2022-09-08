"""Reads Last.fm tags for given artist name
and saves it to `lastfm_tags` and `lastfm_tags_string` columns.
Can be run for all artists or artists with NULL in `lastfm_tags`
"""
import os
import sys
from datetime import datetime, timezone

import pylast

import imports.db as db
from imports.logging import get_logger
from imports.lastfm import get_lastfm_network
import imports.requests

LASTFM_API_CACHE_FILENAME = ".cache-lastfm-api-artists"

log = get_logger(os.path.basename(__file__))


def get_lastfm_artist_tags(artist, lastfm):
    """Get tags for an artist from Last.fm API

    Returns
    -------
    a list of lowercased tags
    """
    tags = []
    lastfrm_artist = pylast.Artist(artist, lastfm)
    try:
        tags = lastfrm_artist.get_top_tags(limit=10)
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
        # '6', 'The artist you supplied could not be found'
        # For "Michelle Lynn Piland"
    tags = [s.item.get_name().lower() for s in tags]
    return tags


def save_lastfm_artist_tags(artist_id, tags, cursor):
    try:
        cursor.execute(
            "UPDATE artists SET lastfm_tags=%s, lastfm_tags_string=%s WHERE spotify_id=%s;",
            (tags, " ".join(tags), artist_id),
        )
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info(
            "👨🏽‍🎤 Added Last.fm tags to artist",
            spotify_id=artist_id,
            tags=" ".join(tags),
            object="artist",
        )


def main():
    db_connection, cursor = db.init_connection()
    lastfm = get_lastfm_network(cache_file=LASTFM_API_CACHE_FILENAME)
    cursor.execute(
        "SELECT name, spotify_id FROM artists WHERE lastfm_tags IS NULL ORDER BY created_at ASC"
    )
    artists = cursor.fetchall()

    for artist in artists:
        tags = get_lastfm_artist_tags(artist[0], lastfm)
        save_lastfm_artist_tags(artist[1], tags, cursor)
        if not tags:
            log.info(
                "👨🏽‍🎤 No Last.fm tags for artist",
                spotify_id=artist[1],
                artist=artist[0],
                object="artist",
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
