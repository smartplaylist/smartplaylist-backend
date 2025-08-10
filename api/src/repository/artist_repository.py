from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models.artist import Artist


def get_total_artists_count(session: Session):
    """Returns the total number of artists in the database."""
    return session.query(Artist).count()


def get_artists_updated_at_minmax(session: Session):
    """Returns the minimum and maximum updated_at timestamps for artists."""
    return session.query(
        func.min(Artist.updated_at).label('min'),
        func.max(Artist.updated_at).label('max')
    ).one()


def get_artists_created_at_minmax(session: Session):
    """Returns the minimum and maximum created_at timestamps for artists."""
    return session.query(
        func.min(Artist.created_at).label('min'),
        func.max(Artist.created_at).label('max')
    ).one()


def get_artists_albums_updated_at_minmax(session: Session):
    """Returns the minimum and maximum albums_updated_at timestamps for artists."""
    return session.query(
        func.min(Artist.albums_updated_at).label('min'),
        func.max(Artist.albums_updated_at).label('max')
    ).one()
