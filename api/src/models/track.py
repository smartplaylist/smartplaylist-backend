import logging

from lib.engine import get_sessionmaker
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import func
from sqlalchemy import Integer
from sqlalchemy import orm
from sqlalchemy import SmallInteger
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy import TIMESTAMP

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

db_sessionmaker = get_sessionmaker()
Base = orm.declarative_base()


# spotify_id,
# all_artists,
# name,
# genres,
# release_date,
# tempo,
# popularity,
# danceability,
# energy,
# speechiness,
# acousticness,
# instrumentalness,
# liveness,
# valence,
# main_artist_popularity,
# main_artist_followers,
# key,
# preview_url


class Track(Base):
    __tablename__ = "tracks"
    name_fts_string = Column(Text)

    spotify_id = Column(Text, primary_key=True)
    all_artists_string = Column(Text)
    all_artists = Column(Text)
    name = Column(Text)
    genres_string = Column(Text)
    genres = Column(Text)
    release_date = Column(Date)
    tempo = Column(SmallInteger)
    popularity = Column(SmallInteger)
    danceability = Column(SmallInteger)
    energy = Column(SmallInteger)
    speechiness = Column(SmallInteger)
    acousticness = Column(SmallInteger)
    instrumentalness = Column(SmallInteger)
    liveness = Column(SmallInteger)
    valence = Column(SmallInteger)
    main_artist_popularity = Column(SmallInteger)
    main_artist_followers = Column(Integer)
    key = Column(SmallInteger)
    preview_url = Column(Text)

    updated_at = Column(TIMESTAMP)
