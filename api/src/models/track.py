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

    def count(self):
        with db_sessionmaker() as session:
            return session.query(Track).count()

    def get_updated_at_max(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(updated_at) as min, max(updated_at) as max FROM tracks"
            )
            result = session.execute(statement).fetchone()
            return result

    def get_created_at_max(self):
        with db_sessionmaker() as session:
            statement = text(
                "SELECT min(created_at) as min, max(created_at) as max FROM tracks"
            )
            result = session.execute(statement).fetchone()
            return result

    def count_with_audiofeatures(self):
        with db_sessionmaker() as session:
            return (
                session.query(Track.spotify_id)
                .filter(Track.energy != None)
                .with_entities(func.count())
                .scalar()
            )

    def search(
        self,
        name,
        genres,
        tempo,
        popularity,
        main_artist_popularity,
        main_artist_followers,
        danceability,
        energy,
        speechiness,
        acousticness,
        instrumentalness,
        liveness,
        valence,
        release,
        key,
    ):
        with db_sessionmaker() as session:
            result = (
                session.query(Track)
                .filter(
                    Track.name_fts_string.like(f"%{name.lower()}%")
                    | Track.all_artists_string.like(f"%{name.lower()}%")
                )
                .filter(Track.genres_string.like(f"%{genres.lower()}%"))
                .filter(Track.tempo >= tempo[0])
                .filter(Track.tempo <= tempo[1])
                .filter(Track.popularity >= popularity[0])
                .filter(Track.popularity <= popularity[1])
                .filter(Track.main_artist_popularity >= main_artist_popularity[0])
                .filter(Track.main_artist_popularity <= main_artist_popularity[1])
                .filter(Track.main_artist_followers >= main_artist_followers[0])
                .filter(Track.main_artist_followers <= main_artist_followers[1])
                .filter(Track.danceability >= danceability[0])
                .filter(Track.danceability <= danceability[1])
                .filter(Track.energy >= energy[0])
                .filter(Track.energy <= energy[1])
                .filter(Track.speechiness >= speechiness[0])
                .filter(Track.speechiness <= speechiness[1])
                .filter(Track.acousticness >= acousticness[0])
                .filter(Track.acousticness <= acousticness[1])
                .filter(Track.instrumentalness >= instrumentalness[0])
                .filter(Track.instrumentalness <= instrumentalness[1])
                .filter(Track.liveness >= liveness[0])
                .filter(Track.liveness <= liveness[1])
                .filter(Track.valence >= valence[0])
                .filter(Track.valence <= valence[1])
                .filter(Track.release_date >= release[0])
                .filter(Track.key >= key[0])
                .filter(Track.key <= key[1])
                .order_by(Track.release_date.desc())
                .order_by(Track.popularity.desc())
                .order_by(Track.spotify_id.asc())
                .limit(100)
                .all()
            )
            return result
