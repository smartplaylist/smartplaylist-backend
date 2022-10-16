from typing import Union

from lib.server import app
from lib.models import Track


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/init")
def read_init():
    track = Track()
    return {
        "total_tracks": track.count(),
        "tracks_with_audiofeature": track.count_with_audiofeatures(),
    }


@app.get("/search")
def search():
    return Track().search(name="Soul", genres_string="", key=1)


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
