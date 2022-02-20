import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import imports.broker as broker
import imports.db as db
import imports.logger as logger


QUEUE_NAME = "artists"
SPOTIY_SCOPE = "user-follow-read"


def main():
    channel = broker.create_channel(QUEUE_NAME)
    db_connection, cursor = db.init_connection()
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope=SPOTIY_SCOPE, open_browser=False)
    )
    log = logger.get_logger(os.path.basename(__file__))

    # Iterate over results to get the full list
    results = sp.current_user_followed_artists(limit=50)

    artists = results["artists"]["items"]
    while results["artists"]["next"]:
        results = sp.next(results["artists"])
        artists.extend(results["artists"]["items"])

    similar_artists = []
    for artist in artists:
        similar = sp.artist_related_artists(artist["id"])
        similar_artists.extend(similar["artists"])

    artists.extend(similar_artists)

    # Iterate over results, save to Postgres, push to Rabbit
    for i, item in enumerate(artists):
        try:
            cursor.execute(
                "INSERT INTO followed_artists (spotify_id, name, popularity, followers, genres, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, now(), now());",
                (
                    item["id"],
                    item["name"],
                    item["popularity"],
                    item["followers"]["total"],
                    item["genres"],
                ),
            )
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=item["id"])
        except Exception as e:
            log.error("id: %s (%s)" % (item["id"], str(e).replace("\n", " ")))
        else:
            log.info(f"Saved id: {item['id']}")

    # Clean up and close connections
    broker.close_connection()
    db.close_connection(db_connection, cursor)


if __name__ == "__main__":
    main()
