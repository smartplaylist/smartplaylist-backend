from datetime import datetime

import spotipy


def save_playlist(accessToken, ids, name=""):
    if "" == name:
        today = datetime.now()
        name = f'🎧 smartplaylist {today.strftime("%Y-%m-%d %H:%M:%S")}'

    sp = spotipy.Spotify(auth=accessToken)
    user = sp.me()

    playlist = sp.user_playlist_create(user=user["id"], name=name)

    for i in range(0, len(ids), 100):
        result = sp.user_playlist_add_tracks(
            user=user["id"],
            playlist_id=playlist["id"],
            tracks=ids[i : i + 100],
        )

    return result
