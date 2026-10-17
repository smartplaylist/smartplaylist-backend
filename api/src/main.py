from typing import Union

from fastapi import HTTPException
from fastapi import Response
from lib.server import app
from models.requests import SavePlaylistRequest
from models.requests import TrackSearchParams
from models.stats import Stats
from models.track import Track
import playlist

DEFAULT_TRACK_LIST_LENGTH = 250


def timestamp_to_string(timestamp):
    # return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


@app.get("/tracks/count")
async def tracks_count(
    response: Response,
    tem: str = "0,100",
    pop: str = "0,100",
    map: str = "0,100",
    maf: str = "0,100",
    dan: str = "0,100",
    ene: str = "0,100",
    spe: str = "0,100",
    aco: str = "0,100",
    ins: str = "0,100",
    liv: str = "0,100",
    val: str = "0,100",
    rel: str = "",
    key: str = "0,12",
    gen: str = "",
    nam: str = "",
):
    try:
        params = TrackSearchParams.from_query_params(
            tem=tem, pop=pop, map=map, maf=maf, dan=dan, ene=ene,
            spe=spe, aco=aco, ins=ins, liv=liv, val=val, rel=rel,
            key=key, gen=gen, nam=nam,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return Track().count(**params.filters())


@app.get("/tracks")
async def tracks(
    response: Response,
    tem: str = "0,100",
    pop: str = "0,100",
    map: str = "0,100",
    maf: str = "0,100",
    dan: str = "0,100",
    ene: str = "0,100",
    spe: str = "0,100",
    aco: str = "0,100",
    ins: str = "0,100",
    liv: str = "0,100",
    val: str = "0,100",
    rel: str = "",
    key: str = "0,12",
    order: str = "rel,desc",
    gen: str = "",
    nam: str = "",
    limit: int = DEFAULT_TRACK_LIST_LENGTH,
):
    try:
        params = TrackSearchParams.from_query_params(
            tem=tem, pop=pop, map=map, maf=maf, dan=dan, ene=ene,
            spe=spe, aco=aco, ins=ins, liv=liv, val=val, rel=rel,
            key=key, gen=gen, nam=nam, limit=limit, order=order,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return Track().search(**params.filters(), limit=params.limit)


@app.post("/user/save_playlist")
async def user_save_playlist(request_data: SavePlaylistRequest):
    try:
        result = playlist.save_playlist(
            request_data.access_token,
            request_data.track_ids,
            request_data.playlist_name or "",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save playlist: {e}") from e
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
