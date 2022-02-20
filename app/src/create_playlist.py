import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import imports.db as db
import imports.logger as logger

username = ""
scope = "playlist-modify-public"


def main():
    db_connection, cursor = db.init_connection()
    # token = SpotifyOAuth(scope=scope, show_dialog=True, username=username)
    sp = spotipy.Spotify(auth_manager=SpotifyPKCE(open_browser=True))

    log = logger.get_logger(os.path.basename(__file__))

    cursor.execute(
        "SELECT spotify_id FROM tracks WHERE release_date>='2022' AND popularity>50 ORDER BY release_date DESC"
    )

    results = cursor.fetchall()
    print(len(results))

    result = sp.user_playlist_create(user=username, name="testsss")
    log.info("Created playlist", result)
    print(result)

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
