import os

from lib.engine import get_sessionmaker
from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Column,
    Date,
    Integer,
    SmallInteger,
    Text,
    func,
    select,
    text,
)
from sqlalchemy.orm import declarative_base

db_sessionmaker = get_sessionmaker()
Base = declarative_base()


class Album(Base):
    __tablename__ = "albums"
    spotify_id = Column(Text, primary_key=True)
    name = Column(Text)
    main_artist = Column(Text)
    all_artists = ARRAY(Text)
    from_discography_of = Column(Text)
    release_date = Column(Date)
    total_tracks = Column(SmallInteger)
    popularity = Column(SmallInteger)
    label = Column(Text)
    copyrights = ARRAY(Text)
    album_group = Column(Text)
    album_type = Column(Text)
    main_artist_spotify_id = Column(Text)
    from_discography_of_spotify_id = Column(Text)
    release_date_precision = Column(Text)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    lastfm_tags = ARRAY(Text)
    lastfm_tags_string = Column(Text)

    def count(self):
        with db_sessionmaker() as session:
            return session.query(Album).count()

    def get_updated_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(updated_at) as min, max(updated_at) as max FROM albums"
            )
            result = session.execute(statement).fetchone()
            return result

    def get_created_at_minmax(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(created_at) as min, max(created_at) as max FROM albums"
            )
            result = session.execute(statement).fetchone()
            return result
