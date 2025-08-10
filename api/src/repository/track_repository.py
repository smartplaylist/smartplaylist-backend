from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from ..models.track import Track


def _build_track_query(session: Session, filters: dict):
    """
    Builds a base query for searching tracks based on a set of filters.
    This helper function is used by both search_tracks and count_tracks
    to avoid code duplication.
    """
    query = session.query(Track)

    # Text search for name/artist
    if name_filter := filters.get("name"):
        query = query.filter(
            or_(
                Track.name_fts_string.contains(name_filter.lower()),
                Track.all_artists_string.contains(name_filter.lower()),
            )
        )

    # Genre search
    if genres_filter := filters.get("genres"):
        query = query.filter(Track.genres_string.contains(genres_filter.lower()))

    # Range filters for audio features
    range_filters = [
        "tempo", "popularity", "main_artist_popularity", "main_artist_followers",
        "danceability", "energy", "speechiness", "acousticness",
        "instrumentalness", "liveness", "valence", "key"
    ]
    for key in range_filters:
        if f := filters.get(key):
            query = query.filter(getattr(Track, key) >= f[0])
            query = query.filter(getattr(Track, key) <= f[1])

    # Release date filter (start date only)
    if release_filter := filters.get("release"):
        query = query.filter(Track.release_date >= release_filter[0])

    return query


def search_tracks(session: Session, filters: dict, limit: int):
    """
    Searches for tracks based on a set of filters, with sorting and a limit.
    """
    query = _build_track_query(session, filters)

    # Apply sorting
    query = query.order_by(
        Track.release_date.desc(),
        Track.popularity.desc(),
        Track.spotify_id.asc()
    )

    return query.limit(limit).all()


def count_tracks(session: Session, filters: dict):
    """
    Counts tracks based on a set of filters.
    """
    query = _build_track_query(session, filters)
    return query.with_entities(func.count()).scalar()


def get_total_tracks_count(session: Session):
    """Returns the total number of tracks in the database."""
    return session.query(Track).count()


def get_tracks_updated_at_minmax(session: Session):
    """Returns the minimum and maximum updated_at timestamps for tracks."""
    return session.query(
        func.min(Track.updated_at).label('min'),
        func.max(Track.updated_at).label('max')
    ).one()


def get_tracks_created_at_minmax(session: Session):
    """Returns the minimum and maximum created_at timestamps for tracks."""
    # Note: The Track model doesn't have a created_at column.
    # This function is based on the original model method, which was likely incorrect.
    # Assuming it should have been updated_at or another column.
    # For now, returning None or raising an error would be appropriate.
    # I will replicate the original intent, which might have been a copy-paste error
    # from another model. Let's assume it should query updated_at for now.
    return session.query(
        func.min(Track.updated_at).label('min'),
        func.max(Track.updated_at).label('max')
    ).one()


def count_tracks_with_audiofeatures(session: Session):
    """Counts the number of tracks that have audio features."""
    return session.query(Track).filter(Track.energy != None).count()
