import json
import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import imports.broker as broker
import imports.db as db
import imports.logger as logger


CHANNEL_ALBUMS_NAME = "artists"
CHANNEL_RELATED_ARTISTS_NAME = "related_artists"
SPOTIFY_SCOPE = "user-follow-read"


def main():
    channel_albums = broker.create_channel(CHANNEL_ALBUMS_NAME)
    channel_related_artists = broker.create_channel(CHANNEL_RELATED_ARTISTS_NAME)

    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(
        auth_manager=SpotifyPKCE(scope=SPOTIFY_SCOPE, open_browser=False)
    )
    log = logger.get_logger(os.path.basename(__file__))

    results = sp.current_user_followed_artists(limit=50)
    artists = results["artists"]["items"]

    # Iterate over results to get the full list
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        artists.extend(results["artists"]["items"])

    # Iterate over results, save to Postgres, push to Rabbit
    for i, item in enumerate(artists):
        try:
            cursor.execute(
                "INSERT INTO artists (spotify_id, name, popularity, followers, genres, genres_string, total_albums) VALUES (%s, %s, %s, %s, %s, %s, 0);",
                (
                    item["id"],
                    item["name"],
                    item["popularity"],
                    item["followers"]["total"],
                    item["genres"],
                    " ".join(item["genres"]),
                ),
            )
            channel_albums.basic_publish(
                exchange="",
                routing_key=CHANNEL_ALBUMS_NAME,
                body=json.dumps({"spotify_id": item["id"], "total_albums": 0}),
            )
            channel_related_artists.basic_publish(
                exchange="",
                routing_key=CHANNEL_RELATED_ARTISTS_NAME,
                body=json.dumps({"spotify_id": item["id"], "name": item["name"]}),
            )
        except Exception as e:
            log.error("id: %s (%s)" % (item["id"], str(e).replace("\n", " ")))
        else:
            log.info(f"Saved id: {item['id']}")

    # Clean up and close connections
    broker.close_connection()
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    main()
