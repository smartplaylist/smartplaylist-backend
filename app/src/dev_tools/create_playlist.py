from datetime import date
import os
import sys

import imports.db as db
import imports.logger as logger
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPE = "playlist-modify-public"


def main():
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE, open_browser=False))
    username = sp.me()["id"]
    log = logger.get_logger(os.path.basename(__file__))

    cursor.execute(
        """
        SELECT spotify_id
        FROM tracks
        WHERE release_date>='2021-09-01'
        AND popularity>10
        AND tempo>122 AND tempo<128
        AND danceability>0.8
        AND energy>0.8
        ORDER BY release_date DESC"""
    )

    tracks = cursor.fetchall()
    tracks = ["spotify:track:%s" % spotify_id for spotify_id in tracks]

    today = date.today()
    playlist = sp.user_playlist_create(
        user=username, name="🥁 gt/%s" % today.strftime("%Y-%m-%d")
    )

    result = sp.user_playlist_add_tracks(
        user=username, playlist_id=playlist["id"], tracks=tracks
    )

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
