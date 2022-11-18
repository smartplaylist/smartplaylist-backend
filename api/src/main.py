from typing import Union

from fastapi import Request
from lib.server import app
from models.stats import Stats
from models.track import Track
import playlist


def timestamp_to_string(timestamp):
    # return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


@app.get("/tracks")
async def tracks(
    tem="0,100",
    pop="0,100",
    map="0,100",
    maf="0,100",
    dan="0,100",
    ene="0,100",
    spe="0,100",
    aco="0,100",
    ins="0,100",
    liv="0,100",
    val="0,100",
    rel="0,100",
    key="0,100",
    limit=250,
    order="rel,desc",
    gen="",
    nam="",
):
    key = key.split(",")

    if key[0] == "any":
        key[0] = 0
    if key[1] == "any":
        key[1] = 12

    return Track().search(
        name=nam.strip(","),
        genres=gen.strip(","),
        tempo=tem.split(","),
        popularity=pop.split(","),
        main_artist_followers=maf.split(","),
        main_artist_popularity=map.split(","),
        danceability=dan.split(","),
        energy=ene.split(","),
        speechiness=spe.split(","),
        acousticness=aco.split(","),
        instrumentalness=ins.split(","),
        liveness=liv.split(","),
        valence=val.split(","),
        release=rel.split(","),
        key=key,
    )


@app.post("/user/save_playlist")
async def user_save_playlist(request: Request):
    request_params = await request.json()
    result = playlist.save_playlist(
        request_params["accessToken"], request_params["ids"]
    )
    return {"saved": True, **result}


@app.get("/init")
def read_init():
    stats = Stats()
    result = stats.get_stats()

    return {
        "tracks": result[0],
        "albums": result[1],
        "artists": result[2],
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
        # 18 and 19 is updated_at and created_at
        "tracks_added": result[20],
        "albums_added": result[21],
        "artists_added": result[22],
        "tracks_with_audiofeatures_added": result[23],
        "albums_oldest_release_date": timestamp_to_string(result[24]),
        "albums_newest_release_date": timestamp_to_string(result[25]),
        "tracks_oldest_release_date": timestamp_to_string(result[26]),
        "tracks_newest_release_date": timestamp_to_string(result[27]),
        "artists_with_null_lastfm_tags": result[28],
        "albums_with_null_lastfm_tags": result[29],
        "tracks_with_null_lastfm_tags": result[30],
        "artists_lastfm_tags_added": result[31],
        "albums_lastfm_tags_added": result[32],
        "tracks_lastfm_tags_added": result[33],
    }
