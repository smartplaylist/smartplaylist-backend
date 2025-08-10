from fastapi import Depends, Request
from sqlalchemy.orm import Session

from lib.engine import get_sessionmaker
from lib.server import app
from models.filters import TrackFilterParams
from repository import artist_repository, track_repository
import playlist

DEFAULT_TRACK_LIST_LENGTH = 250

# Dependency to get a DB session
def get_session():
    session = get_sessionmaker()()
    try:
        yield session
    finally:
        session.close()


@app.get("/tracks/count")
async def tracks_count(
    filters: TrackFilterParams = Depends(),
    session: Session = Depends(get_session),
):
    """
    Counts tracks based on the provided filters.
    The filter parameters are defined in the TrackFilterParams model.
    """
    filter_dict = filters.to_dict()
    return track_repository.count_tracks(session, filter_dict)


@app.get("/tracks")
async def tracks(
    filters: TrackFilterParams = Depends(),
    limit: int = DEFAULT_TRACK_LIST_LENGTH,
    session: Session = Depends(get_session),
):
    """
    Searches for tracks based on the provided filters.
    The filter parameters are defined in the TrackFilterParams model.
    """
    filter_dict = filters.to_dict()
    return track_repository.search_tracks(session, filter_dict, limit)


@app.post("/user/save_playlist")
async def user_save_playlist(request: Request):
    """
    Saves a playlist for a user on Spotify.
    """
    request_params = await request.json()
    result = playlist.save_playlist(
        request_params["accessToken"], request_params["ids"]
    )
    return {"saved": True, **result}


@app.get("/init")
def read_init(session: Session = Depends(get_session)):
    """
    Returns initial statistics and data for the application frontend.
    """
    track_updated_at = track_repository.get_tracks_updated_at_minmax(session)
    artist_created_at = artist_repository.get_artists_created_at_minmax(session)
    artist_updated_at = artist_repository.get_artists_updated_at_minmax(session)
    artist_albums_updated_at = artist_repository.get_artists_albums_updated_at_minmax(session)

    # Note: Many stats from the original endpoint are missing because they were
    # fetched from a `stats` table that doesn't have a corresponding repository yet.
    # This would need to be added if those stats are still required.
    return {
        "stats": {
            "tracks": track_repository.get_total_tracks_count(session),
            "artists": artist_repository.get_total_artists_count(session),
            "tracks_with_audiofeature": track_repository.count_tracks_with_audiofeatures(session),
        },
        "timestamps": {
            "track_updated_at": {
                "min": track_updated_at.min,
                "max": track_updated_at.max,
            },
            "artist_created_at": {
                "min": artist_created_at.min,
                "max": artist_created_at.max,
            },
            "artist_updated_at": {
                "min": artist_updated_at.min,
                "max": artist_updated_at.max,
            },
            "artist_albums_updated_at": {
                "min": artist_albums_updated_at.min,
                "max": artist_albums_updated_at.max,
            },
        }
    }
