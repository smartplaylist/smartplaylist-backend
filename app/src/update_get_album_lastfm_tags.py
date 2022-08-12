"""Reads Last.fm tags for given album
and saves it to `lastfm_tags` and `lastfm_tags_string` columns.
Can be run for all albums or albums with NULL in `lastfm_tags`
"""
import os
import sys
from datetime import datetime, timezone

import pylast

import imports.db as db
from imports.logging import get_logger
from imports.lastfm import get_lastfm_network
from imports.tools import progress_bar
import imports.requests

log = get_logger(os.path.basename(__file__))


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
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    tags = [s.item.get_name().lower() for s in tags]
    return tags


def save_lastfm_album_tags(spotify_id, tags, cursor):
    try:
        cursor.execute(
            "UPDATE albums SET lastfm_tags=%s, lastfm_tags_string=%s WHERE spotify_id=%s;",
            (tags, " ".join(tags), spotify_id),
        )
    except Exception as e:
        log.exception("Unhandled exception", exception=e, exc_info=True)
    else:
        log.info(
            "💿 Added Last.fm tags to album",
            spotify_id=spotify_id,
            tags=" ".join(tags),
            object="album",
        )


def main():
    db_connection, cursor = db.init_connection()
    lastfm = get_lastfm_network(cache_file=".cache-lastfm-api-albums")
    # TODO: https://dellsystem.me/posts/psycopg2-offset-performance
    # Use server-side cursors to select partial results from db
    cursor.execute(
        "SELECT main_artist, name, spotify_id FROM albums WHERE lastfm_tags IS NULL ORDER BY created_at ASC"  # WHERE lastfm_tags IS NULL
    )
    items = cursor.fetchall()
    total = len(items)

    i = 0
    progress_bar(i, total)

    for item in items:
        tags = get_lastfm_album_tags(item[0], item[1], lastfm)
        if tags:
            save_lastfm_album_tags(item[2], tags, cursor)
        else:
            print("🚫 No match for", item[0], item[1])
        i += 1
        progress_bar(i, total)

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
