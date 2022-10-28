from typing import Union

from lib.server import app
from models.album import Album
from models.artist import Artist
from models.stats import Stats
from models.track import Track


def timestamp_to_string(timestamp):
    # return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/init")
def read_init():
    stats = Stats()
    result = stats.get_stats()

    return {
        "total_tracks": result[0],
        "total_albums": result[1],
        "total_artists": result[2],
        "tracks_with_audiofeature": result[3],
        "track_min_updated_at": timestamp_to_string(result[4]),
        "track_max_updated_at": timestamp_to_string(result[5]),
        "track_min_created_at": timestamp_to_string(result[6]),
        "track_max_created_at": timestamp_to_string(result[7]),
        "album_min_updated_at": timestamp_to_string(result[8]),
        "album_max_updated_at": timestamp_to_string(result[9]),
        "album_min_created_at": timestamp_to_string(result[10]),
        "album_max_created_at": timestamp_to_string(result[11]),
        "artist_min_updated_at": timestamp_to_string(result[12]),
        "artist_max_updated_at": timestamp_to_string(result[13]),
        "artist_min_created_at": timestamp_to_string(result[14]),
        "artist_max_created_at": timestamp_to_string(result[15]),
        "artist_albums_updated_at_min": timestamp_to_string(result[16]),
        "artist_albums_updated_at_max": timestamp_to_string(result[17]),
    }


@app.get("/search")
def search():
    return Track().search(name="Good", genres_string="rap", key=1)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
