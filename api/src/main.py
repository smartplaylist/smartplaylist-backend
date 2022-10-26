from typing import Union

from lib.models import Track
from lib.server import app


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/init")
def read_init():
    track = Track()
    return {
        "total_tracks": track.count(),
        "tracks_with_audiofeature": track.count_with_audiofeatures(),
        "track_oldest_update": track.oldest_update(),
        "track_newest_update": track.newest_update(),
    }


@app.get("/search")
def search():
    return Track().search(name="Good", genres_string="rap", key=1)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
