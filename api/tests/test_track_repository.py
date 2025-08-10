import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.src.models.track import Base, Track
from api.src.repository import track_repository

@pytest.fixture(scope="module")
def session():
    """
    Fixture to set up a test database session.
    Uses an in-memory SQLite database for speed.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # Add some test data
    tracks_data = [
        Track(spotify_id='1', name='Track A', all_artists_string='Artist X', name_fts_string='track a artist x', genres_string='pop rock', popularity=80, tempo=120, release_date='2022-01-01', energy=70, danceability=60, key=1, main_artist_popularity=90, main_artist_followers=1000),
        Track(spotify_id='2', name='Track B', all_artists_string='Artist Y', name_fts_string='track b artist y', genres_string='rock indie', popularity=70, tempo=140, release_date='2021-01-01', energy=80, danceability=50, key=2, main_artist_popularity=80, main_artist_followers=2000),
        Track(spotify_id='3', name='Another Song', all_artists_string='Artist X', name_fts_string='another song artist x', genres_string='pop electronic', popularity=90, tempo=120, release_date='2023-01-01', energy=90, danceability=70, key=3, main_artist_popularity=90, main_artist_followers=1000),
    ]
    db_session.add_all(tracks_data)
    db_session.commit()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(engine)

def test_count_tracks_no_filters(session):
    """
    Test counting tracks with no filters.
    """
    count = track_repository.count_tracks(session, {})
    assert count == 3

def test_count_tracks_with_name_filter(session):
    """
    Test counting tracks with a name filter.
    """
    filters = {"name": "Track"}
    count = track_repository.count_tracks(session, filters)
    assert count == 2

def test_search_tracks_with_name_filter(session):
    """
    Test searching for tracks with a name filter.
    """
    filters = {"name": "Track"}
    results = track_repository.search_tracks(session, filters, limit=10)
    assert len(results) == 2
    assert results[0].name == 'Track A' # Sorted by release date desc
    assert results[1].name == 'Track B'

def test_search_tracks_with_artist_filter(session):
    """
    Test searching for tracks by artist name.
    """
    filters = {"name": "Artist X"}
    results = track_repository.search_tracks(session, filters, limit=10)
    assert len(results) == 2
    assert results[0].name == 'Another Song'
    assert results[1].name == 'Track A'

def test_search_tracks_with_genre_filter(session):
    """
    Test searching for tracks with a genre filter.
    """
    filters = {"genres": "rock"}
    results = track_repository.search_tracks(session, filters, limit=10)
    assert len(results) == 2 # Both Track A and Track B have 'rock'

def test_search_tracks_with_popularity_filter(session):
    """
    Test searching for tracks with a popularity filter.
    """
    filters = {"popularity": (85, 100)}
    results = track_repository.search_tracks(session, filters, limit=10)
    assert len(results) == 1
    assert results[0].name == 'Another Song'

def test_search_tracks_with_tempo_filter(session):
    """
    Test searching for tracks with a tempo filter.
    """
    filters = {"tempo": (130, 150)}
    results = track_repository.search_tracks(session, filters, limit=10)
    assert len(results) == 1
    assert results[0].name == 'Track B'
